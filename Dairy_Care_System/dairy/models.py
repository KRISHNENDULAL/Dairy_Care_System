from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
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
    
    """ def save(self, *args, **kwargs):
        if not self.pk or not self.password.startswith('pbkdf2_sha256$'):  # Ensures the password is hashed only once
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs) """

    def __str__(self):
        return self.username
    