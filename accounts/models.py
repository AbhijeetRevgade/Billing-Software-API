from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    OWNER = 'OWNER'
    STAFF = 'STAFF'
    
    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (STAFF, 'Staff'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STAFF)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
