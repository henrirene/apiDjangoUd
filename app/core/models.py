import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

class BaseUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """creates and saves new user"""
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def User(AbstractBaseUser, PermissionsMixin):
        """Customized user model that supports using email instead of username """
        email = models.EmailField(max_length=255, unique=True)
        name = models.CharField(max_length=255)
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)

        objects = UserManager()

        USERNAME_FIELD = 'email'
