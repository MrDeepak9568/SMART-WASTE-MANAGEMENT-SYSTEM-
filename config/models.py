from django.db import models
from encrypted_model_fields.fields import EncryptedTextField

class APIKey(models.Model):
    name = models.CharField(max_length=100, unique=True)
    key = EncryptedTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
