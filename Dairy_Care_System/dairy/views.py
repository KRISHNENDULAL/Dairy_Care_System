from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Users_table, Products_table, ProductImage, WishlistItem, Animals_table, AnimalImages
from django.core.mail import send_mail
from django.conf import settings 
from django.contrib.auth.hashers import make_password, check_password
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
from django.utils import timezone



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

        # Send email notification
        subject = '🎉 Welcome to the Dairy Care System! 🎉'
        message = f"""
        Hello {username},

        Thank you for registering with us! We are excited to have you on board.
        Your account has been successfully created, and you can now log in.
        
        Important Warning: If you did not register for an account with this email address, please report it to us immediately at dairycaresystem25@gmail.com.
        If you have any questions or need assistance, feel free to reach out to us.
        
        Best regards,
        The Dairy Care System Team
        dairycaresystem25@gmail.com
        """
        send_mail(subject, message, 'dairycaresystem25@gmail.com', [email])

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
                    '🔒 Dairy Care System - Password Reset Request 🔒',
                    f'Hello {user.username},\n\n'
                    'We received a request to reset your password for your Dairy Care System account.\n\n'
                    'If you did not make this request, you can safely ignore this email.\n\n'
                    f'To reset your password, please click the link below:\n\n'
                    f'🔗 Reset Password Link: {reset_link}\n\n'
                    'If you encounter any issues or need further assistance, feel free to contact our support team.\n\n'
                    'Best regards,\n'
                    'The Dairy Care System Team',
                    'dairycaresystem25@gmail.com',  # Use the actual email configured in settings
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

        subject = '🎉 Welcome to the Dairy Care System 🎉'
        message = f"""
        Hello {username},

        We are pleased to inform you that your account has been successfully created!

        Here are your login credentials:
        Username: {username}
        Password: {password}

        🔗 Login Link: Click here to log in {login_link}

        We recommend that you log in and change your password in the profile option to ensure your account's security.

        If you have any questions or need assistance, please do not hesitate to reach out to us.

        Best regards,
        The Dairy Care System Team
        dairycaresystem25@gmail.com
        """

        send_mail(subject, message, 'dairycaresystem25@gmail.com', [email])

        return redirect('addemployee')

    return render(request, 'addemployee.html')


def login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to find the user by username or email
        user = Users_table.objects.filter(username=username_or_email).first() or Users_table.objects.filter(email=username_or_email).first()

        # Check if user exists and their account is active
        if user and user.status == 1:
            if user.password == password:
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
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Your account has been deactivated')

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


def reguserlist(request, role=None):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        if role == 'customer' or role == 'employee':
            users = Users_table.objects.filter(role=role)
        elif role == 'all':
            users = Users_table.objects.filter(role__in=['customer', 'employee'])
        else:
            users = []
        
        context = {
            'username': user.username,  # Pass the logged-in username to the template
            'users': users,  # Pass the list of users based on the role
            'role': role,    # Pass the role to identify if it’s customer, employee, or all
        }
        return render(request, 'reguserlist.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in


def regdeleteuser(request, user_id):
    user = get_object_or_404(Users_table, user_id=user_id)
    user.status = False  # Set status to inactive
    user.save()  # Save changes to the database
    # Send email notification
    subject = '⚠️ Account Deactivation Notification - Dairy Care System ⚠️'
    message = (
        f"Hello {user.username},\n\n"
        "We want to inform you that your account has been deactivated.\n\n"
        "If you believe this action was taken in error, please reach out to our support team at "
        "dairycaresystem25@gmail.com for assistance.\n\n"
        "Thank you for being a part of our community. We hope to resolve this matter quickly.\n\n"
        "Best regards,\n"
        "The Dairy Care System Team\n\n\n\n\n"
        "Disclaimer: This is an automated message. If you did not request this change, please contact our support team immediately."
    )

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]         

    send_mail(subject, message, from_email, recipient_list)
    return redirect('reguserlist', 'all')  # Redirect to the user list page


