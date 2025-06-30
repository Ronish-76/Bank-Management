# Bank Management System

A simple Django web app to manage banks and their balances.

## Features

- Add, view, update, and delete banks
- Adjust balances for each bank
- View bank details

## Quick Start

1. **Install dependencies:**
   ```
   pip install django==5.2.3 jazzmin
   ```
2. **Run migrations:**
   ```
   python manage.py migrate
   ```
3. **Start the server:**
   ```
   python manage.py runserver
   ```
4. **Open:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Notes

- Data is not persistent (in-memory only)
- Admin panel: `/admin/`
