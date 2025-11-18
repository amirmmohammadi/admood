"""
Background task for periodic follower count checking and milestone alerts
"""
from django.utils import timezone

from .models import SocialMediaProfile, AlertSettings, FollowerCountHistory, AlertNotification
from .services import mock_social_service, telegram_service


def check_follower_counts():
    """
    Background task to check follower counts for all active profiles
    and send alerts if milestones are reached
    """
    profiles = SocialMediaProfile.objects.all()

    for profile in profiles:
        try:
            # Fetch current follower count from mock API
            api_response = mock_social_service.get_follower_count(
                platform=profile.platform,
                username=profile.username
            )

            new_follower_count = api_response['follower_count']
            old_follower_count = profile.current_follower_count

            # Update profile
            profile.current_follower_count = new_follower_count
            profile.last_checked = timezone.now()
            profile.save()

            # Record in history
            FollowerCountHistory.objects.create(
                profile=profile,
                follower_count=new_follower_count
            )

            # Check for milestone alerts
            check_milestone_alerts(profile, old_follower_count, new_follower_count)

        except Exception as e:
            print(f"Error checking profile {profile.id}: {e}")
            continue


def check_milestone_alerts(profile, old_count, new_count):
    """
    Check if a milestone has been reached and send alert if needed
    """
    try:
        alert_settings = AlertSettings.objects.filter(profile=profile, is_active=True).first()

        if not alert_settings:
            return

        milestone = alert_settings.milestone_followers

        if old_count < milestone <= new_count:
            # Milestone reached!
            message = telegram_service.format_milestone_message(
                username=profile.username,
                platform=profile.platform,
                milestone=milestone,
                current_count=new_count
            )

            notification = AlertNotification.objects.create(
                profile=profile,
                milestone_followers=milestone,
                follower_count_at_alert=new_count,
                message=message
            )

            if alert_settings.telegram_chat_id:
                telegram_sent = telegram_service.send_notif1ication(
                    chat_id=alert_settings.telegram_chat_id,
                    message=message
                )
                notification.telegram_sent = telegram_sent
                notification.save()

    except Exception as e:
        print(f"Error checking milestone alerts for profile {profile.id}: {e}")
