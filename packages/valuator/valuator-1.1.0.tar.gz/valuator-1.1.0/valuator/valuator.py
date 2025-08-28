import json
import os
import aiohttp
import re
from typing import Dict, Optional
from functools import lru_cache, wraps

def convert_currency(func):
    """
    Decorator to convert USD prices to a specified currency if provided.
    """
    @wraps(func)
    def wrapper(self, model: str, currency: Optional[str] = None) -> Dict:
        result = func(self, model)
        if currency and currency.lower() != "usd":
            if currency.lower() not in self.currency_rates:
                raise ValueError(f"Unsupported currency: {currency}")
            rate = self.currency_rates[currency.lower()]
            converted = {}
            for model_name, costs in result.items():
                converted[model_name] = {
                    "input_cost_per_token": costs["input_cost_per_token"] * rate,
                    "output_cost_per_token": costs["output_cost_per_token"] * rate
                }
            return converted
        return result
    return wrapper

class Valuator:
    """
    A library to fetch model prices from GitHub and perform regex search on model names,
    returning only input and output cost per token for matched models.
    Supports currency conversion for prices.
    """

    def __init__(self, model_prices_url: str = "https://raw.githubusercontent.com/AgentOps-AI/tokencost/main/tokencost/model_prices.json", 
                 currency_url: str = "https://latest.currency-api.pages.dev/v1/currencies/usd.json",
                 cache_file: str = "model_prices.json", 
                 etag_file: str = "model_prices.etag",
                 currency_cache_file: str = "currency_rates.json",
                 currency_etag_file: str = "currency_rates.etag"):
        """
        Initialize Valuator with configuration for fetching model prices and currency rates.

        Args:
            model_prices_url (str): URL to fetch model_prices.json.
            currency_url (str): URL to fetch currency conversion rates.
            cache_file (str): Path to cache model_prices.json locally.
            etag_file (str): Path to store the ETag of the cached model prices.
            currency_cache_file (str): Path to cache currency_rates.json locally.
            currency_etag_file (str): Path to store the ETag of the cached currency rates.

        Note:
            Call `await initialize()` to complete setup.
        """
        self.model_prices_url = model_prices_url
        self.currency_url = currency_url
        self.cache_file = cache_file
        self.etag_file = etag_file
        self.currency_cache_file = currency_cache_file
        self.currency_etag_file = currency_etag_file
        self.model_prices = {}
        self.model_names = set()
        self.currency_rates = {}
        self._session = None

    async def initialize(self, force_refresh: bool = True):
        """
        Asynchronously initialize by fetching model prices, currency rates, and setting up the session.

        Args:
            force_refresh (bool): If True, fetch from URLs even if caches exist. Defaults to True.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession()
            try:
                await self._fetch_model_prices(force_refresh)
                await self._fetch_currency_rates(force_refresh)
            except Exception as e:
                await self._session.close()
                self._session = None
                raise e

    async def _fetch_model_prices(self, force_refresh: bool):
        """
        Fetch model_prices.json from the URL or load from cache if available and not modified.

        Args:
            force_refresh (bool): If True, skip cache and fetch from URL.
        """
        cached_etag = None
        if not force_refresh and os.path.exists(self.cache_file) and os.path.exists(self.etag_file):
            try:
                with open(self.etag_file, 'r', encoding='utf-8') as f:
                    cached_etag = f.read().strip()
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.model_prices = {
                        key: {
                            "input_cost_per_token": value.get("input_cost_per_token", 0.0),
                            "output_cost_per_token": value.get("output_cost_per_token", 0.0)
                        }
                        for key, value in data.items()
                    }
                    self.model_names = set(self.model_prices.keys())
                # Check if remote file has changed
                async with self._session.head(self.model_prices_url) as head_response:
                    remote_etag = head_response.headers.get('ETag', '').strip()
                    if remote_etag and cached_etag == remote_etag:
                        return  # Cache is up-to-date
            except (json.JSONDecodeError, IOError):
                print("Invalid or inaccessible model prices cache/ETag file, fetching from URL...")

        # Fetch from URL if cache is missing, invalid, or remote file has changed
        async with self._session.get(self.model_prices_url) as response:
            if response.status == 200:
                response_text = await response.text()
                data = json.loads(response_text)
                self.model_prices = {
                    key: {
                        "input_cost_per_token": value.get("input_cost_per_token", 0.0),
                        "output_cost_per_token": value.get("output_cost_per_token", 0.0)
                    }
                    for key, value in data.items()
                }
                self.model_names = set(self.model_prices.keys())
                try:
                    with open(self.cache_file, 'w', encoding='utf-8') as f:
                        json.dump(self.model_prices, f, indent=2)
                    # Store ETag
                    remote_etag = response.headers.get('ETag', '').strip()
                    if remote_etag:
                        with open(self.etag_file, 'w', encoding='utf-8') as f:
                            f.write(remote_etag)
                except IOError:
                    print("Failed to cache model prices or ETag locally.")
            else:
                raise Exception(f"Failed to fetch model prices: {response.status}")

    async def _fetch_currency_rates(self, force_refresh: bool):
        """
        Fetch currency_rates.json from the URL or load from cache if available and not modified.

        Args:
            force_refresh (bool): If True, skip cache and fetch from URL.
        """
        cached_etag = None
        if not force_refresh and os.path.exists(self.currency_cache_file) and os.path.exists(self.currency_etag_file):
            try:
                with open(self.currency_etag_file, 'r', encoding='utf-8') as f:
                    cached_etag = f.read().strip()
                with open(self.currency_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.currency_rates = data.get("usd", {})
                # Check if remote file has changed
                async with self._session.head(self.currency_url) as head_response:
                    remote_etag = head_response.headers.get('ETag', '').strip()
                    if remote_etag and cached_etag == remote_etag:
                        return  # Cache is up-to-date
            except (json.JSONDecodeError, IOError):
                print("Invalid or inaccessible currency rates cache/ETag file, fetching from URL...")

        # Fetch from URL if cache is missing, invalid, or remote file has changed
        async with self._session.get(self.currency_url) as response:
            if response.status == 200:
                response_text = await response.text()
                data = json.loads(response_text)
                self.currency_rates = data.get("usd", {})
                try:
                    with open(self.currency_cache_file, 'w', encoding='utf-8') as f:
                        json.dump(self.currency_rates, f, indent=2)
                    # Store ETag
                    remote_etag = response.headers.get('ETag', '').strip()
                    if remote_etag:
                        with open(self.currency_etag_file, 'w', encoding='utf-8') as f:
                            f.write(remote_etag)
                except IOError:
                    print("Failed to cache currency rates or ETag locally.")
            else:
                raise Exception(f"Failed to fetch currency rates: {response.status}")

    async def close(self):
        """
        Close the aiohttp session to free resources.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @lru_cache(maxsize=100)
    def _search_model_name(self, model: str, limit: int = 5) -> tuple:
        """
        Perform regex search on model names to find all matches, cached for efficiency.

        Args:
            model (str): User-provided model name (can be partial or regex pattern).
            limit (int): Maximum number of results to return.

        Returns:
            tuple: Tuple of dictionaries with model names and their input/output cost details.

        Raises:
            KeyError: If no matching models are found.
            ValueError: If model name is empty.
        """
        if not model:
            raise ValueError("Model name cannot be empty.")

        model = model.lower().strip()
        matches = []

        if model in self.model_names:
            return ({"model": model,
                     "input_cost_per_token": self.model_prices[model]["input_cost_per_token"],
                     "output_cost_per_token": self.model_prices[model]["output_cost_per_token"]},)

        try:
            pattern = re.compile(model, re.IGNORECASE)
            matches = [name for name in self.model_names if pattern.search(name)]
        except re.error:
            matches = [name for name in self.model_names if model in name.lower()]

        matches = matches[:limit]

        if not matches:
            raise KeyError(f"No models found matching '{model}'.")

        return tuple(
            {
                "model": matched_model,
                "input_cost_per_token": self.model_prices[matched_model]["input_cost_per_token"],
                "output_cost_per_token": self.model_prices[matched_model]["output_cost_per_token"]
            }
            for matched_model in matches
        )

    @convert_currency
    def calculate_prompt_cost(self, model: str, currency: Optional[str] = None) -> Dict:
        """
        Return input/output costs per token for all matching models.

        Args:
            model (str): Model name (can be partial or regex pattern).
            currency (str, optional): Currency to convert prices to (e.g., "INR"). Defaults to USD.

        Returns:
            Dict: Dictionary with model names and input/output costs per token.
        """
        matched_models = self._search_model_name(model)
        return {match["model"]: {
            "input_cost_per_token": match["input_cost_per_token"],
            "output_cost_per_token": match["output_cost_per_token"]
        } for match in matched_models}

    @convert_currency
    def count_tokens(self, model: str, currency: Optional[str] = None) -> Dict:
        """
        Return input/output costs per token for all matching models.

        Args:
            model (str): Model name (can be partial or regex pattern).
            currency (str, optional): Currency to convert prices to (e.g., "INR"). Defaults to USD.

        Returns:
            Dict: Dictionary with model names and input/output costs per token.
        """
        matched_models = self._search_model_name(model)
        return {match["model"]: {
            "input_cost_per_token": match["input_cost_per_token"],
            "output_cost_per_token": match["output_cost_per_token"]
        } for match in matched_models}

    @convert_currency
    def get_model_costs(self, model: str, currency: Optional[str] = None) -> Dict:
        """
        Get the input/output cost details for all matching models.

        Args:
            model (str): Model name (can be partial or regex pattern).
            currency (str, optional): Currency to convert prices to (e.g., "INR"). Defaults to USD.

        Returns:
            Dict: Dictionary with input/output cost details for all matching models.
        """
        matched_models = self._search_model_name(model)
        return {match["model"]: {
            "input_cost_per_token": match["input_cost_per_token"],
            "output_cost_per_token": match["output_cost_per_token"]
        } for match in matched_models}