from django.contrib import admin
from .models import EmailTemplate,UserProfile,CampaignMetrics



    

admin.site.register(EmailTemplate)
admin.site.register(UserProfile)
admin.site.register(CampaignMetrics)
