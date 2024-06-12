from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.core.exceptions import ValidationError


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Contact, UserContactRelation
from .serializers import ContactSerializer


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Contact, UserContactRelation
from .serializers import ContactSerializer


class ContactList(APIView):
    """
    ContactList View:

    - GET: Retrieve the list of all contacts.
    - POST: Add a new contact for the authenticated user, checking for existing relations.

    GET Parameters: None

    POST Parameters:
    - name (string): The name of the contact.
    - phone_number (string): The phone number of the contact.
    - email (string, optional): The optional email address of the contact.

    Returns:
    - 200 OK: If the GET operation is successful.
    - 201 Created: If a new contact is added successfully in POST.
    - 200 OK: If a contact already exists in POST, with a message indicating the existing contact.

    Example Usage:
    - GET: /api/contacts/
    - POST: /api/contacts/
      - name: John Doe
      - phone_number: +1234567890
      - email: john.doe@example.com
    """

    def get(self, request):
        """
        Retrieve the list of all contacts.

        Returns:
        - 200 OK: List of all contacts.
        """
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Add a new contact for the authenticated user, checking for existing relations.

        Returns:
        - 201 Created: If a new contact is added successfully.
        - 200 OK: If a contact already exists, with a message indicating the existing contact.
        """
        # Validate required parameters
        required_params = ["name", "phone_number"]
        if not all(key in request.data for key in required_params):
            return Response(
                {"Error": "Name and phone_number are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract optional parameter
        email = request.data.get("email", None)

        # Check if a user contact relation already exists for the given username and phone number
        username = request.data["name"]
        phone_number = request.data["phone_number"]
        existing_relation = UserContactRelation.objects.filter(
            contact__phone_number=phone_number,
            user__user__username=username,
        ).first()

        if existing_relation:
            # If relation already exists, return a response indicating that the contact already exists
            return Response(
                {"Message": "Contact already exists."},
                status=status.HTTP_200_OK,
            )
        else:
            # If relation doesn't exist, create a new contact and relation
            contact = Contact.objects.create(
                name=username,
                phone_number=phone_number,
                email=email,
            )
            UserContactRelation.objects.create(
                user=request.user.userprofile,
                contact=contact,
            )
            return Response(
                {"Message": "Contact saved successfully!!"},
                status=status.HTTP_201_CREATED,
            )


@permission_classes((AllowAny,))
class Register(APIView):
    """
    Register View:

    - POST: Register a new user with the provided name, phone number, and password.

    POST Parameters:
    - name (string): The username for the new user.
    - phone_number (string): The phone number for the new user.
    - password (string): The password for the new user.
    - email (string, optional): The optional email address for the new user.

    Returns:
    - 200 OK: If the user is registered successfully.
    - 400 Bad Request: If any required parameter is missing or if a user with the same phone number already exists.
    - 400 Bad Request: If there's an error during user creation, with details in the response.

    Example Usage:
    - POST: /api/register/
      - name: JohnDoe
      - phone_number: +1234567890
      - password: securepassword
      - email: john.doe@example.com
    """

    def post(self, request):
        """
        Register a new user with the provided name, phone number, and password.

        Returns:
        - 200 OK: If the user is registered successfully.
        - 400 Bad Request: If any required parameter is missing or if a user with the same phone number already exists.
        - 400 Bad Request: If there's an error during user creation, with details in the response.
        """
        # Validate required parameters
        required_params = ["name", "phone_number", "password"]
        if not all(key in request.data for key in required_params):
            return Response(
                {"Error": "Name, phone_number, and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract optional parameter
        email = request.data.get("email", "NONE")

        # Check if a user with the same phone number already exists
        existing_user = UserProfile.objects.filter(
            phone_number=request.data["phone_number"]
        ).first()

        if existing_user:
            return Response(
                {"Error": "User with this phone number already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the user and user profile
        try:
            user = User.objects.create_user(
                username=request.data["name"],
                password=request.data["password"],
                email=email,
            )
        except ValidationError as e:
            return Response(
                {"Error": f"Error during Signup: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_profile = UserProfile.objects.create(
            user=user,
            phone_number=request.data["phone_number"],
            email=email,
        )
        return Response(
            {"Message": "Registered successfully"}, status=status.HTTP_200_OK
        )


@permission_classes((AllowAny,))
class Login(APIView):
    """
    Login View:

    - POST: Authenticate a user with the provided username and password, returning an authentication token.

    POST Parameters:
    - username (string): The username for authentication.
    - password (string): The password for authentication.

    Returns:
    - 200 OK: If the provided credentials are valid, returning an authentication token.
    - 400 Bad Request: If any required parameter is missing.
    - 401 Unauthorized: If the provided credentials are invalid.

    Example Usage:
    - POST: /api/login/
      - username: JohnDoe
      - password: securepassword
    """

    def post(self, request):
        """
        Authenticate a user with the provided username and password, returning an authentication token.

        Returns:
        - 200 OK: If the provided credentials are valid, returning an authentication token.
        - 400 Bad Request: If any required parameter is missing.
        - 401 Unauthorized: If the provided credentials are invalid.
        """
        # Validate required parameters
        required_params = ["username", "password"]
        if not all(key in request.data for key in required_params):
            return Response(
                {"Error": "Please provide username/password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract credentials
        username = request.data["username"]
        password = request.data["password"]

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user:
            # Generate or retrieve authentication token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"Token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"Error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class MarkSpam(APIView):
    """
    Mark Spam View:

    - POST: Mark a phone number as spam for a contact or globally.

    POST Parameters:
    - phone_number (string): The phone number to mark as spam.

    Returns:
    - 200 OK: If the phone number is successfully marked as spam for a contact or globally.
    - 400 Bad Request: If the required parameter 'phone_number' is missing.
    - 200 OK: If the phone number is already marked as spam for a contact or globally.

    Example Usage:
    - POST: /api/mark-spam/
      - phone_number: +1234567890
    """

    def post(self, request):
        """
        Mark a phone number as spam for a contact or globally.

        Returns:
        - 200 OK: If the phone number is successfully marked as spam for a contact or globally.
        - 400 Bad Request: If the required parameter 'phone_number' is missing.
        - 200 OK: If the phone number is already marked as spam for a contact or globally.
        """
        # Validate required parameters
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response(
                {"Error": "Phone number required!!"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Check if the phone number is already marked as spam for a contact
            contact = Contact.objects.get(phone_number=phone_number)
            contact.spam = True
            contact.save()

            try:
                # Try to get the associated user profile
                user_profile = UserProfile.objects.get(phone_number=phone_number)
                user_profile.spam = True
                user_profile.save()
            except UserProfile.DoesNotExist:
                # Handle the case where UserProfile does not exist for the given phone number
                pass

            return Response(
                {"Message": "Contact marked as spam successfully!!"},
                status=status.HTTP_200_OK,
            )
        except Contact.DoesNotExist:
            # If the phone number is not found for a contact, mark as global spam
            global_spam, created_global_spam = GlobalSpam.objects.get_or_create(
                phone_number=phone_number
            )
            if created_global_spam:
                return Response(
                    {"Message": "Number marked as spam globally successfully!!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"Message": "Number already marked as spam globally."},
                    status=status.HTTP_200_OK,
                )


class SearchName(APIView):
    """
    Search by Name View:

    - GET: Search for people by name in the global database.
           Returns a list of results with name, phone number, and spam likelihood.

    GET Parameters:
    - name (string): The name to search for.

    Returns:
    - 200 OK: List of results with name, phone number, and spam likelihood.
    - 400 Bad Request: If the required parameter 'name' is missing.

    Example Usage:
    - GET: /api/search-name/
      - name: John
    """

    def get(self, request):
        """
        Search for people by name in the global database.

        Returns:
        - 200 OK: List of results with name, phone number, and spam likelihood.
        - 400 Bad Request: If the required parameter 'name' is missing.
        """
        # Validate required parameters
        name = request.data.get("name")
        if not name:
            return Response(
                {"Error": "Name is required!!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Query UserProfile and Contact for name matches
        UserProfile_start = UserProfile.objects.filter(user__username__startswith=name)
        UserProfile_contain = UserProfile.objects.filter(
            user__username__contains=name
        ).exclude(user__username__startswith=name)
        contact_start = Contact.objects.filter(name__startswith=name)
        contact_contain = Contact.objects.filter(name__contains=name).exclude(
            name__startswith=name
        )

        # Compile and return response
        response = []
        for contact in UserProfile_start:
            response.append(
                {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "spam": contact.spam,
                }
            )
        for contact in contact_start:
            response.append(
                {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "spam": contact.spam,
                }
            )
        for contact in UserProfile_contain:
            response.append(
                {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "spam": contact.spam,
                }
            )
        for contact in contact_contain:
            response.append(
                {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "spam": contact.spam,
                }
            )
        return Response(response, status=status.HTTP_200_OK)


class SearchPhoneNumber(APIView):
    """
    Search by Phone Number View:

    - GET: Search for a person by phone number in the global database.
           Returns details for the matching person, including spam likelihood.

    GET Parameters:
    - phone_number (string): The phone number to search for.

    Returns:
    - 200 OK: Details for the matching person, including spam likelihood.
    - 400 Bad Request: If the required parameter 'phone_number' is missing.
    - 404 Not Found: If no user or contact is found for the given phone number.

    Example Usage:
    - GET: /api/search-phone-number/
      - phone_number: +1234567890
    """

    def get(self, request):
        """
        Search for a person by phone number in the global database.

        Returns:
        - 200 OK: Details for the matching person, including spam likelihood.
        - 400 Bad Request: If the required parameter 'phone_number' is missing.
        - 404 Not Found: If no user or contact is found for the given phone number.
        """
        # Validate required parameters
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response(
                {"Error": "Phone number required!!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Query UserProfile and Contact for phone number matches
        user_profiles = UserProfile.objects.filter(phone_number=phone_number)
        contacts = Contact.objects.filter(phone_number=phone_number)

        # Return response based on search results
        if user_profiles:
            user_profile_serializer = UserProfileSerializer(user_profiles.first())
            return Response(user_profile_serializer.data)
        elif contacts:
            contact_serializer = ContactSerializer(contacts, many=True)
            return Response(contact_serializer.data)
        else:
            return Response(
                {"Message": "No user or contact found for the given phone number."},
                status=status.HTTP_404_NOT_FOUND,
            )