def restoreuser(request, user_id):
    user = get_object_or_404(Users_table, user_id=user_id)
    user.status = True  # Set status back to active
    user.save()  # Save changes to the database
    # Prepare email notification
    subject = '🎉 Account Reactivation Notification - Dairy Care System 🎉'
    message = (
        f"Hello {user.username},\n\n"
        "We are pleased to inform you that your account has been successfully reactivated.\n\n"
        "You can now log in and continue enjoying our services without interruption.\n\n"
        "If you have any questions or need assistance, feel free to reach out to our support team at "
        "dairycaresystem25@gmail.com.\n\n"
        "Best regards,\n"
        "The Dairy Care System Team\n\n\n\n\n"
        "Disclaimer: This is an automated message. If you did not request this change, please contact our support team immediately."
    )

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
    return redirect('reguserlist', 'all')  # Redirect to the user list page



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
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'feedbackpage.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in 
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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


# def user_logout(request):
#     logout(request)
#     return redirect('home')  # Redirect to home page or login page

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    request.session.flush()  # This clears the session data
    return redirect('home')


def addproducts(request): 
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_quantity = request.POST.get('product_quantity')
        quantity_unit = request.POST.get('quantity_unit')
        product_price = request.POST.get('product_price')  # Get the price from the POST data
        
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
            product_price=product_price,  # Add price to the product instance
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
        
        # Get the search query from the GET request (if any)
        search_query = request.GET.get('search', '')
        
        # If a search query exists, filter products based on the search term and their status
        if search_query:
            products = Products_table.objects.filter(product_name__icontains=search_query, status=True).select_related('employee')
        else:
            # Fetch all available products and the related employee who added them
            products = Products_table.objects.filter(status=True).select_related('employee')
        
        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to retain the input value in the search bar
        }
        
        return render(request, 'productslist.html', context)
    
    else:
        return redirect('login')  # Redirect to login if no user is logged in

    

def custproductslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        search_query = request.GET.get('search', '')  # Get the search query from the GET request
        
        # If a search query exists, filter the products based on the search term
        if search_query:
            products = Products_table.objects.filter(product_name__icontains=search_query, status=True)
        else:
            # Fetch all available products if no search query is provided
            products = Products_table.objects.filter(status=True)
        
        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to the template (optional for retaining input value)
        }
        return render(request, 'custproductslist.html', context)
    
    else:
        return redirect('login')  # Redirect to login if no user is logged in

    

def productdetails(request, product_id):
    product = get_object_or_404(Products_table, product_id=product_id)
    images = product.images.all()  # Get associated images

    if request.method == 'POST':
        if 'add_to_wishlist' in request.POST:
            user_id = request.session.get('user_id')
            if user_id:
                user = Users_table.objects.get(user_id=user_id)
                wishlist_item, created = WishlistItem.objects.get_or_create(user=user, product=product)

                if created:
                    messages.success(request, 'Product added to wishlist!')
                else:
                    messages.info(request, 'Product is already in your wishlist.')
            else:
                messages.error(request, 'You need to log in to add to your wishlist.')

    context = {
        'product': product,
        'images': images,
    }
    return render(request, 'productdetails.html', context)



# View to display the wishlist page
def wishlist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = get_object_or_404(Users_table, user_id=user_id)  # Fetch the user object using user_id

        if request.method == 'POST':
            product_id = request.POST.get('remove_product_id')  # Get the product ID from the form
            print("Product ID to remove:", product_id)  # Debugging line
            if product_id:
                try:
                    wishlist_item = WishlistItem.objects.get(user=user, product_id=product_id)
                    wishlist_item.delete()  # Remove the product from the wishlist
                    print("Wishlist item removed:", wishlist_item)  # Debugging line
                    messages.success(request, 'Product removed from your wishlist.')
                except WishlistItem.DoesNotExist:
                    print("Wishlist item does not exist.")  # Debugging line
                    messages.error(request, 'This product is not in your wishlist.')
            return redirect('wishlist')  # Redirect to avoid form resubmission

        # Fetch the wishlist items for the user
        wishlist_items = WishlistItem.objects.filter(user=user).select_related('product')

        context = {
            'wishlist': wishlist_items,  # Pass the wishlist items to the template
            'username': user.username,   # Pass the username to the template
            'error': None
        }
    else:
        messages.error(request, "You need to log in to view your wishlist.")
        context = {
            'wishlist': [],
            'username': None,
            'error': "You need to log in to view your wishlist."
        }

    return render(request, 'wishlist.html', context)


