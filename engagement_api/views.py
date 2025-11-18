from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    SocialMediaProfile, AlertSettings,
    FollowerCountHistory, AlertNotification
)
from .serializers import (
    SocialMediaProfileSerializer, AlertSettingsSerializer,
    EngagementInsightsSerializer, TopFollowerInsightsSerializer,
    AlertNotificationSerializer, FollowerCountHistorySerializer
)


class ProfileRegisterView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SocialMediaProfileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile, created = SocialMediaProfile.objects.get_or_create(
            user=request.user,
            platform=serializer.validated_data['platform'],
            username=serializer.validated_data['username'],
            defaults={
                'current_follower_count': serializer.validated_data.get('current_follower_count', 0)
            }
        )

        if not created:
            profile.current_follower_count = serializer.validated_data.get(
                'current_follower_count', profile.current_follower_count)
            profile.save()

        response_serializer = self.serializer_class(profile)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def get(self, request):
        profiles = SocialMediaProfile.objects.filter(user=request.user)
        serializer = self.serializer_class(profiles, many=True)
        return Response(serializer.data)


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SocialMediaProfileSerializer

    def get(self, request, profile_id):
        profile = get_object_or_404(SocialMediaProfile, id=profile_id, user=request.user)
        serializer = self.serializer_class(profile)
        return Response(serializer.data)

    def put(self, request, profile_id):
        profile = get_object_or_404(SocialMediaProfile, id=profile_id, user=request.user)
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, profile_id):
        profile = get_object_or_404(SocialMediaProfile, id=profile_id, user=request.user)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlertSettingsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlertSettingsSerializer

    def post(self, request):
        profile_id = request.data.get('profile_id')
        if not profile_id:
            return Response(
                {'profile_id': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = get_object_or_404(SocialMediaProfile, id=profile_id, user=request.user)

        alert_settings, created = AlertSettings.objects.get_or_create(profile=profile, defaults=request.data)

        if not created:
            serializer = self.serializer_class(alert_settings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.serializer_class(alert_settings)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, alert_id=None):
        if alert_id:
            alert = get_object_or_404(AlertSettings, id=alert_id, profile__user=request.user)
            serializer = self.serializer_class(alert)
            return Response(serializer.data)

        alerts = AlertSettings.objects.filter(profile__user=request.user)
        serializer = self.serializer_class(alerts, many=True)
        return Response(serializer.data)

    def put(self, request, alert_id):
        alert = get_object_or_404(AlertSettings, id=alert_id, profile__user=request.user)
        serializer = self.serializer_class(alert, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EngagementInsightsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EngagementInsightsSerializer

    def get(self, request, profile_id=None):
        if profile_id:
            profile = get_object_or_404(SocialMediaProfile, id=profile_id, user=request.user)
            insights_data = self._calculate_insights(profile)
            serializer = self.serializer_class(insights_data)
            return Response(serializer.data)

        # Get insights for all profiles
        profiles = SocialMediaProfile.objects.filter(user=request.user)
        insights_list = [self._calculate_insights(profile) for profile in profiles]
        serializer = self.serializer_class(insights_list, many=True)
        return Response(serializer.data)

    def _calculate_insights(self, profile):
        # Get follower count 24 hours ago
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

        old_record = FollowerCountHistory.objects.filter(profile=profile,
                                                         recorded_at__lte=twenty_four_hours_ago).first()

        old_count = old_record.follower_count if old_record else profile.current_follower_count
        current_count = profile.current_follower_count

        follower_change = current_count - old_count
        follower_change_percentage = ((follower_change / old_count * 100) if old_count > 0 else 0)

        # Get recent history (last 10 records)
        recent_history = FollowerCountHistory.objects.filter(profile=profile)[:10]

        # Serialize recent history
        history_serializer = FollowerCountHistorySerializer(recent_history, many=True)

        return {
            'profile_id': profile.id,
            'username': profile.username,
            'platform': profile.platform,
            'current_follower_count': current_count,
            'last_checked': profile.last_checked,
            'follower_change_24h': follower_change,
            'follower_change_percentage_24h': round(follower_change_percentage, 2),
            'recent_history': history_serializer.data
        }


class TopFollowerInsightsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TopFollowerInsightsSerializer

    def get(self, request):
        """Get top follower insights"""
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

        # Get all profiles for the user
        profiles = SocialMediaProfile.objects.filter(user=request.user)

        top_increases = []
        top_decreases = []

        for profile in profiles:
            # Get oldest and newest records in last 24 hours
            history_24h = FollowerCountHistory.objects.filter(
                profile=profile,
                recorded_at__gte=twenty_four_hours_ago
            )

            if history_24h.count() >= 2:
                oldest = history_24h.first()
                newest = history_24h.last()

                change = newest.follower_count - oldest.follower_count
                change_percentage = (
                    (change / oldest.follower_count * 100) if oldest.follower_count > 0 else 0
                )

                insight_data = {
                    'profile_id': profile.id,
                    'username': profile.username,
                    'platform': profile.platform,
                    'follower_change': change,
                    'follower_change_percentage': round(change_percentage, 2),
                    'old_count': oldest.follower_count,
                    'new_count': newest.follower_count
                }

                if change > 0:
                    top_increases.append(insight_data)
                elif change < 0:
                    top_decreases.append(insight_data)

        # Sort and get top 5
        top_increases = sorted(top_increases, key=lambda x: x['follower_change'], reverse=True)[:5]
        top_decreases = sorted(top_decreases, key=lambda x: x['follower_change'])[:5]

        data = {
            'top_increases': top_increases,
            'top_decreases': top_decreases,
            'period': '24 hours'
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class AlertNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AlertNotificationSerializer

    def get(self, request, notification_id=None):
        if notification_id:
            notification = get_object_or_404(
                AlertNotification,
                id=notification_id,
                profile__user=request.user
            )
            serializer = self.serializer_class(notification)
            return Response(serializer.data)

        # Get all notifications for user's profiles
        notifications = AlertNotification.objects.filter(
            profile__user=request.user
        )
        serializer = self.serializer_class(notifications, many=True)
        return Response(serializer.data)
