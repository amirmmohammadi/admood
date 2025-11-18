from django.db import models


class PlatformChoice(models.TextChoices):
    """Platform choices for social media profiles"""
    TWITTER = 'twitter', 'Twitter'
    INSTAGRAM = 'instagram', 'Instagram'

