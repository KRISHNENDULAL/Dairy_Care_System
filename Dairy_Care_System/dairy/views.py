from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Users_table, Products_table, ProductImage, Feedback_table, WishlistItem, PreOrder, Cart, Order_table, OrderItem_table, Address_table, Notifications_table, Animals_table, AnimalImages, AnimalHealth_table
from django.core.mail import send_mail
from django.conf import settings 
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.dateparse import parse_date
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth import logout 
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q  # Import Q for case-insensitive query
from google.cloud import dialogflow_v2 as dialogflow
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.cloud import vision
from google.oauth2 import service_account
from google.cloud.vision_v1 import types
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime

from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count, Q

import io
import razorpay
import random
import string
import logging
import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
import json
import qrcode
import cv2
import numpy as np
from .utils.image_search import ImageSearcher
from .utils.delivery_assignment import DeliveryAssignment


DAIRY_KEYWORDS = {
    # Basic dairy products with variations
    'milk', 'dairy', 'milk product', 'dairy product',
    'milk bottle', 'milk pack', 'milk packet', 'milk container',
    
    # Milk varieties and types
    'whole milk', 'full cream milk', 'toned milk', 'double toned milk',
    'skimmed milk', 'skim milk', 'low fat milk', 'full fat milk',
    'cow milk', 'buffalo milk', 'fresh milk', 'pasteurized milk',
    'homogenized milk', 'raw milk', 'organic milk', 'flavored milk',
    
    # Milk packaging terms
    'milk carton', 'milk jug', 'milk pouch', 'milk packaging',
    'milk box', 'milk sachet', 'milk bag', 'milk container',
    
    # Common milk brands and descriptors
    'amul milk', 'milma', 'mother dairy', 'dairy fresh',
    'farm fresh milk', 'pure milk', 'natural milk',
    
    # Other dairy products
    'curd', 'yogurt', 'butter', 'cheese', 'cream',
    'ghee', 'paneer', 'buttermilk', 'lassi', 'whey',
    
    # Milk processing and storage
    'pasteurized', 'homogenized', 'refrigerated milk',
    'cold milk', 'fresh dairy', 'dairy farm', 'milk farm'
}

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def contactus(request):
    return render(request, 'contactus.html')


def productexplore(request):

        search_query = request.GET.get('search', '')  # Get the search query from the GET request
        selected_category = request.GET.get('product_category', '')  # Selected category

        # Fetch all products filtered by status
        products = Products_table.objects.order_by('product_name')

        # Apply search filter if search query is provided
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        # Apply category filter if a category is selected
        if selected_category:
            products = products.filter(product_category=selected_category)

        context = {
            # 'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to the template (optional for retaining input value)
            'selected_category': selected_category,  # Pass the selected category to retain its value
        }
        return render(request, 'productexplore.html', context)

    

otp_storage = {}

def send_otp_email(user_email):
    otp = random.randint(1000, 9999)  # Generate a random OTP
    otp_storage[user_email] = otp  # Store the OTP for later verification

    subject = 'Dairy Care System - Email Verification'
    message = f"""
    Dear User,

    Thank you for registering with Dairy Care System. 
    To complete your email verification, please use the following One-Time Password (OTP):

    OTP: {otp}

    This OTP is valid for the next 10 minutes. Please do not share it with anyone. If you did not request this, please ignore this email.

    Regards,
    Dairy Care System Team
    dairycaresystem25@gmail.com
    """
    from_email = 'dairycaresystem25@gmail.com'  # Your system email
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


def regmailverify(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Users_table.objects.filter(username=email).exists():
            messages.info(request, "Email is already registered. Please log in.")
            return redirect('login')

        send_otp_email(email)

        request.session['user_email'] = email

        return redirect('regotpverify')

    return render(request, 'regmailverify.html')


def regotpverify(request):
    email = request.session.get('user_email') 

    if not email:
        messages.error(request, "Session expired. Please enter your email again.")
        return redirect('enter_email')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')

        if otp_storage.get(email) and otp_storage[email] == int(otp_input):
          
            del otp_storage[email]
            request.session['verified_email'] = email

            return redirect('registration')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'regotpverify.html')


def registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        pincode = request.POST['pincode']
        role = request.POST['role']  
        password = request.POST['password']

        # Check if the username or email already exists
        if Users_table.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('registration')

        if Users_table.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('registration')
        
        if not role:
            messages.error(request, 'Please select a role.')
            return redirect('registration')

        # Create the new user with hashed password
        user = Users_table(username=username, email=email, phone=phone, pincode=pincode, password=password, role=role)
        user.save()

        # Send email notification
        subject = 'Welcome to the Dairy Care System! 🎉'
        message = f"""
        Hello {username},

        Thank you for registering with us! We are excited to have you on board.
        Your account has been successfully created as a {role}, and you can now log in.
        
        Important Warning: If you did not register for an account with this email address, please report it to us immediately at dairycaresystem25@gmail.com.
        If you have any questions or need assistance, feel free to reach out to us.
        
        Best regards,
        The Dairy Care System Team
        dairycaresystem25@gmail.com
        """
        send_mail(subject, message, 'dairycaresystem25@gmail.com', [email])

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    else:
        # Pre-fill the email field with the verified email from the session
        verified_email = request.session.get('verified_email', '')
        context = {'verified_email': verified_email}
        return render(request, 'registration.html', context)



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
                    'Dairy Care System - Password Reset Request 🔒',
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
        pincode = request.POST['pincode']

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
        user = Users_table(username=username, email=email, phone=phone, pincode=pincode, password=password, role='employee')
        user.save()

        # Print success message only after saving the user
        messages.success(request, f"Delivery Employee '{username}' added successfully and email sent with login credentials.")

        # Get the current site
        current_site = get_current_site(request)
        domain = current_site.domain

        # Construct the full login link
        login_link = f"http://{domain}/login"

        # Send email with login credentials

        subject = 'Welcome to the Dairy Care System 🎉'
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
            # Use check_password to validate the hashed password
            if check_password(password, user.password):
                # Store user information in session
                request.session['user_id'] = user.user_id
                request.session['username'] = user.username

                # Redirect based on user role
                if user.role == 'customer':
                    return redirect('customerpage')
                elif user.role == 'owner':
                    return redirect('farmownerpage')
                elif user.role == 'employee':
                    return redirect('employeepage')
                elif user.role == 'admin':
                    return redirect('adminpage')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Your account has been deactivated')

        return render(request, 'login.html')

    return render(request, 'login.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def changepassword(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in

    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id

    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password == confirm_password:
            user.password = new_password  # Update with the new password
            user.save()
            messages.success(request, 'Password reset successful. Please log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')

    # Render the change password page with the username
    context = {
        'username': user.username,  # Pass the username to the template
        'user': user  # Pass the entire user object to the template
    }
    return render(request, 'changepassword.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reguserlist(request, role=None):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        if role == 'customer' or role == 'owner' or role == 'employee':
            users = Users_table.objects.filter(role=role)
        elif role == 'all':
            users = Users_table.objects.filter(role__in=['customer', 'owner', 'employee'])
        else:
            users = []
        
        context = {
            'username': user.username,  # Pass the logged-in username to the template
            'users': users,  # Pass the list of users based on the role
            'role': role,    # Pass the role to identify if it's customer, employee, or all
        }
        return render(request, 'reguserlist.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in



def regdeleteuser(request, user_id):
    reason = request.GET.get('reason')
    if not reason:
        return HttpResponseBadRequest("Reason for deactivation is required.")
    
    user = get_object_or_404(Users_table, user_id=user_id)
    user.status = False  # Set status to inactive
    user.save()  # Save changes to the database
    
    # Send email notification
    subject = 'Account Deactivation Notification - Dairy Care System ⚠️'
    message = (
        f"Hello {user.username},\n\n"
        "We want to inform you that your account has been deactivated.\n\n"
        f"Reason for deactivation: {reason}\n\n"
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
    subject = 'Account Reactivation Notification - Dairy Care System 🎉'
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



def deleteaccount(request, user_id):
    user = get_object_or_404(Users_table, user_id=user_id)
    user.status = False  # Set status to inactive
    user.save()  # Save changes to the database
    
    # Send email notification
    subject = 'Account Deletion Notification - Dairy Care System ⚠️'
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
    return redirect('home')  



def get_seasonal_recommendations():
    from datetime import datetime

    month = datetime.now().month

    if month in [12, 1, 2]:  # Winter
        return Products_table.objects.filter(product_category="Dairy-based sweets")[:2]
    elif month in [6, 7, 8]:  # Summer
        return Products_table.objects.filter(product_category="Cold milk beverages")[:2]
    return []



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customerpage(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = Users_table.objects.get(user_id=user_id)

    last_month = now() - timedelta(days=30)

    # Fetch top-selling products in the last month
    top_selling_products = (
        OrderItem_table.objects.filter(order__order_date__gte=last_month)
        .values('product_id')
        .annotate(total_sold=Count('product_id'))
        .order_by('-total_sold')[:4]
    )

    # Get product details for top-selling items
    top_products = Products_table.objects.filter(product_id__in=[p['product_id'] for p in top_selling_products])

    # Fetch user's past purchases
    user_purchased_products = OrderItem_table.objects.filter(order__user=user).values_list('product_id', flat=True)

    # Fetch user's wishlisted items
    wishlisted_products = WishlistItem.objects.filter(user=user).values_list('product_id', flat=True)

    # Identify similar products based on the category of purchased/wishlisted products
    similar_products = Products_table.objects.filter(
        Q(product_category__in=Products_table.objects.filter(product_id__in=user_purchased_products).values_list('product_category', flat=True))
        | Q(product_id__in=wishlisted_products)
    ).exclude(product_id__in=user_purchased_products).distinct()[:4]

    # Add seasonal products dynamically
    seasonal_products = get_seasonal_recommendations()

    # Merge all recommendations with AI-based rule adjustments
    final_recommendations = list(top_products) + list(similar_products) + list(seasonal_products)

    # Remove duplicates and keep top 6 recommendations
    final_recommendations = list(set(final_recommendations))[:6]

    return render(request, 'customerpage.html', {
        'username': user.username,
        'recommended_products': final_recommendations
    })



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
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmownerpage(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'farmownerpage.html', context)
    else:
        return redirect('login')
    


PROJECT_ID = 'dairybot-ygjc'  # Replace with your Dialogflow project ID

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()

            # Comprehensive dairy-related responses
            responses = {
                'products_general': {
                    'keywords': ['products', 'items', 'available', 'sell', 'offering'],
                    'response': "We offer a wide range of dairy products including:\n"
                               "• Fresh Milk (Full cream, Toned, Double-toned)\n"
                               "• Curd and Yogurt\n"
                               "• Butter and Ghee\n"
                               "• Cheese varieties\n"
                               "• Paneer\n"
                               "• Cream\n"
                               "You can view all products and their prices in our Products List section."
                },
                
                'milk_specific': {
                    'keywords': ['milk', 'fresh milk', 'milk types', 'milk variety'],
                    'response': "Our milk varieties include:\n"
                               "• Full Cream Milk (6% fat)\n"
                               "• Toned Milk (3% fat)\n"
                               "• Double Toned Milk (1.5% fat)\n"
                               "• Skimmed Milk (0.3% fat)\n"
                               "All our milk is pasteurized and packed fresh daily."
                },
                
                'product_quality': {
                    'keywords': ['quality', 'fresh', 'pure', 'natural', 'organic'],
                    'response': "We maintain the highest quality standards:\n"
                               "• All products are sourced from our own dairy farms\n"
                               "• Regular quality checks and testing\n"
                               "• No artificial preservatives\n"
                               "• Hygienically packed\n"
                               "• Temperature-controlled storage and delivery"
                },
                
                'storage': {
                    'keywords': ['store', 'storage', 'keep', 'refrigerate', 'preserve'],
                    'response': "Storage recommendations:\n"
                               "• Milk: Refrigerate at 4°C, consume within 2-3 days\n"
                               "• Curd: Refrigerate, consume within 5-7 days\n"
                               "• Butter: Refrigerate, use within 2-3 weeks\n"
                               "• Cheese: Refrigerate, check package for expiry\n"
                               "• Ghee: Store in cool, dry place, can last 6-12 months"
                },
                
                'delivery': {
                    'keywords': ['delivery', 'shipping', 'deliver', 'ship', 'when'],
                    'response': "Our delivery service:\n"
                               "• Daily morning delivery (6 AM - 9 AM)\n"
                               "• Evening delivery slot (4 PM - 7 PM)\n"
                               "• Free delivery for orders above ₹500\n"
                               "• Temperature-controlled delivery vehicles\n"
                               "• Real-time order tracking available"
                },
                
                'ordering': {
                    'keywords': ['order', 'buy', 'purchase', 'booking', 'cart'],
                    'response': "How to order:\n"
                               "1. Browse our Products List\n"
                               "2. Add items to cart\n"
                               "3. Select delivery time slot\n"
                               "4. Choose payment method\n"
                               "5. Place order\n"
                               "You can also set up daily/weekly subscriptions!"
                },
                
                'payment': {
                    'keywords': ['payment', 'pay', 'price', 'cost', 'rates'],
                    'response': "Payment options:\n"
                               "• Online payment (Credit/Debit cards)\n"
                               "• UPI payments\n"
                               "• Net banking\n"
                               "• Cash on delivery\n"
                               "• Monthly subscription billing available"
                },
                
                'subscription': {
                    'keywords': ['subscription', 'daily', 'weekly', 'monthly', 'regular'],
                    'response': "Subscription benefits:\n"
                               "• Regular delivery at preferred time\n"
                               "• 10% discount on subscription orders\n"
                               "• Flexible pause/resume option\n"
                               "• Easy quantity modification\n"
                               "• Monthly billing facility"
                },
                
                'returns': {
                    'keywords': ['return', 'refund', 'replace', 'exchange', 'damaged'],
                    'response': "Our return policy:\n"
                               "• Report issues within 24 hours of delivery\n"
                               "• Immediate replacement for quality issues\n"
                               "• Full refund for valid complaints\n"
                               "• Photo evidence might be required\n"
                               "Contact our support team for assistance."
                },
                
                'farm_info': {
                    'keywords': ['farm', 'source', 'cattle', 'cow', 'buffalo'],
                    'response': "About our farms:\n"
                               "• Own dairy farms with healthy cattle\n"
                               "• Regular veterinary care\n"
                               "• Organic feed for cattle\n"
                               "• Modern milking facilities\n"
                               "• Strict hygiene protocols"
                },
                
                'contact': {
                    'keywords': ['contact', 'help', 'support', 'reach', 'complaint'],
                    'response': "Contact us:\n"
                               "• Customer Care: +91-XXXXXXXXXX\n"
                               "• Email: dairycaresystem25@gmail.com\n"
                               "• Working hours: 8 AM - 8 PM\n"
                               "• Emergency support available 24/7\n"
                               "• Feedback form available on website"
                },
                
                'offers': {
                    'keywords': ['offer', 'discount', 'deal', 'save', 'promotion'],
                    'response': "Current offers:\n"
                               "• 10% off on subscription orders\n"
                               "• Buy 3 get 1 free on curd products\n"
                               "• Free delivery above ₹500\n"
                               "• Referral bonus: ₹100 off\n"
                               "Check our website for more offers!"
                }
            }

            # Check for matching keywords and return appropriate response
            for category in responses.values():
                if any(keyword in user_message for keyword in category['keywords']):
                    return JsonResponse({'response': category['response']})

            # Default response if no keywords match
            return JsonResponse({
                'response': "I'm here to help with any dairy-related queries! You can ask about:\n"
                           "• Our dairy products and their quality\n"
                           "• Ordering and delivery\n"
                           "• Storage recommendations\n"
                           "• Payment options and offers\n"
                           "• Farm information\n"
                           "Please rephrase your question or choose from these topics."
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def feedbackpage(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')  
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)  
        # Fetch products with status 1 to display in the dropdown
        products = Products_table.objects.filter(status=1)  

        if request.method == 'POST':
            product_id = request.POST.get('product')
            rating = request.POST.get('star')
            feedback_text = request.POST.get('feedback')

            # Handle overall site feedback
            if product_id == 'feedback':
                feedback = Feedback_table.objects.create(
                    user=user,
                    product=None,  # No product associated for site feedback
                    rating=rating,
                    feedback_text=feedback_text
                )
            # Handle product-specific feedback
            else:
                product = get_object_or_404(Products_table, pk=product_id)
                feedback = Feedback_table.objects.create(
                    user=user,
                    product=product,
                    rating=rating,
                    feedback_text=feedback_text
                )

            feedback.save()
            messages.success(request, 'Thank you! Your feedback has been submitted successfully.')
            return redirect('feedbackpage')  # Redirect after submission

        # Pass username and products to the template
        context = {
            'username': user.username,  
            'products': products,
        }
        return render(request, 'feedbackpage.html', context)

    else:
        # Redirect to login if no user is logged in
        return redirect('login')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminfeedbackreview(request):
    feedback_list = Feedback_table.objects.all().order_by('-created_at')
    return render(request, 'adminfeedbackreview.html', {'feedback_list': feedback_list})



def get_sentiment_label(score):
    if score > 0.05:
        return 'Positive', 'text-success'
    elif score < -0.05:
        return 'Negative', 'text-danger'
    else:
        return 'Neutral', 'text-warning'



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def feedbackreview(request):
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            user = Users_table.objects.get(user_id=user_id)
            feedback_list = Feedback_table.objects.filter(
                product__employee_id=user_id
            ).select_related('user', 'product__employee').order_by('-created_at')
            
            # Initialize VADER
            analyzer = SentimentIntensityAnalyzer()
            
            # Process each feedback with sentiment analysis
            analyzed_feedback = []
            for feedback in feedback_list:
                # TextBlob analysis
                blob = TextBlob(feedback.feedback_text)
                textblob_score = blob.sentiment.polarity
                
                # VADER analysis
                vader_scores = analyzer.polarity_scores(feedback.feedback_text)
                vader_compound = vader_scores['compound']
                
                # Get sentiment labels
                textblob_label, textblob_class = get_sentiment_label(textblob_score)
                vader_label, vader_class = get_sentiment_label(vader_compound)
                
                analyzed_feedback.append({
                    'feedback': feedback,
                    'textblob': {
                        'score': round(textblob_score, 2),
                        'label': textblob_label,
                        'class': textblob_class
                    },
                    'vader': {
                        'score': round(vader_compound, 2),
                        'label': vader_label,
                        'class': vader_class
                    }
                })
            
            context = {
                'username': user.username,
                'feedback_list': analyzed_feedback,
            }
            
            return render(request, 'feedbackreview.html', context)
        
        except Users_table.DoesNotExist:
            return redirect('login')
    
    else:
        return redirect('login')

    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def custfeedback(request):
    user_id = request.session.get('user_id')  # Retrieve the logged-in user's ID from the session

    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)

        # Filter feedback submitted by the logged-in user
        feedback_list = Feedback_table.objects.filter(
            user_id=user_id
        ).select_related('product', 'product__employee').order_by('-created_at')

        # Prepare the context for the template
        context = {
            'username': user.username,  # Pass the username to the template
            'feedback_list': feedback_list  # Pass the feedback list to the template
        }

        return render(request, 'custfeedback.html', context)
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



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
        user.pincode = request.POST.get('pincode')
        user.save()  # Save changes

        messages.success(request, 'Profile updated successfully.')

    context = {
        'user': user
    }
    return render(request, 'updateuserprofile.html', context)



# def send_otp(request):
#     if request.user.is_authenticated:
#         otp = random.randint(1000, 9999)
#         request.session['otp'] = otp  # Store OTP in session
#         # Here, implement logic to send OTP to `request.user.phone`
#         print(f"OTP sent to {request.user.phone}: {otp}")  # Debugging purpose
#         return JsonResponse({'success': True, 'message': 'OTP sent successfully!'})
#     return JsonResponse({'success': False, 'message': 'User not authenticated.'})



# @csrf_exempt
# def verify_otp(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         data = json.loads(request.body)
#         user_otp = data.get('otp')
#         session_otp = request.session.get('otp')

#         if str(user_otp) == str(session_otp):
#             user = Users_table.objects.get(user_id=request.user.user_id)
#             user.is_phone_verified = True
#             user.save()
#             return JsonResponse({'success': True, 'message': 'Phone verified successfully!'})
#         else:
#             return JsonResponse({'success': False, 'message': 'Invalid OTP. Please try again.'})
#     return JsonResponse({'success': False, 'message': 'Invalid request.'})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    request.session.flush()  # This clears the session data
    return redirect('home')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addproducts(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in

    try:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
    except Users_table.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('login')

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        product_category = request.POST.get('product_category')  # Get the product category
        product_subcategory = request.POST.get('product_subcategory')  # Get the product category
        product_quantity = request.POST.get('product_quantity')
        quantity_unit = request.POST.get('quantity_unit')
        product_price = request.POST.get('product_price')  # Get the price from the POST data
        product_photo = request.FILES.get('product_images')

        # Check if a product with the same name exists for the current employee
        if Products_table.objects.filter(product_name__iexact=product_name, employee=user).exists():
            messages.error(request, 'You already have a product with this name.')
            return render(request, 'addproducts.html', {'username': user.username})

        # Create a new product entry
        product = Products_table(
            product_name=product_name,
            product_description=product_description,
            product_category=product_category,
            product_subcategory=product_subcategory,
            product_quantity=product_quantity,
            quantity_unit=quantity_unit,
            product_price=product_price,
            employee=user
        )
        product.save()

        # Save product image if uploaded
        if product_photo:
            ProductImage.objects.create(product=product, image=product_photo)

        return redirect('productslist')

    return render(request, 'addproducts.html', {'username': user.username})



@csrf_exempt
def validate_dairy_image(request):
    """
    View function to handle dairy image validation requests
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            is_valid, message = validate_dairy_image_content(image_file)
            return JsonResponse({
                'valid': is_valid,
                'message': message
            })
        except Exception as e:
            return JsonResponse({
                'valid': False,
                'message': f"Error processing image: {str(e)}"
            })
    return JsonResponse({
        'valid': False,
        'message': "No image file provided"
    })

def validate_dairy_image_content(image_file):
    """
    Helper function to validate if the image contains dairy products using Google Cloud Vision API
    """
    try:
        # Create credentials and client
        client = vision.ImageAnnotatorClient()

        # Read the image file
        content = image_file.read()
        image = vision.Image(content=content)

        # Perform detection with multiple feature types
        response = client.annotate_image({
            'image': image,
            'features': [
                {'type_': vision.Feature.Type.LABEL_DETECTION},
                {'type_': vision.Feature.Type.OBJECT_LOCALIZATION},
                {'type_': vision.Feature.Type.TEXT_DETECTION}
            ]
        })

        # Define dairy-related keywords
        dairy_keywords = {
            'milk', 'dairy', 'cheese', 'yogurt', 'butter', 'cream', 'curd', 
            'ghee', 'paneer', 'buttermilk', 'whey', 'dairy product'
        }

        # Process labels
        detected_labels = set()
        high_confidence_matches = set()
        
        for label in response.label_annotations:
            label_text = label.description.lower()
            detected_labels.add(label_text)
            
            # Check for dairy-related terms with confidence threshold
            if any(keyword in label_text for keyword in dairy_keywords) and label.score >= 0.6:
                high_confidence_matches.add(f"{label_text} ({label.score:.2%})")

        # Process objects
        for object_ in response.localized_object_annotations:
            obj_name = object_.name.lower()
            detected_labels.add(obj_name)
            
            if any(keyword in obj_name for keyword in dairy_keywords) and object_.score >= 0.6:
                high_confidence_matches.add(f"{obj_name} ({object_.score:.2%})")

        # Process text
        if response.text_annotations:
            text = response.text_annotations[0].description.lower()
            words = text.split()
            
            # Look for dairy-related terms in text
            for word in words:
                if any(keyword in word for keyword in dairy_keywords):
                    detected_labels.add(word)

        # Decision logic
        if high_confidence_matches:
            return True, f"Validated as dairy product: {', '.join(high_confidence_matches)}"
        elif any(keyword in label for keyword in dairy_keywords for label in detected_labels):
            return True, "Validated as dairy-related product"
        else:
            return False, "Please upload an image that clearly shows dairy products"

    except Exception as e:
        return False, f"Error validating image: {str(e)}"




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminproductslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session

    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id

        # Get the search query and selected category from the GET request
        search_query = request.GET.get('search', '').strip()
        selected_category = request.GET.get('product_category', '').strip()

        # Start with a base query for active products
        products = Products_table.objects.all().order_by('product_name')

        # Apply search filter if a search query is provided
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        # Apply category filter if a category is selected
        if selected_category:
            products = products.filter(product_category=selected_category)

        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered products to the template
            'search_query': search_query,  # Retain the search query in the input field
            'selected_category': selected_category,  # Retain the selected category
        }

        return render(request, 'adminproductslist.html', context)

    else:
        return redirect('login')  # Redirect to login if no user is logged in

    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def productslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        # Get the search query from the GET request (if any)
        search_query = request.GET.get('search', '')
        selected_category = request.GET.get('product_category', '')  # Selected category
        
        # Base query: Filter products added by the logged-in user
        products = Products_table.objects.filter(
            employee_id=user_id  # Use employee_id instead of added_by
        ).select_related('employee').order_by('product_name')
        
        # Apply additional filters based on search query and selected category
        if search_query:
            products = products.filter(product_name__icontains=search_query)
        
        if selected_category:
            products = products.filter(product_category=selected_category)

        # Fetch distinct categories for products added by the logged-in user
        categories = Products_table.objects.filter(
            employee_id=user_id
        ).values_list('product_category', flat=True).distinct()

        
        
        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to retain the input value in the search bar
            'selected_category': selected_category,  # Pass the selected category to retain the selection in the dropdown
            'categories': categories,  # Pass the categories to the template
        }
        
        return render(request, 'productslist.html', context)
    
    else:
        return redirect('login')  # Redirect to login if no user is logged in


    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def custproductslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session

    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id

        search_query = request.GET.get('search', '')  # Get the search query from the GET request
        selected_category = request.GET.get('product_category', '')  # Selected category

        # Fetch all products filtered by status
        products = Products_table.objects.filter(status=True).order_by('product_name')

        # Apply search filter if search query is provided
        if search_query:
            products = products.filter(product_name__icontains=search_query)

        # Apply category filter if a category is selected
        if selected_category:
            products = products.filter(product_category=selected_category)

        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to the template (optional for retaining input value)
            'selected_category': selected_category,  # Pass the selected category to retain its value
        }
        return render(request, 'custproductslist.html', context)

    else:
        return redirect('login')  # Redirect to login if no user is logged in



@csrf_exempt
def image_search(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_searcher = ImageSearcher()
            best_match, products = image_searcher.search_products(request.FILES['image'])
            
            if products:
                # Return success with matching products
                return JsonResponse({
                    'success': True,
                    'match': best_match,
                    'products': [
                        {
                            'id': p.product_id,
                            'name': p.product_name,
                            'description': p.product_description,
                            'category': p.product_category,
                            'price': str(p.product_price),
                            'images': [img.image.url for img in p.images.all()]
                        } for p in products[:10]  # Limit to top 10 matches
                    ]
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No matching products found'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def productdetails(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session

    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in

    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Products_table, product_id=product_id)
        images = product.images.all()  # Get associated images

        # Determine product availability status
        product_status = "In Stock" if product.product_quantity > 0 else "Out of Stock"

        # Wishlist addition logic
        if 'add_to_wishlist' in request.POST:
            wishlist_item, created = WishlistItem.objects.get_or_create(user=user, product=product)

            if created:
                messages.success(request, f'{product.product_name} added to wishlist successfully!')
            else:
                messages.info(request, f'{product.product_name} is already in your wishlist.')

        # Fetch feedbacks for the current product
        feedbacks = Feedback_table.objects.filter(product=product).order_by('-created_at')

        context = {
            'product': product,
            'images': images,
            'username': user.username,  # Pass the username to the template
            'feedbacks': feedbacks,  # Pass feedbacks to the template
            'product_status': product_status,  # Pass product status to the template
        }
        return render(request, 'productdetails.html', context)

    # If not a POST request, simply pass the user's username
    context = {
        'username': user.username,
    }
    return render(request, 'productdetails.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def wishlist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = get_object_or_404(Users_table, user_id=user_id)  # Fetch the user object using user_id

        if request.method == 'POST':
            print("POST data:", request.POST)  # Debugging the entire POST data
            product_id = request.POST.get('remove_product_id')  # Get product ID
            print("Product ID received in POST request:", product_id)

            if product_id:
                try:
                    wishlist_item = WishlistItem.objects.filter(user=user, product_id=product_id).first()
                    if wishlist_item:
                        wishlist_item.delete()
                        print("Wishlist item deleted successfully.")
                    else:
                        print("Wishlist item not found for this user.")
                except Exception as e:
                    print("Error while deleting wishlist item:", e)
            else:
                print("No product ID provided in the POST request.")

            return redirect('wishlist')

        wishlist_items = WishlistItem.objects.filter(user=user).select_related('product')
        
        # Add print statements to debug the product details
        for item in wishlist_items:
            print(f"Wishlist Item: {item.product.product_name}, Product ID: {item.product.product_id}")
        
        return render(request, 'wishlist.html', {'wishlist': wishlist_items, 'username': user.username})
    else:
        return redirect('login')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
            products = Products_table.objects.filter(employee_id=user_id)

        context = {
            'username': user.username,  # Pass the username to the template
            'products': products,       # Pass the filtered or all products to the template
            'search_query': search_query,  # Pass the search query to retain the input value in the search bar
        }

        return render(request, 'editproduct.html', context)

    else:
        return redirect('login')  # Redirect to login if no user is logged in

    

def updateproduct(request, product_id):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in
    
    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
    product = Products_table.objects.get(product_id=product_id)
    images = ProductImage.objects.filter(product=product)

    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.product_description = request.POST.get('product_description')
        product.product_category = request.POST.get('product_category')  # Updated for category
        product.product_subcategory = request.POST.get('product_subcategory')  # Updated for category
        product.product_quantity = request.POST.get('product_quantity')
        product.quantity_unit = request.POST.get('quantity_unit')
        product.product_price = request.POST.get('product_price')
        product.save()

        # Handle new image upload
        product_photo = request.FILES.get('product_images')  # Ensure this matches your input name
        if product_photo:
            ProductImage.objects.filter(product=product).delete()  # Delete all old images
            ProductImage.objects.create(product=product, image=product_photo)  # Add new image

        return redirect('productslist')  # Redirect to product list after update

    context = {
        'username': user.username,
        'product': product,
        'images': images,
    }
    return render(request, 'updateproduct.html', context)



def deleteproduct(request, product_id):
    product = get_object_or_404(Products_table, product_id=product_id)
    product.status = False  # Set status to 0 (deleted)
    product.save()
    return redirect('productslist')  # Redirect to the product listing page

def restoreproduct(request, product_id):
    product = get_object_or_404(Products_table, product_id=product_id)
    product.status = True  # Set status to 1 (active)
    product.save()
    return redirect('productslist')  # Redirect to the product listing page



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminproductstock(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch all products from the Products_table
        products = Products_table.objects.all()
        
        # Pass both the username and products to the template
        context = {
            'username': user.username,
            'products': products
        }
        return render(request, 'adminproductstock.html', context)
    else:
        # Redirect to login if user is not authenticated
        return redirect('login')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmerproductstock(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch all products from the Products_table
        products = Products_table.objects.filter(employee_id=user_id)
        
        # Pass both the username and products to the template
        context = {
            'username': user.username,
            'products': products
        }
        return render(request, 'farmerproductstock.html', context)
    else:
        # Redirect to login if user is not authenticated
        return redirect('login')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def productstock(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch all products from the Products_table
        products = Products_table.objects.filter(employee_id=user_id)
        
        # Pass both the username and products to the template
        context = {
            'username': user.username,
            'products': products
        }
        return render(request, 'productstock.html', context)
    else:
        # Redirect to login if user is not authenticated
        return redirect('login')

# def preorder(request):
#     if request.method == "POST":
#         # Handle form submission
#         user_id = request.session.get('user_id')
#         if not user_id:
#             messages.error(request, "Please log in to place a pre-order.")
#             return redirect("login")

#         user = Users_table.objects.get(user_id=user_id)
#         product_id = request.POST.get("product_id")
#         product = get_object_or_404(Products_table, product_id=product_id)

#         # Get form data and validate
#         quantity = int(request.POST.get("quantity"))
#         date_of_delivery = request.POST.get("date_of_delivery")
#         additional_notes = request.POST.get("additional_notes", "")

#         if quantity > product.product_quantity:
#             messages.error(request, "Quantity exceeds available stock.")
#             return redirect("preorder")  # Or reload with context for errors

#         # Create new pre-order
#         PreOrder.objects.create(
#             product=product,
#             quantity=quantity,
#             date_of_delivery=date_of_delivery,
#             additional_notes=additional_notes,
#             user=user
#         )

#         messages.success(request, f"Your pre-order for {product.product_name} was successfully placed!")
#         # Redirect to the same page to display success message
#         return redirect(request.path + '?product_id=' + str(product_id))

#     # GET request to display the form
#     product_id = request.GET.get("product_id")
#     if not product_id:
#         messages.error(request, "Product not found.")
#         return redirect("custproductslist")

#     product = get_object_or_404(Products_table, product_id=product_id)
#     return render(request, "preorder.html", {"product": product})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def preorder(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session

    if not user_id:
        messages.error(request, "Please log in to place a pre-order.")
        return redirect("login")  # Redirect to login if no user is logged in

    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id

    if request.method == "POST":
        # Handle form submission
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Products_table, product_id=product_id)

        # Get form data and validate
        try:
            quantity = int(request.POST.get("quantity"))
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid quantity.")
            return redirect(request.path + f'?product_id={product_id}')

        date_of_delivery = request.POST.get("date_of_delivery")
        additional_notes = request.POST.get("additional_notes", "")

        if quantity > product.product_quantity:
            messages.error(request, "Quantity exceeds available stock.")
            return redirect(request.path + f'?product_id={product_id}')  # Reload page with error message
        
        # Fetch the farmer from the product's `farmer_id`
        farmer = get_object_or_404(Users_table, user_id=product.employee_id)

        # Create new pre-order
        PreOrder.objects.create(
            product=product,
            quantity=quantity,
            date_of_delivery=date_of_delivery,
            additional_notes=additional_notes,
            user=user,
            farmer=farmer
        )

        messages.success(request, f"Your pre-order for {product.product_name} was successfully placed!")
        # Redirect to the same page to display success message
        return redirect(request.path + f'?product_id={product_id}')

    # GET request to display the form
    product_id = request.GET.get("product_id")
    if not product_id:
        messages.error(request, "Product not found.")
        return redirect("custproductslist")

    product = get_object_or_404(Products_table, product_id=product_id)

    # Pass the product details and username to the template
    context = {
        "product": product,
        "username": user.username,  # Pass the username to the template
    }
    return render(request, "preorder.html", context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def preorderlisting(request):
    # Get user_id from the session
    user_id = request.session.get('user_id')

    if user_id:  # Check if user_id exists in the session
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        preorders = PreOrder.objects.filter(user_id=user_id)  # Fetch pre-orders for the user
        
        context = {
            'username': user.username,  # Pass the username to the template
            'preorders': preorders,  # Pass pre-orders to the template
        }
        return render(request, 'preorderlisting.html', context)
    else:
        return redirect('login')  # Redirect to login if user_id is not in the session
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def preorderfarm(request):
    # Get the logged-in farmer's ID from the session
    farmer_id = request.session.get('user_id')

    if farmer_id:  # Check if the farmer is logged in
        # Fetch preorders where the logged-in farmer is the owner of the products
        preorders = PreOrder.objects.filter(farmer_id=farmer_id)

        # Pass the preorders to the template
        context = {
            'username': request.session.get('username'),  # Pass username for display
            'preorders': preorders,  # Filtered preorders for the farmer
        }
        return render(request, 'preorderfarm.html', context)
    else:
        # Redirect to login if farmer_id is not found in the session
        return redirect('login')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminanimalslist(request):
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
        return render(request, 'adminanimalslist.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def animalslist(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        
        # Fetch all animals with their related images
        animals = Animals_table.objects.filter(added_by=user_id).prefetch_related('images').all()  # Use the correct related name
        
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



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addanimal(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in
    
    user = get_object_or_404(Users_table, pk=user_id)  # Fetch the user object using user_id
    
    if request.method == 'POST':
        # Fetch form data
        animal_name = request.POST.get('animal_name')
        breed = request.POST.get('breed')
        date_of_birth = request.POST.get('date_of_birth') or None
        gender = request.POST.get('gender')
        milk_capacity = request.POST.get('milk_capacity') or None

        # Create a new animal record
        animal = Animals_table.objects.create(
            animal_name=animal_name,
            breed=breed,
            date_of_birth=date_of_birth,
            gender=gender,
            milk_capacity=milk_capacity,
            added_by=user  # Assign the user instance
        )

        # Handle multiple file uploads
        for img in request.FILES.getlist('animal_images'):
            AnimalImages.objects.create(animal=animal, animal_image=img)
        
        return redirect('animalslist')  # Redirect after successful addition
    
    context = {'username': user.username}  # Pass username to template
    return render(request, 'addanimal.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminanimaldetails(request, animal_id): 
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    # Initialize context dictionary
    context = {}

    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context['username'] = user.username  # Pass the username to the template
    else:
        return redirect('login')  # Redirect to login if no user is logged in

    # Fetch the specific animal with related images
    animal = get_object_or_404(Animals_table.objects.prefetch_related('images'), animal_id=animal_id)

    # Calculate the age of the animal
    if animal.date_of_birth:
        current_date = timezone.now().date()  # Get the current date
        animal_age_years = (current_date - animal.date_of_birth).days // 365  # Calculate age in years
        animal.age_in_years = animal_age_years  # Add a custom attribute to hold the age

    # Pass the animal details to the context
    context['animal'] = animal

    return render(request, 'adminanimaldetails.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def animaldetails(request, animal_id): 
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    # Initialize context dictionary
    context = {}

    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context['username'] = user.username  # Pass the username to the template
    else:
        return redirect('login')  # Redirect to login if no user is logged in

    # Fetch the specific animal with related images
    animal = get_object_or_404(Animals_table.objects.prefetch_related('images'), animal_id=animal_id)

    # Calculate the age of the animal
    if animal.date_of_birth:
        current_date = timezone.now().date()  # Get the current date
        animal_age_years = (current_date - animal.date_of_birth).days // 365  # Calculate age in years
        animal.age_in_years = animal_age_years  # Add a custom attribute to hold the age

    # Pass the animal details to the context
    context['animal'] = animal

    return render(request, 'animaldetails.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def updateanimal(request, animal_id):
    user_id = request.session.get('user_id')  # Retrieve user_id from session
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in
    
    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object
    animal = get_object_or_404(Animals_table, animal_id=animal_id)
    images = AnimalImages.objects.filter(animal=animal)
    
    if request.method == 'POST':
        animal.animal_name = request.POST.get('animal_name', animal.animal_name)
        animal.breed = request.POST.get('breed', animal.breed)
        date_of_birth_str = request.POST.get('date_of_birth')
        if date_of_birth_str:
            animal.date_of_birth = parse_date(date_of_birth_str)
        animal.gender = request.POST.get('gender', animal.gender)
        animal.milk_capacity = request.POST.get('milk_capacity', animal.milk_capacity)
        
        if request.FILES.get('animal_image'):
            images.delete()  # Delete all existing images
            new_image = request.FILES['animal_image']
            AnimalImages.objects.create(animal=animal, animal_image=new_image)
        
        animal.save()
        return redirect('animaldetails', animal_id=animal.animal_id)  
    
    return render(request, 'updateanimal.html', {'animal': animal, 'images': images, 'username': user.username})



def delete_animal(request, animal_id):
    animal = get_object_or_404(Animals_table, pk=animal_id)
    animal.status = False  # Deactivate the animal
    animal.save()
    # messages.success(request, f"{animal.animal_name} has been deactivated.")
    return redirect('animaldetails', animal_id=animal_id)

def restore_animal(request, animal_id):
    animal = get_object_or_404(Animals_table, pk=animal_id)
    animal.status = True  # Reactivate the animal
    animal.save()
    # messages.success(request, f"{animal.animal_name} has been reactivated.")
    return redirect('animaldetails', animal_id=animal_id)
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def animal_health_status(request, animal_id):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in

    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object
    animal = get_object_or_404(Animals_table, animal_id=animal_id)  # Fetch the animal
    health_records = AnimalHealth_table.objects.filter(animal=animal)  # Fetch health records

    context = {
        'username': user.username,
        'animal': animal,
        'health_records': health_records,
    }
    
    return render(request, 'animal_health_status.html', context)



def add_health_record(request, animal_id):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if request.method == "POST":
        # Retrieve data from the form
        checkup_date = request.POST['checkup_date']
        health_status = request.POST.getlist('health_status')  # Multiple selections
        vaccinations = request.POST.getlist('vaccinations')
        treatment_details = request.POST['treatment_details']
        veterinarian_name = request.POST['veterinarian_name']
        next_checkup_date = request.POST['next_checkup_date']

        # Create a new health record instance
        health_record = AnimalHealth_table(
            animal_id=animal_id,
            checkup_date=checkup_date,
            health_status="; ".join(health_status),  # Joining multiple selections into a string
            vaccinations ="; ".join(vaccinations),
            treatment_details="; ".join(treatment_details),
            veterinarian_name=veterinarian_name,
            next_checkup_date=next_checkup_date,
            added_by_id=user_id  # Set the current user
        )
        
        health_record.save()  # Save the health record

        # messages.success(request, 'Health record added successfully!')
        return redirect('animal_health_status', animal_id=animal_id)

    return render(request, 'add_health_record.html', {'animal_id': animal_id})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_health_record(request, health_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Redirect to login if no user is logged in

    user = Users_table.objects.get(user_id=user_id)  # Fetch the user object
    health_record = get_object_or_404(AnimalHealth_table, health_id=health_id)

    if request.method == "POST":
        # Update health record
        health_record.checkup_date = request.POST['checkup_date']
        health_record.health_status = request.POST['health_status']
        health_record.vaccinations = request.POST['vaccinations']
        health_record.treatment_details = request.POST['treatment_details']
        health_record.veterinarian_name = request.POST['veterinarian_name']
        health_record.next_checkup_date = request.POST['next_checkup_date']
        health_record.save()

        messages.success(request, 'Health record updated successfully!')
        return redirect('animal_health_status', animal_id=health_record.health_id)

    context = {
        'health_record': health_record,
        'username': user.username,  # Pass the username to the template
    }
    return render(request, 'update_health_record.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminmilkdetails(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch animals and related images
        animals = Animals_table.objects.prefetch_related('images').all()
        
        # Prepare context with username and animals
        context = {
            'username': user.username,  # Pass the username
            'animals': animals,         # Pass the animals
        }
        
        # Render the milkdetails.html page with context
        return render(request, 'adminmilkdetails.html', context)
    
    else:
        # If user is not authenticated, redirect to the login page
        return redirect('login')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def milkdetails(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch animals and related images
        animals = Animals_table.objects.prefetch_related('images').filter(added_by=user_id)
        
        # Prepare context with username and animals
        context = {
            'username': user.username,  # Pass the username
            'animals': animals,         # Pass the animals
        }
        
        # Render the milkdetails.html page with context
        return render(request, 'milkdetails.html', context)
    
    else:
        # If user is not authenticated, redirect to the login page
        return redirect('login')


""" # Add a product to the cart
def add_to_cart(request):
    if request.method == 'POST':
        # Get product_id from the POST data
        product_id = request.POST.get('product_id')
        # Get the quantity from the form submission (input field)
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not specified

        # Fetch product and user
        product = get_object_or_404(Products_table, pk=product_id)
        user_id = request.session['user_id']
        user = get_object_or_404(Users_table, pk=user_id)

        # Check if the product is already in the cart
        cart_item, created = Cart.objects.get_or_create(
            user=user,  # Assuming the user is logged in
            product=product,
            defaults={'quantity': quantity}  # Default quantity if the item is being added for the first time
        )

        if not created:  # If the item already exists in the cart, just update the quantity
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('viewcart')  # Redirect to the cart view after adding the item

# View the cart
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewcart(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch cart items for the logged-in user
        cart_items = Cart.objects.filter(user=user)
        
        # Calculate the total price of the cart
        total_price = sum([item.get_total_price() for item in cart_items])
        
        # Pass the username, cart items, and total price to the template
        context = {
            'username': user.username,  # User's username
            'cart_items': cart_items,    # Cart items for the user
            'total_price': total_price   # Total price of the items in the cart
        }
        return render(request, 'viewcart.html', context)
    
    else:
        # Redirect to login if no user is logged in
        return redirect('login')


# Update the quantity of a product in the cart
def update_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_id)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()

        return redirect('viewcart')

# Delete a product from the cart
def delete_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, pk=cart_id)
    cart_item.delete()
    return redirect('viewcart') """



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request):
    if request.method == 'POST':
        # Get product_id from the POST data
        product_id = request.POST.get('product_id')
        # Get the quantity from the form submission (input field)
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not specified

        # Fetch product and user
        product = get_object_or_404(Products_table, pk=product_id)
        user_id = request.session['user_id']
        user = get_object_or_404(Users_table, pk=user_id)

        # Check if the product is already in the cart
        cart_item, created = Cart.objects.get_or_create(
            user=user,  # Assuming the user is logged in
            product=product,
            defaults={'quantity': quantity}  # Default quantity if the item is being added for the first time
        )

        if not created:  # If the item already exists in the cart, just update the quantity
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('viewcart')  # Redirect to the cart view after adding the item


# View the cart
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewcart(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch cart items for the logged-in user
        cart_items = Cart.objects.filter(user=user)
        
        # Calculate the total price of the cart
        total_price = sum([item.get_total_price() for item in cart_items])
        
        # Pass the username, cart items, and total price to the template
        context = {
            'username': user.username,  # User's username
            'cart_items': cart_items,    # Cart items for the user
            'total_price': total_price   # Total price of the items in the cart
        }
        return render(request, 'viewcart.html', context)
    
    else:
        # Redirect to login if no user is logged in
        return redirect('login')



def update_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_id)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()

        return redirect('viewcart')

# Delete a product from the cart
def delete_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, pk=cart_id)
    cart_item.delete()
    return redirect('viewcart')


# def checkoutbilling(request):
#     user = Users_table.objects.get(user_id=request.session['user_id'])
    
#     if request.method == 'POST':
#         # Handle the form submission to add a new address
#         name = request.POST.get('name')
#         place = request.POST.get('place')
#         delivery_address = request.POST.get('delivery_address')
#         pincode = request.POST.get('pincode')
#         phone = request.POST.get('phone')
#         email = request.POST.get('email')

#         # Create and save the new address
#         new_address = Address_table.objects.create(
#             user=user,  # Assuming you have a relationship to Users_table
#             name=name,
#             place=place,
#             delivery_address=delivery_address,
#             pincode=pincode,
#             phone=phone,
#             email=email
#         )
#         messages.success(request, 'Address added successfully!')
#         return redirect('checkoutbilling')  # Redirect to the same page to show the updated list

#     addresses = Address_table.objects.filter(user=user)  # Fetch the addresses for the user

#     return render(request, 'checkoutbilling.html', {
#         'addresses': addresses,
#         'user_name': user.username,
#         'user_phone': user.phone,
#         'user_email': user.email
#     })

def checkoutbilling(request):
    user = Users_table.objects.get(user_id=request.session['user_id'])

    # Fetch user details
    user_name = user.username
    user_phone = user.phone
    user_email = user.email

    if request.method == 'POST':
        # Save billing details to session and proceed to order page
        request.session['billing_details'] = {
            'name': request.POST['username'],
            'phone': request.POST['phone'],
            'email': request.POST['email'],
            'place': request.POST['place'],
            'pincode': request.POST['pincode'],
            'delivery_address': request.POST['delivery_address']
        }
        return redirect('checkoutorder')  # Redirect to the second page

    return render(request, 'checkoutbilling.html', {
        'user_name': user_name,
        'user_phone': user_phone,
        'user_email': user_email
    })


# def checkoutorder(request):
#     user = Users_table.objects.get(user_id=request.session['user_id'])
#     user_cart = Cart.objects.filter(user=user)

#     # Calculate total price
#     total_price = sum([item.get_total_price() for item in user_cart])

#     # Retrieve billing details from session
#     billing_details = request.session.get('billing_details')

#     if request.method == 'POST':
#         # Complete order details
#         payment_method = request.POST['payment_method']

#         # Create the order
#         order = Order_table.objects.create(
#             user=user,
#             name=billing_details['name'],
#             phone=billing_details['phone'],
#             email=billing_details['email'],
#             place=billing_details['place'],
#             pincode=billing_details['pincode'],
#             delivery_address=billing_details['delivery_address'],
#             payment_method=payment_method,
#             total_price=total_price
#         )

#         # Create OrderItem instances for each item in the cart
#         for cart_item in user_cart:
#             OrderItem_table.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 price=cart_item.get_total_price()
#             )

#             # Remove from wishlist if the item is present
#             # WishlistItem.objects.filter(user=user, product=cart_item.product).delete()

#             # Reduce product stock and save
#             cart_item.product.product_quantity -= cart_item.quantity
#             cart_item.product.save()

#             # Check if product quantity is below 2 and create a notification
#             if cart_item.product.product_quantity < 2:
#                 Notifications_table.objects.create(
#                     message=f"Alert: Stock for '{cart_item.product.product_name}' is critically low (below 2 units). Immediate restocking is required.",
#                 )

#         # Clear the user's cart after placing the order
#         user_cart.delete()

#         return redirect('ordersummary', order_id=order.id)

#     return render(request, 'checkoutorder.html', {
#         'user_cart': user_cart,
#         'total_price': total_price,
#         'billing_details': billing_details
#     })


# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def checkoutorder(request):
    user = Users_table.objects.get(user_id=request.session['user_id'])
    user_cart = Cart.objects.filter(user=user)
    total_price = sum([item.get_total_price() for item in user_cart])
    billing_details = request.session.get('billing_details')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # Create order based on payment method
        if payment_method == "online":
            # Process Razorpay payment
            payment_id = request.POST.get('payment_id')
            try:
                # Verify the payment
                razorpay_client.payment.fetch(payment_id)
            except razorpay.errors.RazorpayError:  # Catch all Razorpay errors
                return JsonResponse({"error": "Payment verification failed"})

            # If payment is successful, create the order
            order = Order_table.objects.create(
                user=user,
                name=billing_details['name'],
                phone=billing_details['phone'],
                email=billing_details['email'],
                place=billing_details['place'],
                pincode=billing_details['pincode'],
                delivery_address=billing_details['delivery_address'],
                payment_method="online",
                total_price=total_price
            )
        else:  # For Cash on Delivery
            order = Order_table.objects.create(
                user=user,
                name=billing_details['name'],
                phone=billing_details['phone'],
                email=billing_details['email'],
                place=billing_details['place'],
                pincode=billing_details['pincode'],
                delivery_address=billing_details['delivery_address'],
                payment_method="cod",
                total_price=total_price
            )

        for cart_item in user_cart:
            OrderItem_table.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.get_total_price()
            )
            cart_item.product.product_quantity -= cart_item.quantity
            cart_item.product.save()

            if cart_item.product.product_quantity < 2:
                Notifications_table.objects.create(
                    message=f"Alert: Stock for '{cart_item.product.product_name}' is critically low (below 2 units). Immediate restocking is required.",
                    product=cart_item.product,  # Link to the product
                    farmer=user  # Link to the user who added the product
                )

        # Auto-assign delivery agent
        DeliveryAssignment.auto_assign_delivery_agent(order)

        user_cart.delete()

        # Redirect for Razorpay
        if payment_method == "online":
            return redirect('ordersummary', order_id=order.id)

        return redirect('ordersummary', order_id=order.id)

    return render(request, 'checkoutorder.html', {
        'user_cart': user_cart,
        'total_price': total_price,
        'billing_details': billing_details,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID
    })



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminstocknotification(request):
    # Fetch unread notifications
    notifications = Notifications_table.objects.filter(is_read=False).order_by('-created_at')
    
    # Get the count of unread notifications
    unread_count = notifications.count()

    # Mark all fetched notifications as read
    notifications.update(is_read=True)
    
    # Fetch all notifications (to display both read and unread)
    all_notifications = Notifications_table.objects.all().order_by('-created_at')
    
    return render(request, 'adminstocknotification.html', {
        'notifications': all_notifications,
        'unread_count': unread_count  # Pass the unread count to the template
    })



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def stocknotification(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')
    
    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)
        
        # Fetch products added by the logged-in user (assuming Products_table has a reference to the user)
        user_products = Products_table.objects.filter(employee=user)
        
        # Fetch all notifications related to the logged-in user's products
        notifications = Notifications_table.objects.filter(
            product__in=user_products  # Only get notifications related to the products of this user
        ).order_by('-created_at')
        
        # Get the count of unread notifications
        unread_count = notifications.filter(is_read=False).count()
        
        # Mark all fetched notifications as read
        notifications.filter(is_read=False).update(is_read=True)
        
        # Prepare the context for rendering the template
        context = {
            'notifications': notifications,
            'unread_count': unread_count,  # Pass the unread count to the template
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'stocknotification.html', context)
    else:
        # Redirect to login if no user is logged in
        return redirect('login')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ordersummary(request, order_id):
    # order_id = request.GET.get('order_id')
    # if not order_id:
    #     return redirect('orderhistory')

    # Fetch the specific order using the order_id
    order = get_object_or_404(Order_table, id=order_id)

    # Fetch the related items from OrderItem_table for this order
    order_items = OrderItem_table.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items,  # Passing the OrderItem instances to the template
        'total_price': order.total_price,
        'payment_method': order.get_payment_method_display(),
    }

    return render(request, 'ordersummary.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orderhistory(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')  

    if user_id:
        # Fetch the user object using user_id
        user = Users_table.objects.get(user_id=user_id)

        # Fetch all orders placed by the logged-in user, ordered by most recent
        orders = Order_table.objects.filter(user=user).order_by('-order_date')

        # Pass both orders and username to the template
        context = {
            'username': user.username,
            'orders': orders,
        }

        return render(request, 'orderhistory.html', context)
    else:
        # Redirect to login if no user is logged in
        return redirect('login')
    

def cancelorder(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order_table, id=order_id)

        # Restock the products
        order_items = OrderItem_table.objects.filter(order=order)
        for item in order_items:
            product = item.product
            product.product_quantity += item.quantity  # Restock the quantity
            product.save()

        # Update order status to canceled
        order.status = 'Cancelled'  # Assuming you have a status field in Order_table
        order.save()

        # Add a success message
        messages.success(request, 'Order has been canceled and items have been restocked.')

        # Redirect to the order history page
        return redirect('orderhistory')

    # If the request is not POST, redirect back to order history
    return redirect('orderhistory')



# Check if the user has any pending orders
def pendingorders(request):
    user_id = request.session.get('user_id')
    if user_id:
        pending_orders = Order_table.objects.filter(user_id=user_id, status='pending')
        return JsonResponse({'has_pending_orders': pending_orders.exists()})
    return JsonResponse({'has_pending_orders': False})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def orderdetails(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')

    if user_id:
        # Fetch the farm owner object using user_id
        farm_owner = Users_table.objects.get(user_id=user_id)

        # Fetch all products added by the logged-in farm owner
        products = Products_table.objects.filter(employee_id=farm_owner)

        # Fetch all orders that contain the products added by the farm owner
        orders = Order_table.objects.filter(order_items__product__in=products).distinct().order_by('-order_date')

        # Pass both orders and username to the template
        context = {
            'username': farm_owner.username,
            'orders': orders,
        }

        return render(request, 'orderdetails.html', context)
    else:
        # Redirect to login if no user is logged in
        return redirect('login')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deliveryassigns(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        try:
            user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
            orders = Order_table.objects.all().order_by('-order_date')  # Fetch all orders
            context = {
                'username': user.username,  # Pass the username to the template
                'orders': orders,  # Pass the orders to the template
            }
            return render(request, 'deliveryassigns.html', context)
        except Users_table.DoesNotExist:
            return redirect('login')  # Redirect to login if user doesn't exist
    else:
        return redirect('login')  # Redirect to login if no user is logged in



def get_employees(request):
    if request.method == "GET":
        # Fetch users with role='employee' including phone number
        employees = Users_table.objects.filter(role='employee').values('user_id', 'username', 'phone')
        return JsonResponse({"employees": list(employees)})
    return JsonResponse({"employees": []})


@csrf_exempt
def assign_delivery(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("id")
        employee_id = data.get("deliveryboy")
        action = data.get("action", "assign")

        try:
            order = Order_table.objects.get(id=order_id)

            if action == "assign":
                employee = Users_table.objects.get(user_id=employee_id)
                order.deliveryboy = employee
                order.status = "Confirmed"
            else:  # unassign
                order.deliveryboy = None
                order.status = "Pending"  # or whatever your initial status is
            
            order.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deliveryboyassigns(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')

    if user_id:
        try:
            # Fetch the user object using user_id
            user = Users_table.objects.get(user_id=user_id)

            # Fetch all orders assigned to this delivery boy with specific statuses
            assigned_orders = Order_table.objects.filter(
                deliveryboy=user, 
                status__in=['Pending', 'Confirmed', 'Shipped', 'Out']
            ).order_by('-order_date')

            context = {
                'username': user.username,  # Pass the username to the template
                'assigned_orders': assigned_orders,  # Pass assigned orders to the template
            }
            return render(request, 'deliveryboyassigns.html', context)
        except Users_table.DoesNotExist:
            # Handle case where user does not exist (e.g., invalid session data)
            return redirect('login')
    else:
        # Redirect to login if no user is logged in
        return redirect('login')
    


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deliverydetailsall(request):
    # Retrieve user_id from the session
    user_id = request.session.get('user_id')

    if user_id:
        try:
            # Fetch the user object using user_id
            user = Users_table.objects.get(user_id=user_id)

            # Fetch all orders assigned to this delivery boy
            assigned_orders = Order_table.objects.filter(deliveryboy=user).order_by('-order_date')

            context = {
                'username': user.username,  # Pass the username to the template
                'assigned_orders': assigned_orders,  # Pass assigned orders to the template
            }
            return render(request, 'deliverydetailsall.html', context)
        except Users_table.DoesNotExist:
            # Handle case where user does not exist (e.g., invalid session data)
            return redirect('login')
    else:
        # Redirect to login if no user is logged in
        return redirect('login')



def generate_qr_code(request, order_id):
    """Dynamically generates a QR code for order confirmation."""
    order = get_object_or_404(Order_table, id=order_id)

    if order.status != "Out":
        return HttpResponse("QR Code is only available when the order is 'Out for Delivery'.", status=400)

    confirmation_url = f"http://127.0.0.1:8000/confirm-delivery/{order_id}/"  # Replace with production URL
    qr = qrcode.make(confirmation_url)
    
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")



def verify_qr(request, order_id):
    """Verify QR Code and mark order as delivered"""
    order = get_object_or_404(Order_table, id=order_id)

    if order.status == "out_for_delivery":
        order.status = "delivered"
        order.is_verified = True
        order.save()
        return JsonResponse({"message": "Order successfully delivered!"})
    else:
        return JsonResponse({"error": "Invalid Order Status"}, status=400)
    


def scan_qr(request):
    """Render QR scanner page"""
    return render(request, 'qr_scanner.html')



@csrf_exempt  # Add this decorator
def confirm_delivery(request, order_id):
    """Mark order as delivered when QR code is scanned."""
    if request.method == 'POST':
        order = get_object_or_404(Order_table, id=order_id)
        
        if order.status == "Out":
            order.status = "Delivered"
            order.save()
            
            # Create notification for customer
            Notifications_table.objects.create(
                message=f"Your order #{order.id} has been delivered successfully!",
                order=order,
                user=order.user
            )
            
            return HttpResponse("Order has been successfully marked as Delivered!")
        
        return HttpResponse("Invalid QR Code or Order is not Out for Delivery.", status=400)
    
    return HttpResponse("Invalid request method.", status=405)



@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('status')
            
            # Get the order and update its status
            order = Order_table.objects.get(id=order_id)
            order.status = new_status
            order.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



def get_order_tracking(request, order_id):
    try:
        order = Order_table.objects.get(id=order_id)
        
        # Map the status to tracking steps
        status_mapping = {
            'Placed': 'orderPlaced',
            'Confirmed': 'orderConfirmed',
            'Shipped': 'orderShipped',
            'Out': 'orderOut',
            'Delivered': 'orderDelivered'
        }
        
        current_status = status_mapping.get(order.status, 'orderPlaced')
        
        # Get tracking information with timestamps
        tracking_info = {
            'orderPlaced': order.created_at.strftime("%B %d, %Y %I:%M %p"),
            'orderConfirmed': order.updated_at.strftime("%B %d, %Y %I:%M %p") if order.status in ['Confirmed', 'Shipped', 'Out', 'Delivered'] else None,
            'orderShipped': order.updated_at.strftime("%B %d, %Y %I:%M %p") if order.status in ['Shipped', 'Out'] else None,
            'orderOut': order.updated_at.strftime("%B %d, %Y %I:%M %p") if order.status in ['Out', 'Delivered'] else None,
            'orderDelivered': order.updated_at.strftime("%B %d, %Y %I:%M %p") if order.status == 'Delivered' else None
        }

        return JsonResponse({
            'success': True,
            'status': current_status,
            'tracking_info': tracking_info
        })
    except Order_table.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def diseasedetection(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'diseasedetection.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in 



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deliverynotifications(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from the session
    if user_id:
        user = Users_table.objects.get(user_id=user_id)  # Fetch the user object using user_id
        context = {
            'username': user.username,  # Pass the username to the template
        }
        return render(request, 'deliverynotifications.html', context)
    else:
        return redirect('login')  # Redirect to login if no user is logged in



"""def login(request):
    return render(request, 'login.html')

def registration(request):
    return render(request, 'registration.html')

def addproducts(request): 
    return render(request, 'addproducts.html') 

def productslist(request):
    return render(request, 'login.html')  """









