
from django.db import models
from django.contrib.auth.models import User

class EmailTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=255,default=None)
    lastname = models.CharField(max_length=255,default=None)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    

class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    
    def __str__(self):
        return self.email

