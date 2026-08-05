# Djando-web-Stock-Modeling

Django-web prototype for modeling stocks

This prototype project explores linear time series analysis model Autoregressive Moving Average (ARMA) and nonlinear time series model Generalized Auto regressive Conditional Heteroskedasticity(GARCH) for modeling stocks through a website using django framework.

## Setup

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` and fill in real values, then export them into your shell
   (Django doesn't auto-load `.env` files without an extra library):
   ```
   export DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
   export IEX_API_TOKEN=your_iex_cloud_token
   ```
3. Run the dev server from `stock_modeling/`:
   ```
   cd stock_modeling
   python manage.py migrate
   python manage.py runserver
   ```
