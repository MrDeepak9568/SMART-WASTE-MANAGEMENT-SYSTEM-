from django.db import models
from django.contrib.auth.models import User

class WasteReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=100)
    estimate_amt = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    date_reported = models.DateTimeField(auto_now_add=True)
    collected = models.BooleanField(default=False)
    proof_image = models.ImageField(upload_to='proof_images/', blank=True, null=True)
    reward_given = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.waste_type} - {self.estimate_amt} at {self.location}"
