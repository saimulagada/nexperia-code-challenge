from rest_framework import serializers
from .models import EmailTemplate,UserProfile,CampaignMetrics

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'user', 'firstname', 'lastname', 'subject', 'body', 'created_at']
        read_only_fields = ['user', 'created_at']  # `user` is auto-assigned and not passed in the request

    def create(self, validated_data):
        user = self.context['request'].user  # Get user from request context
        return EmailTemplate.objects.create(user=user, **validated_data)
    
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"

class CampaignMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignMetrics
        fields = ['id', 'campaign_name', 'emails_sent', 'emails_pending', 'emails_failed', 'last_updated']