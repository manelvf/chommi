# Chommies

A Django-based betting platform for friendly wagers among friends.

## Features

- Event creation and management
- Betting with dynamic odds
- User profiles and authentication
- Celery for async tasks
- Redis for task queue

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables (copy `.env.example` to `.env`):
   ```bash
   cp .env.example .env
   ```

3. Run migrations:
   ```bash
   uv run python manage.py migrate
   ```

4. Start the development server:
   ```bash
   uv run python manage.py runserver
   ```

## Development

- Django 5.1.7
- Python 3.11+
- SQLite database (default)
- Celery for background tasks
- Redis for task broker
