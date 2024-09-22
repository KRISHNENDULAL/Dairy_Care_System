from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class Users_table(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    password = models.CharField(max_length=128)  # For hashed password storage
    
    ROLES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='customer')
    
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    """def save(self, *args, **kwargs):
        if not self.pk or not self.password.startswith('pbkdf2_sha256$'):  # Ensures the password is hashed only once
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)  """

    def __str__(self):
        return self.username
    

class Products_table(models.Model):
    product_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    product_name = models.CharField(max_length=255)  # Product Name
    product_description = models.TextField()           # Product Description
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity
    quantity_unit = models.CharField(max_length=20)   # Unit of measurement
    status = models.BooleanField(default=True)         # 1 if available, else 0
    added_at = models.DateTimeField(auto_now_add=True) # Timestamp for when the product is added
    updated_at = models.DateTimeField(auto_now=True)   # Timestamp for when the product is last updated

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    image_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    product = models.ForeignKey(Products_table, related_name='images', on_delete=models.CASCADE)  # Link to Products_table
    image = models.ImageField(upload_to='product_images/', null=False)  # Upload path for product images
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the image is added

    def __str__(self):
        return f"Image {self.image_id} for {self.product.product_name}"
    


  