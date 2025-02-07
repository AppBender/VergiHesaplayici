import os
from evds import evdsAPI
import json


def fetch_exchange_rate(date: str):
    API_KEY = os.getenv('TCMB_API_KEY')

    if not API_KEY:
        raise ValueError("TCMB_API_KEY environment variable is not set")

    evds = evdsAPI(API_KEY)
    # series = 'TP.DK.USD.S.YTL'
    try:
        df = evds.get_data(['TP.DK.USD.S.YTL'], startdate=date, enddate=date)
        json_str = df.to_json()
        print(f"Data fetched: {json_str}")
        dict = json.loads(json_str)
        rate = dict['TP_DK_USD_S_YTL']['0']
        if rate:
            return rate
        else:
            raise Exception("No exchange rate data found for the given date")
    except Exception as e:
        raise Exception(f"Error fetching exchange rates: {str(e)}")
