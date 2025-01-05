
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from emailApp.views import *
from emailApp import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/upload-csv/',CSVUploadView.as_view(),name="upload_csv"),
    path('api/login/', LoginView.as_view(), name='login'),
    path('upload-csv/', CSVSavingView.as_view(), name='save-csv'),
    path('api/email-templates/', EmailTemplateCreateView.as_view(), name='create-email-template'),
    path('api/send-email/', SendEmailView.as_view(), name='send_email'),
    path("api/email-suggestions/", get_email_suggestions, name="email_suggestions"),
    path('api/campaign-metrics/save/', CampaignMetricsCreateView.as_view(), name='create_campaign'),
    path('api/campaign-metrics/<str:campaign_name>/', CampaignMetricsView.as_view(), name='campaign_detail'),
   path('api/campaign-view-set/', CampaignMetricsViewSet.as_view({'get': 'list', 'post': 'create'}), name="campaign_view"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
