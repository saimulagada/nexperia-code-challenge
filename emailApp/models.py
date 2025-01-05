
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
    
class CampaignMetrics(models.Model):
    campaign_name = models.CharField(max_length=255)
    emails_sent = models.IntegerField(default=0)
    emails_pending = models.IntegerField(default=0)
    emails_failed = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.campaign_name} - {self.emails_sent} Sent, {self.emails_pending} Pending, {self.emails_failed} Failed"

