
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    reward = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
class RewardTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('add', 'Add'),
        ('deduct', 'Deduct'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reward_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
    reason = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = '+' if self.transaction_type == 'add' else '-'
        return f"{self.user.username} {sign}{self.amount} ({self.reason})"
