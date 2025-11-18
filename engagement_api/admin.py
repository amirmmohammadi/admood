from django.contrib import admin

from .models import SocialMediaProfile, AlertSettings, FollowerCountHistory, AlertNotification


@admin.register(SocialMediaProfile)
class SocialMediaProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'platform', 'user', 'current_follower_count', 'last_checked', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['username', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AlertSettings)
class AlertSettingsAdmin(admin.ModelAdmin):
    list_display = ['profile', 'milestone_followers', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['profile__username', 'profile__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FollowerCountHistory)
class FollowerCountHistoryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'follower_count', 'recorded_at']
    list_filter = ['recorded_at', 'profile__platform']
    search_fields = ['profile__username']
    readonly_fields = ['recorded_at']
    date_hierarchy = 'recorded_at'


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = ['profile', 'milestone_followers', 'follower_count_at_alert', 'telegram_sent', 'sent_at']
    list_filter = ['telegram_sent', 'sent_at']
    search_fields = ['profile__username', 'message']
    readonly_fields = ['sent_at']
