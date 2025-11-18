from django.urls import path
from .views import (
    ProfileRegisterView,
    ProfileDetailView,
    AlertSettingsView,
    EngagementInsightsView,
    TopFollowerInsightsView,
    AlertNotificationsView,
)

app_name = 'engagement_api'

urlpatterns = [
    # Profile endpoints
    path('profiles/', ProfileRegisterView.as_view(), name='profile-list'),
    path('profiles/<int:profile_id>/', ProfileDetailView.as_view(), name='profile-detail'),
    
    # Alert settings endpoints
    path('alerts/', AlertSettingsView.as_view(), name='alert-list'),
    path('alerts/<int:alert_id>/', AlertSettingsView.as_view(), name='alert-detail'),
    
    # Insights endpoints
    path('insights/', EngagementInsightsView.as_view(), name='insights-list'),
    path('insights/<int:profile_id>/', EngagementInsightsView.as_view(), name='insights-detail'),
    path('insights/top/', TopFollowerInsightsView.as_view(), name='top-insights'),
    
    # Notifications endpoint
    path('notifications/', AlertNotificationsView.as_view(), name='notifications-list'),
    path('notifications/<int:notification_id>/', AlertNotificationsView.as_view(), name='notification-detail'),
]

