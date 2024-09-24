from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Users_table, Products_table, ProductImage
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
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required


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
        if Users_table.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('registration')

        if Users_table.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('registration')

        # Create the new user with hashed password
        user = Users_table(username=username, email=email, phone=phone, password=password)
        user.save()

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'registration.html')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Users_table.objects.filter(email=email).first()
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
                    f'Hello {user.username},\n\nWe have got a password reset request.\n\nClick the link below to reset your password:\n\n{reset_link}',
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
    user = Users_table.objects.filter(reset_token=token).first()
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


# @login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminpage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
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
        if Users_table.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('addemployee')

        if Users_table.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('addemployee')

        # Generate a secure random password
        password = generate_random_password()

        # Create the new employee with the role set to 'employee'
        user = Users_table(username=username, email=email, phone=phone, password=password, role='employee')
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
        message = f"Hello {username},\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\nLogin Link: {login_link}\n\nPlease log in and change your password in the profile option."
        send_mail(subject, message, 'admin@example.com', [email])

        return redirect('addemployee')

    return render(request, 'addemployee.html')


def login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to find the user by username or email
        user = Users_table.objects.filter(username=username_or_email).first() or Users_table.objects.filter(email=username_or_email).first()

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
                user = Users_table.objects.get(user_id=user_id)
                user.password = new_password  # Update with the new password
                user.save()

                messages.success(request, 'Password reset successful. Please log in with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            return redirect('login')

    return render(request, 'changepassword.html')



def regusersview(request, role):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        # Fetch users based on the provided role
        users = Users_table.objects.filter(role=role)
        
        context = {
            'username': user.username,  # Pass the username to the template
            'users': users,             # Pass the list of users with the specified role
            'role': role                # Pass the role to the template
        }
        
        return render(request, 'regusersview.html', context)
    else:
        return redirect('login')  # Redirect to the login page if no user_id in session
    



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customerpage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'customerpage.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def employeepage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'employeepage.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in 



def feedbackpage(request):
    return render(request, 'feedbackpage.html')


def userprofile(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'user': user,  # Pass the entire user object to the template
        }
        return render(request, 'userprofile.html', context)
    else: 
        return render(request, 'login.html')


def updateuserprofile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Redirect if not logged in

    user = Users_table.objects.get(user_id=user_id)  # Fetch the user

    if request.method == 'POST':
        # Update user fields
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.save()  # Save changes

        messages.success(request, 'Profile updated successfully.')

    context = {
        'user': user
    }
    return render(request, 'updateuserprofile.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to home page or login page


def addproducts(request): 
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_quantity = request.POST.get('product_quantity')
        quantity_unit = request.POST.get('quantity_unit')
        
        # Get user_id from the session
        employee_user_id = request.session.get('user_id')  # Assuming 'user_id' is stored in the session for employees

        try:
            # Fetch the Users_table instance
            employee = Users_table.objects.get(user_id=employee_user_id)  # Adjust this if your Users_table uses a different field
            
        except Users_table.DoesNotExist:
            messages.error(request, 'Employee not found.')
            return redirect('productslist')  # Handle user not found

        # Create a new product entry
        product = Products_table(
            product_name=product_name,
            product_description=product_description,
            product_quantity=product_quantity,
            quantity_unit=quantity_unit,
            employee=employee  # Assign the logged-in employee
        )
        product.save()

        # If a photo was uploaded, create a new ProductImage entry
        product_photo = request.FILES.get('product_images')  # Ensure this matches your input name
        if product_photo:
            ProductImage.objects.create(product=product, image=product_photo)  # Update here

        # messages.success(request, f'Product "{product_name}" added successfully!')
        return redirect('productslist')  # Redirect to the products list page

    return render(request, 'addproducts.html')


def productslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        # Fetch all products and their images
        products = Products_table.objects.filter(status=True)  # Only get available products
        
        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,        # Pass the products to the template
        }
        return render(request, 'productslist.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in
    

def custproductslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        # Fetch all products and their images
        products = Products_table.objects.filter(status=True)  # Only get available products
        
        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,        # Pass the products to the template
        }
        return render(request, 'custproductslist.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in
    

def productdetails(request, product_id):
    product = get_object_or_404(Products_table, product_id=product_id)
    images = product.images.all()  # Get associated images
    context = {
        'product': product,
        'images': images,
    }
    return render(request, 'productdetails.html', context)


def updateproduct(request):
    products = Products_table.objects.prefetch_related('images').all()
    products_data = [
        {
            'product_name': product.product_name,
            'product_description': product.product_description,
            'product_quantity': product.product_quantity,
            'quantity_unit': product.quantity_unit,
            'images': [{'image_url': image.image.url} for image in product.images.all()]
        }
        for product in products
    ]

    return render(request, 'updateproduct.html', {'products': products_data})
 



"""def login(request):
    return render(request, 'login.html')

def registration(request):
    return render(request, 'registration.html')

def addproducts(request): 
    return render(request, 'addproducts.html') 

def productslist(request):
    return render(request, 'login.html')  """