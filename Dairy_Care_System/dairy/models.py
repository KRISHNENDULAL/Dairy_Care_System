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
        ('owner', 'Farm Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        # Only hash the password if it has been set/changed
        if self.pk is None or self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username  
    


class Products_table(models.Model):
    product_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    product_name = models.CharField(max_length=255)  # Product Name
    product_description = models.TextField()           # Product Description
    product_quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity
    quantity_unit = models.CharField(max_length=20)   # Unit of measurement
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price field
    product_category = models.CharField(max_length=100, null=True, blank=True)  # Category field
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



class Notifications_table(models.Model):
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Products_table, on_delete=models.CASCADE, null=True, blank=True)



class PreOrder(models.Model):
    user = models.ForeignKey(Users_table, on_delete=models.CASCADE)
    product = models.ForeignKey(Products_table, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date_of_delivery = models.DateField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pre-Order: {self.product.product_name} by {self.user.username}"
    


class Animals_table(models.Model):
    animal_id = models.AutoField(primary_key=True)
    animal_name = models.CharField(max_length=100)
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



class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)  # Unique identifier for the cart item
    user = models.ForeignKey(Users_table, on_delete=models.CASCADE)  # Link to the user who added the product to the cart
    product = models.ForeignKey(Products_table, on_delete=models.CASCADE)  # Link to the product added to the cart
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product
    quantity_unit = models.CharField(max_length=20)   # Unit of measurement
    added_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when a product is added to the cart

    class Meta:
        unique_together = ('user', 'product')  # Prevents the same user adding the same product more than once

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name} in cart"

    def get_total_price(self):
        return self.quantity * self.product.product_price  # Calculate the total price
    


class Feedback_table(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users_table, on_delete=models.CASCADE)  # Customer providing the feedback
    product = models.ForeignKey(Products_table, on_delete=models.CASCADE)  # Product being reviewed
    rating = models.IntegerField()  # Rating out of 5
    feedback_text = models.TextField(blank=True, null=True)  # Optional feedback text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the feedback was submitted

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.product.product_name}"
    


class Order_table(models.Model):
    PAYMENT_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(Users_table, on_delete=models.CASCADE)  # Reference to user
    name = models.CharField(max_length=255, null=False, blank=False)  # Customer name
    email = models.EmailField(null=False, blank=False)  # Email address
    phone = models.CharField(max_length=20, null=False, blank=False)  # Contact number
    place = models.CharField(max_length=255, null=False, blank=False)  # Place
    pincode = models.CharField(max_length=6, null=False, blank=False)  # Pincode
    delivery_address = models.TextField(null=False, blank=False)  # Delivery address
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price of the order
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)  # Payment method
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # Order status
    order_date = models.DateTimeField(auto_now_add=True)  # Automatically set order date
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem_table(models.Model):
    order = models.ForeignKey(Order_table, on_delete=models.CASCADE, related_name='order_items')  # Reference to Order_table
    product = models.ForeignKey(Products_table, on_delete=models.CASCADE)  # Reference to the Product
    quantity = models.PositiveIntegerField()  # Quantity of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in Order {self.order.id}"
    


class Address_table(models.Model):
    user = models.ForeignKey(Users_table, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    place = models.CharField(max_length=50)  # Removed choices
    delivery_address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name}, {self.district} - {self.street_address}, {self.town_city}, {self.postcode_zip}"

    
    def full_address(self):
        return f"{self.street_address}, {self.town_city}, {self.district}, {self.postcode_zip}"
    

