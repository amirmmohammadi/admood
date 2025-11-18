# Social Media Engagement Insights API


## Requirements

- Python 3.12+
- Django 5.2.8
- Pycharm

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.sample .env
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### Environment Variables

All sensitive configuration is stored in the `.env` file. Copy `env.sample` to `.env` and update the values:

```bash
cp env.sample .env
```

### Telegram Bot (Optional)

To enable Telegram notifications:

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Add it to your `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
4. Get your chat ID (you can use [@userinfobot](https://t.me/userinfobot))
5. Include the chat ID when setting up alerts via the API

## API Endpoints

All endpoints require Basic Authentication. Use your Django user credentials.

### Base URL
```
http://localhost:8000/api/
```

### Profile Management

#### Register/Update Profile
```
POST /api/profiles/
Content-Type: application/json

{
    "platform": "twitter",
    "username": "example_user",
    "current_follower_count": 500
}
```

#### Get All Profiles
```
GET /api/profiles/
```

#### Get Profile Details
```
GET /api/profiles/{id}/
```

#### Update Profile
```
PUT /api/profiles/{id}/
Content-Type: application/json

{
    "current_follower_count": 600
}
```

#### Delete Profile
```
DELETE /api/profiles/{id}/
```

### Alert Settings

#### Set Alert Settings
```
POST /api/alerts/
Content-Type: application/json

{
    "profile_id": 1,
    "milestone_followers": 1000,
    "telegram_chat_id": "123456789",
    "is_active": true
}
```

#### Get All Alert Settings
```
GET /api/alerts/
```

#### Get Alert Settings
```
GET /api/alerts/{id}/
```

#### Update Alert Settings
```
PUT /api/alerts/{id}/
Content-Type: application/json

{
    "milestone_followers": 2000,
    "is_active": false
}
```

### Engagement Insights

#### Get Insights for All Profiles
```
GET /api/insights/
```

#### Get Insights for Specific Profile
```
GET /api/insights/{profile_id}/
```

Response includes:
- Current follower count
- Follower change in last 24 hours
- Follower change percentage
- Recent history

#### Top Follower Insights (Bonus)
```
GET /api/insights/top/
```

Returns top 5 increases and decreases in the last 24 hours.

### Notifications

#### Get All Notifications
```
GET /api/notifications/
```

#### Get Specific Notification
```
GET /api/notifications/{id}/
```

## Background Task

The system includes a background task to periodically check follower counts and send milestone alerts.

### Run Once
```bash
python manage.py check_followers --once
```

### Run Periodically (Default: every 5 minutes)
```bash
python manage.py check_followers
```

### Custom Interval
```bash
python manage.py check_followers --interval 600  # 10 minutes
```

For production, you can set this up as a cron job or use a task scheduler like Celery.

## Example Workflow

1. **Register a profile:**
   ```bash
   curl -X POST http://localhost:8000/api/profiles/ \
     -u username:password \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "twitter",
       "username": "example_user",
       "current_follower_count": 500
     }'
   ```

2. **Set an alert for 1000 followers:**
   ```bash
   curl -X POST http://localhost:8000/api/alerts/ \
     -u username:password \
     -H "Content-Type: application/json" \
     -d '{
       "profile_id": 1,
       "milestone_followers": 1000,
       "telegram_chat_id": "123456789",
       "is_active": true
     }'
   ```

3. **Start the background task:**
   ```bash
   python manage.py check_followers
   ```

4. **Check insights:**
   ```bash
   curl -u username:password http://localhost:8000/api/insights/1/
   ```

5. **View notifications when milestone is reached:**
   ```bash
   curl -u username:password http://localhost:8000/api/notifications/
   ```

## Mock Data

The API uses a mock social media service that simulates follower count changes. Each profile starts with a random base count between 500-2000 followers and gradually increases with each check (1-5 followers per check, with some randomness).


## Authentication

The API uses Basic Authentication. Include credentials in your requests:

```bash
curl -u username:password http://localhost:8000/api/profiles/
```

Or in Python:
```python
import requests
response = requests.get(
    'http://localhost:8000/api/profiles/',
    auth=('username', 'password')
)
```

## Testing

You can test the API using:
- cURL
- Postman

## License

This project is created for http://hamipishgaman.com/.

