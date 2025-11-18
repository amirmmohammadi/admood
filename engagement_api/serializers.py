from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SocialMediaProfile, AlertSettings, FollowerCountHistory, AlertNotification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class SocialMediaProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = SocialMediaProfile
        fields = [
            'id', 'user', 'platform', 'username', 
            'current_follower_count', 'last_checked', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'last_checked']


class AlertSettingsSerializer(serializers.ModelSerializer):
    profile = SocialMediaProfileSerializer(read_only=True)
    profile_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = AlertSettings
        fields = [
            'id', 'profile', 'profile_id', 'milestone_followers', 
            'telegram_chat_id', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FollowerCountHistorySerializer(serializers.ModelSerializer):
    profile = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = FollowerCountHistory
        fields = ['id', 'profile', 'follower_count', 'recorded_at']
        read_only_fields = ['id', 'recorded_at']


class AlertNotificationSerializer(serializers.ModelSerializer):
    profile = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'profile', 'milestone_followers', 
            'follower_count_at_alert', 'message', 
            'sent_at', 'telegram_sent'
        ]
        read_only_fields = ['id', 'sent_at']


class EngagementInsightsSerializer(serializers.Serializer):
    profile_id = serializers.IntegerField()
    username = serializers.CharField()
    platform = serializers.CharField()
    current_follower_count = serializers.IntegerField()
    last_checked = serializers.DateTimeField()
    follower_change_24h = serializers.IntegerField()
    follower_change_percentage_24h = serializers.FloatField()
    recent_history = FollowerCountHistorySerializer(many=True)


class TopFollowerInsightsSerializer(serializers.Serializer):
    top_increases = serializers.ListField()
    top_decreases = serializers.ListField()
    period = serializers.CharField()

