# Django Todo Application

A simple task manager built with Django. Each user registers an account and manages their own
private list of tasks, which can be marked important, marked complete, edited, or deleted.

## Features

- User registration, login, and logout
- Per-user tasks (each user only sees their own)
- Add a task with a title and an optional due date
- Mark a task as important
- Mark a task as complete
- Edit a task
- Delete a task
- Home dashboard split into **Active**, **Important**, and **Completed** sections
- Django admin dashboard

## Requirements

- Python 3.14
- Django 6.0.7

## Installation

```
git clone <repo-url>

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

## Usage

1. Go to `/auth/register/` to create an account (or `/auth/login/` if you already have one).
2. You'll be redirected to `/home/`, your task dashboard.
3. Add tasks, and use the controls on each task to mark it important, mark it complete, edit it, or delete it.
4. Log out from `/auth/logout/`.

## Admin

Django admin is available at `/admin/`, using the superuser created during installation.
