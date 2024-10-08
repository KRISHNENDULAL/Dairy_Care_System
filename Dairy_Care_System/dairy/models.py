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
    
    # def save(self, *args, **kwargs):
    #     # Only hash the password if it has been set/changed
    #     if self.pk is None or self.password and not self.password.startswith('pbkdf2_sha256$'):
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.username  
    

class Products_table(models.Model):
    product_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    product_name = models.CharField(max_length=255)  # Product Name
    product_description = models.TextField()           # Product Description
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity
    quantity_unit = models.CharField(max_length=20)   # Unit of measurement
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price field
    employee = models.ForeignKey(Users_table, on_delete=models.CASCADE)
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
    

class WishlistItem(models.Model):
    user = models.ForeignKey(Users_table, on_delete=models.CASCADE)
    product = models.ForeignKey(Products_table, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"
    


class Animals_table(models.Model):
    animal_id = models.AutoField(primary_key=True)
    animal_name = models.CharField(max_length=100)
    animal_category = models.CharField(max_length=50)  # E.g., Cow, Buffalo, etc.
    breed = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)  # Gender of the animal
    milk_capacity = models.FloatField(blank=True, null=True)  # Milk capacity in liters per day
    added_by = models.ForeignKey(Users_table, on_delete=models.SET_NULL, null=True)  # Employee managing the animal
    status = models.BooleanField(default=True)  # Active or inactive
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.animal_name


# Animal Images Table (Multiple images can be associated with each animal)
class AnimalImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animals_table, related_name='images', on_delete=models.CASCADE)  # ForeignKey to the Animals_table
    animal_image = models.ImageField(upload_to='animal_images/')  # Image upload path
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Date when the image was uploaded

    def __str__(self):
        return f"Image for {self.animal.animal_name}"


class AnimalHealth_table(models.Model):
    health_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animals_table, related_name='health_records', on_delete=models.CASCADE)  # ForeignKey to the Animals_table
    checkup_date = models.DateField()  # Date of the health checkup
    health_status = models.TextField()  # Details about the current health status
    vaccinations = models.CharField(max_length=255, blank=True, null=True)  # List of vaccinations (comma-separated)
    treatment_details = models.TextField(blank=True, null=True)  # Details of any treatments or medication
    veterinarian_name = models.CharField(max_length=100)  # Name of the vet who performed the checkup
    next_checkup_date = models.DateField(blank=True, null=True)  # Date for the next health checkup
    added_by = models.ForeignKey(Users_table, on_delete=models.SET_NULL, null=True)  # Employee who recorded the health information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health record for {self.animal.animal_name} on {self.checkup_date}"
