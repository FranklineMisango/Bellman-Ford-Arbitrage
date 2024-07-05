# forex_scraper.py
import json
import urllib.request
import pandas as pd
import numpy as np
import ssl
from config import Exchange_Rates_api as API_KEY

class ForexScraper:
    """
    This class is used to pull exchange rate information for a specified date
    from an API and store the results in an adjacency matrix.
    """
    adjacency_matrix = None
    currency_list = None
    currency_flags = {
            "CAD": "🇨🇦", "HKD": "🇭🇰", "ISK": "🇮🇸", "PHP": "🇵🇭",
            "DKK": "🇩🇰", "HUF": "🇭🇺", "CZK": "🇨🇿", "GBP": "🇬🇧",
            "RON": "🇷🇴", "SEK": "🇸🇪", "IDR": "🇮🇩", "INR": "🇮🇳",
            "BRL": "🇧🇷", "RUB": "🇷🇺", "HRK": "🇭🇷", "JPY": "🇯🇵",
            "THB": "🇹🇭", "CHF": "🇨🇭", "EUR": "🇪🇺", "MYR": "🇲🇾",
            "BGN": "🇧🇬", "TRY": "🇹🇷", "CNY": "🇨🇳", "NOK": "🇳🇴",
            "NZD": "🇳🇿", "ZAR": "🇿🇦", "USD": "🇺🇸", "MXN": "🇲🇽",
            "SGD": "🇸🇬", "AUD": "🇦🇺", "ILS": "🇮🇱", "KRW": "🇰🇷",
            "PLN": "🇵🇱"
        }

    def __init__(self, date, base_currency="EUR"):
        """
        Constructor that initializes the list of currencies used,
        creates the adjacency_matrix and creates a CSV file from the matrix.
        """
        self.base_currency = base_currency.upper()
        self.currency_list = list(self.currency_flags.keys())
        self.create_adjacency_matrix(date)
        self.create_csv_from_adjacency_matrix()

    def create_adjacency_matrix(self, date):
        """
        Method that pulls exchange rates from the API and stores the results
        in an adjacency_matrix.
        """
        num_currencies = len(self.currency_list)
        self.adjacency_matrix = pd.DataFrame(
            np.zeros(shape=(num_currencies, num_currencies)),
            columns=self.currency_list,
            index=self.currency_list
        )

        # Fetch rates using the specified base currency
        json_obj = self.get_exchange_rate_json_from_api(date=date, base=self.base_currency)
        if json_obj is None or "rates" not in json_obj:
            raise Exception(f"Error retrieving base exchange rates from API for base {self.base_currency}")

        base_rates = json_obj["rates"]
        base_rates[self.base_currency] = 1.0  # Add the base itself

        # Fill in the adjacency matrix with derived rates
        for currency1 in self.currency_list:
            for currency2 in self.currency_list:
                if currency1 in base_rates and currency2 in base_rates:
                    rate = base_rates[currency2] / base_rates[currency1]
                    self.adjacency_matrix.at[currency1, currency2] = rate

    def get_exchange_rate_json_from_api(self, date, base="EUR"):
        """
        This method accesses the API and returns a JSON object for a given
        currency and date.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        
        json_obj = None
        try:
            with urllib.request.urlopen(url, context=context) as response:
                json_obj = json.loads(response.read())
        except Exception as e:
            print(f"Error retrieving information from API for base {base} on {date}: {e}")
        return json_obj

    def create_csv_from_adjacency_matrix(self):
        """
        This method creates and saves a CSV file from the adjacency_matrix.
        """
        if self.adjacency_matrix is not None:
            self.adjacency_matrix.to_csv("forex_exchange_matrix.csv")

    def get_exchange_table_html(self):
        """
        This method returns the HTML content for the adjacency_matrix.
        """
        return self.adjacency_matrix.to_html()

    def get_adjacency_matrix(self):
        """
        This method returns the adjacency_matrix.
        """
        return self.adjacency_matrix

    def get_currency_list(self):
        """
        This method returns the currency_list.
        """
        return self.currency_list
