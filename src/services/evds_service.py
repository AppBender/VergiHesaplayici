import os
from evds import evdsAPI
import pandas as pd
from datetime import datetime
from decimal import Decimal
from services.logger_service import LoggerService
from databases.database_factory import DatabaseFactory


class EvdsService:
    def __init__(self):
        self.logger = LoggerService()
        self.db = DatabaseFactory.get_database('mongoDB')
        self.api_key = os.getenv('TCMB_API_KEY')

        if not self.api_key:
            raise ValueError("TCMB_API_KEY environment variable is not set")

        self.evds = evdsAPI(self.api_key)

    def get_exchange_rate(self, date: datetime) -> Decimal:
        """Get USD/TRY exchange rate for given date"""
        date_str = date.strftime("%d-%m-%Y")

        try:
            # Check cache first
            existing_rate = self.db.get_exchange_rate(date_str)
            if existing_rate:
                return existing_rate

            # Fetch from EVDS if not in cache
            rate = self._fetch_from_evds('TP.DK.USD.S.YTL', date_str, value_code='TP_DK_USD_S_YTL')
            if rate is None:
                self.logger.log_warning(f"No exchange rate found for {date}")
                return None

            # Cache the result
            self.db.save_exchange_rate(date_str, rate)
            return rate

        except Exception as e:
            self.logger.log_error(f"Error getting exchange rate: {str(e)}")
            raise ValueError(f"Could not get exchange rate for {date_str}")

    def get_next_available_exchange_rate(self, date):
        """
        If there is no exchange rate data for the specified date, it returns the exchange
        rate data for the next available business day.
        """
        rate = self.get_exchange_rate(date)
        if rate is not None:
            return rate

        # Search for data starting from the next day (maximum 10 days)
        for i in range(1, 10):
            next_date = date + pd.Timedelta(days=i)
            rate = self.get_exchange_rate(next_date)
            if rate is not None:
                return rate

        # If no data is found within 10 days, return a default value or throw an error
        self.logger.log_error(f"No exchange rate data found within 10 days after {date}.")
        return 1.0  # Default value or you can return None

    def get_yiufe_index(self, date: datetime) -> Decimal:
        """Get YI-ÜFE index for given date"""
        date_str = date.strftime("%d-%m-%Y")

        try:
            # Check cache first
            existing_index = self.db.get_yiufe_index(date_str)
            if existing_index:
                return existing_index

            # Fetch from EVDS if not in cache
            index = self._fetch_from_evds('TP.TUFE1YI.T1', date_str, value_code='TP_TUFE1YI_T1')  # TP.TUFE1YI.T1 Yİ-ÜFE genel endeks serisi
            if index is None:
                self.logger.log_warning(f"No YI-ÜFE index found for {date}")
                return None

            # Cache the result
            self.db.save_yiufe_index(date_str, index)
            return index

        except Exception as e:
            self.logger.log_error(f"Error getting YI-ÜFE index: {str(e)}")
            raise ValueError(f"Could not get YI-ÜFE index for {date_str}")

    def get_yiufe_index_rate(self, buy_date: datetime, sell_date: datetime) -> Decimal:
        """Calculate YI-ÜFE rate between buy and sell dates"""
        try:
            buy_index = self.get_yiufe_index(buy_date)
            sell_index = self.get_yiufe_index(sell_date)

            # Log specific dates when indices are None
            if buy_index is None:
                self.logger.log_warning(f"No YI-ÜFE index found for buy date: {buy_date}")

            if sell_index is None:
                self.logger.log_warning(f"No YI-ÜFE index found for sell date: {sell_date}")

            if buy_index is None or sell_index is None:
                self.logger.log_warning(f"Could not calculate YI-ÜFE rate for period {buy_date} - {sell_date}")
                return None

            # Calculate increase rate
            increase_rate = ((sell_index - buy_index) / buy_index) * 100

            return Decimal(str(increase_rate))

        except Exception as e:
            self.logger.log_error(f"YI-ÜFE rate calculation failed: {str(e)}")
            return None

    def get_next_available_yiufe_index(self, date):
        """
        If there is no YI-ÜFE index data for the specified date, it returns the index
        data for the next available business day.
        """
        index = self.get_yiufe_index(date)
        if index is not None:
            return index

        # Search for data starting from the next day (maximum 10 days)
        for i in range(1, 10):
            next_date = date + pd.Timedelta(days=i)
            index = self.get_yiufe_index(next_date)
            if index is not None:
                return index

        # If no data is found within 10 days, return a default value or throw an error
        self.logger.log_error(f"No YI-ÜFE index data found within 10 days after {date}.")
        return None

    def _fetch_from_evds(self, series_code: str, date_str: str, value_code=None) -> Decimal:
        """Fetch data from EVDS API for given series and date"""
        if not value_code:
            value_code = series_code
        try:
            df = self.evds.get_data([series_code], startdate=date_str, enddate=date_str)

            if df.empty:
                self.logger.log_error(f"No data returned from EVDS API for {series_code} on {date_str}")
                return None

            # Get the first value from the series
            value = df.iloc[0][value_code]

            # Check if value is valid (not NaN or None)
            if pd.notna(value):
                return Decimal(str(value))

            return None

        except Exception as e:
            self.logger.log_error(f"EVDS API error for {series_code}: {str(e)}")
            return None
