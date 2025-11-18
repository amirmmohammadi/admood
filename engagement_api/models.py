from django.contrib.auth.models import User
from django.db import models

from .base import TimeStampedBaseModel
from .choices import PlatformChoice


class SocialMediaProfile(TimeStampedBaseModel):
    """Model to store social media profiles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    platform = models.CharField(max_length=20, choices=PlatformChoice.choices)
    username = models.CharField(max_length=100)
    current_follower_count = models.IntegerField(default=0)
    last_checked = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'platform', 'username']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.platform}: {self.username} ({self.user.username})"


class AlertSettings(TimeStampedBaseModel):
    """Model to store milestone alert settings for profiles"""
    profile = models.OneToOneField(SocialMediaProfile, on_delete=models.CASCADE, related_name='alert_settings')
    milestone_followers = models.IntegerField(help_text="Follower count milestone to alert on")
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Telegram chat ID for notifications"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert for {self.profile.username} at {self.milestone_followers} followers"


class FollowerCountHistory(models.Model):
    """Model to track follower count changes over time"""
    profile = models.ForeignKey(SocialMediaProfile, on_delete=models.CASCADE, related_name='follower_history')
    follower_count = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['profile', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.profile.username}: {self.follower_count} at {self.recorded_at}"


class AlertNotification(models.Model):
    """Model to store sent alert notifications"""
    profile = models.ForeignKey(SocialMediaProfile, on_delete=models.CASCADE, related_name='notifications')
    milestone_followers = models.IntegerField()
    follower_count_at_alert = models.IntegerField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    telegram_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Alert for {self.profile.username} at {self.milestone_followers} followers"
