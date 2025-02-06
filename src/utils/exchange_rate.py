import requests
from datetime import datetime


def get_exchange_rate(date: datetime) -> float:
    # Example API endpoint for exchange rates
    api_url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(api_url)
    data = response.json()
    return data['rates']['TRY']