def editproduct(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session

    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id

        # Get the search query from the GET request (if any)
        search_query = request.GET.get('search', '')

        # If a search query exists, filter products based on the search term
        if search_query:
            products = Products_table.objects.filter(product_name__icontains=search_query)
        else:
            # Fetch all products if no search query is provided
            products = Products_table.objects.all()

        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to retain the input value in the search bar
        }

        return render(request, 'editproduct.html', context)

    else:
        return redirect('login')  # Redirect to login if no user is logged in

    


def updateproduct(request, product_id):
    product = Products_table.objects.get(product_id=product_id)
    images = ProductImage.objects.filter(product=product)

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.product_description = request.POST.get('product_description')
        product.product_quantity = request.POST.get('product_quantity')
        product.quantity_unit = request.POST.get('quantity_unit')
        product.product_price = request.POST.get('product_price')
        product.save()

        # Handle new image upload
        product_photo = request.FILES.get('product_images')  # Ensure this matches your input name
        if product_photo:
            # Delete existing images
            ProductImage.objects.filter(product=product).delete()  # Delete all old images
            ProductImage.objects.create(product=product, image=product_photo)  # Add new image

        return redirect('editproduct')  # Redirect to a detail page after update

    context = {
        'product': product,
        'images': images,
    }
    return render(request, 'updateproduct.html', context)


def deleteproduct(request, product_id):
    product = get_object_or_404(Products_table, product_id=product_id)
    product.status = False  # Set status to 0 (deleted)
    product.save()
    return redirect('editproduct')  # Redirect to the product listing page

def restoreproduct(request, product_id):
    product = get_object_or_404(Products_table, product_id=product_id)
    product.status = True  # Set status to 1 (active)
    product.save()
    return redirect('editproduct')  # Redirect to the product listing page



def animalslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        # Fetch all animals with their related images
        animals = Animals_table.objects.prefetch_related('images').all()  # Use the correct related name
        
        # Calculate the age of each animal in years based on date_of_birth
        for animal in animals:
            # Assuming 'date_of_birth' is the field that indicates the animal's birthdate
            if animal.date_of_birth:
                current_date = timezone.now().date()  # Get the current date
                animal_age_years = (current_date - animal.date_of_birth).days // 365  # Calculate age in years
                animal.age_in_years = animal_age_years  # Add a custom attribute to hold the age

        context = {
            'username': user.username,  # Pass the username to the template
            'animals': animals,         # Pass the list of animals to the template
        }
        return render(request, 'animalslist.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in



def addanimal(request):
    if request.method == 'POST':
        # Fetch form data
        animal_name = request.POST.get('animal_name')
        animal_category = request.POST.get('animal_type')
        breed = request.POST.get('breed')
        date_of_birth = request.POST.get('date_of_birth') if request.POST.get('date_of_birth') else None
        gender = request.POST.get('gender')
        milk_capacity = request.POST.get('milk_capacity') if request.POST.get('milk_capacity') else None

        # Fetch the currently logged-in user's ID as 'added_by'
        by_user_id = request.session.get('user_id')  # Get the user_id from session
        
        # Get the Users_table instance corresponding to the user_id
        added_by_user = get_object_or_404(Users_table, pk=by_user_id)

        # Create a new animal record with the user instance in the added_by field
        animal = Animals_table.objects.create(
            animal_name=animal_name,
            animal_category=animal_category,
            breed=breed,
            date_of_birth=date_of_birth,
            gender=gender,
            milk_capacity=milk_capacity,
            added_by=added_by_user  # Assign the user instance, not the raw ID
        )

        # Handle multiple file uploads
        if request.FILES.getlist('animal_images'):
            for img in request.FILES.getlist('animal_images'):
                animal_image = AnimalImages(
                    animal=animal,
                    animal_image=img
                )
                animal_image.save()

        # Redirect to the animals list page after successfully adding the animal
        return redirect('animalslist')

    # If GET request, render the form page
    return render(request, 'addanimal.html')





"""def login(request):
    return render(request, 'login.html')

def registration(request):
    return render(request, 'registration.html')

def addproducts(request): 
    return render(request, 'addproducts.html') 

def productslist(request):
    return render(request, 'login.html')  """