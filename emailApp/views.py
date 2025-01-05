from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from django.core.validators import validate_email
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserProfileSerializer,EmailSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from core.tasks import send_email_with_delay
import time

class RegisterView(APIView):
    def post(self, request):
        data = request.data

        # Validate that required fields are present
        if 'username' not in data or 'password' not in data:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        username = data.get('username')
        password = data.get('password')
        email = data.get('email', None)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

        # Optional: Check if the email already exists
        if email:
            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already taken"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                validate_email(email)  # Validate the email format
            except ValidationError:
                return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the password with Django's built-in validators
        try:
            validate_password(password)  # This checks password strength
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        
User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the user by email
            user = User.objects.filter(email=email).first()

            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # Check the user's credentials
            user = authenticate(request, username=user.username, password=password)
            if user is None:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            for token in OutstandingToken.objects.filter(user=request.user):
                BlacklistedToken.objects.get_or_create(token=token)
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class CSVUploadView(APIView):
    authentication_classes = [JWTAuthentication]  # Ensure you're using JWT for authentication
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can upload CSVs

    def post(self, request):
        # Retrieve file from the request
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided. Please upload a file."}, status=status.HTTP_400_BAD_REQUEST)
        if not file.name.endswith('.csv'):
            return Response({"error": "Invalid file format. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)

            # Validate required fields
            required_fields = {'email', 'first_name'}
            missing_fields = required_fields - set(df.columns)
            if missing_fields:
                return Response(
                    {"error": f"CSV must contain the fields: {', '.join(required_fields)}. Missing: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate email column
            invalid_emails = []
            for email in df['email']:
                try:
                    if not isinstance(email, str):
                        raise ValidationError("Invalid type. Email must be a string.")
                    validate_email(email)
                except ValidationError:
                    invalid_emails.append(email)

            if invalid_emails:
                return Response(
                    {"error": f"Invalid emails found: {', '.join(map(str, invalid_emails))}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If all validations pass
            return Response({"message": "CSV uploaded and validated successfully."}, status=status.HTTP_200_OK)

        except pd.errors.ParserError:
            return Response({"error": "Error reading CSV file. Ensure it is properly formatted."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        

class CSVSavingView(APIView):
    authentication_classes = [JWTAuthentication]  # Ensures the view uses JWT authentication
    permission_classes = [IsAuthenticated]  # Ensure the view only allows authenticated users
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # Log the request headers to check if the Authorization token is passed
        print("Request Headers:", request.headers)

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the uploaded file from the request
        file = request.FILES.get('file')
        
        if not file or not file.name.endswith('.csv'):
            return Response({"error": "Invalid file format. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read CSV file into a DataFrame
            df = pd.read_csv(file)

            # Validate required fields
            required_fields = {'email', 'first_name', 'last_name'}
            missing_fields = required_fields - set(df.columns)
            if missing_fields:
                return Response(
                    {"error": f"CSV must contain the fields: {', '.join(required_fields)}. Missing: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate the email format
            invalid_emails = []
            for email in df['email']:
                try:
                    validate_email(email)
                except ValidationError:
                    invalid_emails.append(email)

            if invalid_emails:
                return Response(
                    {"error": f"Invalid emails found: {', '.join(map(str, invalid_emails))}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save records to the database
            for index, row in df.iterrows():
                data = {
                    'email': row['email'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'age': row['age'],
                    'city': row['city']
                }
                serializer = UserProfileSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({"error": "Error saving record."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "CSV uploaded and records saved successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error for debugging
            print("Error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

logger = logging.getLogger(__name__)

class EmailTemplateCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        # Log user and auth details for debugging
        logger.info(f"User: {request.user}, Authenticated: {request.auth is not None}")

        # Initialize the serializer with request data and context
        serializer = EmailSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                # Save the serializer and associate it with the authenticated user
                template = serializer.save(user=request.user)
                logger.info(f"Email template created successfully with ID: {template.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                # Log and return a server error response in case of an exception
                logger.error(f"Error creating email template: {e}", exc_info=True)
                return Response(
                    {"detail": "An error occurred while saving the email template."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Log validation errors
        logger.warning(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class SendEmailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated to send emails

    def post(self, request):
        # Extract data from the request
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        subject = request.data.get('subject')
        body = request.data.get('body')
        recipient_email = request.data.get('recipient_email')

        # Validate inputs
        if not first_name or not last_name or not subject or not body or not recipient_email:
            return Response({'error': 'First Name, Last Name, Subject, Body, and Recipient Email are required'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Format the email content
            formatted_body = f"Dear {first_name} {last_name},\n\n{body}"

            # Set up the MIME (Multipurpose Internet Mail Extensions) for the email
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER  # Your Gmail email address (configured in settings.py)
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(formatted_body, 'plain'))

            # Establish a secure SMTP connection with Gmail's server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                # Login to the Gmail account (this needs to be the email configured in settings.py)
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                
                # Send the email
                server.sendmail(settings.EMAIL_HOST_USER, recipient_email, msg.as_string())

            return Response({'success': f'Email sent successfully to {recipient_email}'}, status=status.HTTP_200_OK)

        except smtplib.SMTPException as e:
            # Log the error if the email sending fails
            return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)