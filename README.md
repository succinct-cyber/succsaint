
# Succsaint

A freestyle clothing store made when I was bored and needd to just build something.

## Overview

Succsaint is a full-stack online store with product listings, product variations, cart logic, checkout flow, order handling, and admin management.

## Features

- Product catalogue
- Product categories
- Size and colour
- Cart system for logged-in users
- Checkout flow
- Order management
- Static and media file handling

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript

## Screenshots

### Homepage
![Homepage](screenshot/homepages.png)

### Product Page
![Product Page](screenshot/prod-desc.png)

### Cart Page
![Cart Page](screenshot/carts.png)

## Setup

```bash
git clone https://github.com/succinct-cyber/succsaint.git
cd succsaint
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
