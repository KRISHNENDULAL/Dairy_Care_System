from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import random
import string
import logging
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth import logout


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def contactus(request):
    return render(request, 'contactus.html')


def registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']

        # Check if the username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('registration')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('registration')

        # Create the new user with hashed password
        user = User(username=username, email=email, phone=phone, password=password)
        user.save()

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'registration.html')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            # Generate a unique token
            token = get_random_string(20)
            
            # Save the token to the user's record
            user.reset_token = token
            user.save()
            
            # Create the password reset link
            reset_link = request.build_absolute_uri(reverse('resetpassword', args=[token]))
            
            # Send the email
            try:
                send_mail(
                    'Dairy Care System - Password Reset Request',
                    f'We have got a password reset request.\n\nClick the link below to reset your password:\n\n{reset_link}',
                    'your-email@example.com',  # Use the actual email configured in settings
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Password reset link has been sent to your email.')
            except Exception as e:
                messages.error(request, f"Error sending email: {str(e)}")
        else:
            messages.error(request, 'No account found with that email.')

    return render(request, 'forgotpassword.html')


def resetpassword(request, token):
    user = User.objects.filter(reset_token=token).first()
    if user:
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.password = new_password
                user.reset_token = None
                user.save()
                messages.success(request, 'Password reset successful. You can now log in.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'resetpassword.html', {'token': token})
    else:
        messages.error(request, 'Invalid or expired reset token.')
        return redirect('forgotpassword')


def adminpage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = User.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'adminpage.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in 
    

def generate_random_password():
    length = 8

    # Ensure that the password contains at least one character from each category
    password = [
        random.choice(string.ascii_uppercase),  # Uppercase letter
        random.choice(string.ascii_lowercase),  # Lowercase letter
        random.choice(string.digits),           # Digit
        random.choice(string.punctuation)       # Special character
    ]

    # Fill the remaining characters randomly from all categories
    remaining_length = length - len(password)
    all_characters = string.ascii_letters + string.digits + string.punctuation
    password += random.choices(all_characters, k=remaining_length)

    # Shuffle the password list to ensure randomness
    random.shuffle(password)

    return ''.join(password)


def addemployee(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']

        # Check if the username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('addemployee')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('addemployee')

        # Generate a secure random password
        password = generate_random_password()

        # Create the new employee with the role set to 'employee'
        user = User(username=username, email=email, phone=phone, password=password, role='employee')
        user.save()

        # Print success message only after saving the user
        messages.success(request, f"Employee '{username}' added successfully and email sent with login credentials.")

        # Get the current site
        current_site = get_current_site(request)
        domain = current_site.domain

        # Construct the full login link
        login_link = f"http://{domain}/login"

        # Send email with login credentials
        subject = 'Welcome to the Dairy Care System'
        message = f"Hello {username},\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\nLogin Link: {login_link}\n\nPlease log in and change your password in profile option."
        send_mail(subject, message, 'admin@example.com', [email])

        return redirect('addemployee')

    return render(request, 'addemployee.html')


def login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to find the user by username or email
        user = User.objects.filter(username=username_or_email).first() or User.objects.filter(email=username_or_email).first()

        if user and user.password == password:
            # Store user information in session
            request.session['user_id'] = user.user_id
            request.session['username'] = user.username

            # Redirect based on user role
            if user.role == 'customer':
                return redirect('customerpage')
            elif user.role == 'employee':
                if user.password == password:  # Assuming the random password is stored in plain text (ideally it should be hashed)
                    return redirect('employeepage')
            elif user.role == 'admin':
                return redirect('adminpage')
        else:
            messages.error(request, 'Invalid username/email or password')
            return render(request, 'login.html')

    return render(request, 'login.html')


def changepassword(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']

            if new_password == confirm_password:
                user = User.objects.get(user_id=user_id)
                user.password = new_password  # Update with the new password
                user.save()

                messages.success(request, 'Password reset successful. Please log in with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            return redirect('login')

    return render(request, 'changepassword.html')


def customerpage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = User.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'customerpage.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in
    

def employeepage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = User.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'employeepage.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in 



def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to home page or login page


def feedbackpage(request):
    return render(request, 'feedbackpage.html')


def userprofile(request):
    return render(request, 'userprofile.html')




""" def login(request):
    return render(request, 'login.html')

def signin(request):
    return render(request, 'signin.html') """


""" # Function to generate a random password
def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def addemployee(request):
    success_message = None
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = generate_random_password()

        # Create a new User instance with the role set to 'employee'
        user = User(
            username=username,
            email=email,
            phone=phone,
            role='employee'
        )
        user.set_password(password)
        user.save()

        token = get_random_string(32)

        # Save the token and related email in the database
        # Here, you should save the token along with the email in a database table like 'PasswordTokens'

        reset_link = f"{request.build_absolute_uri('/reset-password/')}{token}/"
        send_mail(
            'Reset Your Password',
            f'Hi {username},\n\nClick the link below to reset your password:\n{reset_link}\n\nThis link is valid for only one use.',
            'krishnendulal113@gmail.com',
            [email],
            fail_silently=False,
        )

        success_message = f"Employee '{username}' added successfully!"

    return render(request, 'addemployee.html', {'success_message': success_message})


def reset_password(request, token):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password == confirm_password:
            # Update the password in the database
            # Ensure the token is valid and associated with an email address
            query = f"UPDATE users SET password='{new_password}' WHERE email=(SELECT email FROM password_tokens WHERE token='{token}')"
            # Execute this query using the preferred database method

            # Delete the used token from the database to prevent reuse

            return render(request, 'reset_password.html', {'message': 'Password updated successfully!'})

    return render(request, 'reset_password.html', {'token': token}) """