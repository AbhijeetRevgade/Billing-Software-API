from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    OWNER  = 'OWNER'
    STAFF  = 'STAFF'
    VIEWER = 'VIEWER'

    ROLE_CHOICES = [
        (OWNER,  'Owner'),
        (STAFF,  'Staff'),
        (VIEWER, 'Viewer'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STAFF)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_owner(self):
        return self.role == self.OWNER

    @property
    def is_staff_member(self):
        return self.role == self.STAFF

    @property
    def is_viewer(self):
        return self.role == self.VIEWER
