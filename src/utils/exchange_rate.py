from datetime import datetime
from decimal import Decimal
from api.tcmb_gov_tr import fetch_exchange_rate
from databases.database_factory import DatabaseFactory

db = DatabaseFactory.get_database('mongoDB')


def get_exchange_rate(date: datetime) -> Decimal:
    date_str = date.strftime("%d-%m-%Y")
    try:
        # Check if the exchange rate for the given date is already in the database
        existing_rate = db.get_exchange_rate(date_str)
        if existing_rate:
            return existing_rate

        # Fetch the exchange rate from the API
        exchange_rate = fetch_exchange_rate(date_str)
        if exchange_rate is None:
            logger.log_warning(f"No exchange rate found for {date}")

        # Save the exchange rate to the database
        db.save_exchange_rate(date_str, exchange_rate)

        return exchange_rate
    except Exception as e:
        db.log_error({'message': str(e)})
        raise ValueError(f"Could not fetch exchange rate for {date_str}")
