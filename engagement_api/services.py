"""
Services for mock social media API and Telegram notifications
"""
import random
from datetime import datetime
from typing import Dict

import requests
from django.conf import settings


class MockSocialMediaService:
    """
    Mock service to simulate social media API calls
    Generates realistic follower count data with some randomness
    """

    def __init__(self):
        # Store base follower counts per profile to simulate gradual growth
        self._base_counts = {}

    def get_follower_count(self, platform: str, username: str) -> Dict:
        """
        Mock API call to get follower count
        Simulates gradual growth with some randomness
        """
        # Create a unique key for this profile
        profile_key = f"{platform}_{username}"

        # Initialize base count if not exists
        if profile_key not in self._base_counts:
            # Start with a random base between 500-2000
            self._base_counts[profile_key] = random.randint(500, 2000)

        # Simulate gradual growth (1-5 followers per check)
        growth = random.randint(1, 5)
        self._base_counts[profile_key] += growth

        # Add some randomness (-2 to +3)
        current_count = self._base_counts[profile_key] + random.randint(-2, 3)
        current_count = max(0, current_count)  # Ensure non-negative

        return {
            'follower_count': current_count,
            'timestamp': datetime.now().isoformat(),
            'platform': platform,
            'username': username
        }

    def reset_base_count(self, platform: str, username: str):
        """Reset base count for testing purposes"""
        profile_key = f"{platform}_{username}"
        if profile_key in self._base_counts:
            del self._base_counts[profile_key]


class TelegramNotificationService:

    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None

    def send_notification(self, chat_id: str, message: str) -> bool:

        if not self.bot_token or not self.api_url:
            # If no bot token configured, just log (for development)
            print(f"[TELEGRAM MOCK] Would send to {chat_id}: {message}")
            return True  # Return True for mock mode

        try:
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to send Telegram notification: {e}")
            return False

    def format_milestone_message(self, username: str, platform: str,
                                 milestone: int, current_count: int) -> str:
        return (
            f"🎉 <b>Milestone Achieved!</b>\n\n"
            f"Profile: <b>@{username}</b> ({platform})\n"
            f"Reached: <b>{current_count:,}</b> followers\n"
            f"Milestone: <b>{milestone:,}</b> followers\n\n"
            f"Congratulations! 🚀"
        )


# Singleton instances
mock_social_service = MockSocialMediaService()
telegram_service = TelegramNotificationService()
