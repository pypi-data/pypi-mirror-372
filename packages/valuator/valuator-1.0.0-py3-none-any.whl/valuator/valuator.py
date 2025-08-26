import json
import os
import aiohttp
import re
from typing import Dict
from functools import lru_cache

class Valuator:
    """
    A library to fetch model prices from GitHub and perform regex search on model names,
    returning only input and output cost per token for matched models.
    """

    def __init__(self, model_prices_url: str = "https://raw.githubusercontent.com/AgentOps-AI/tokencost/main/tokencost/model_prices.json", cache_file: str = "model_prices.json", etag_file: str = "model_prices.etag"):
        """
        Initialize Valuator with configuration for fetching model prices.

        Args:
            model_prices_url (str): URL to fetch model_prices.json.
            cache_file (str): Path to cache model_prices.json locally.
            etag_file (str): Path to store the ETag of the cached file.

        Note:
            Call `await initialize()` to complete setup.
        """
        self.model_prices_url = model_prices_url
        self.cache_file = cache_file
        self.etag_file = etag_file
        self.model_prices = {}
        self.model_names = set()
        self._session = None

    async def initialize(self, force_refresh: bool = True):
        """
        Asynchronously initialize by fetching model prices and setting up the session.

        Args:
            force_refresh (bool): If True, fetch from URL even if cache exists. Defaults to True.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession()
            try:
                await self._fetch_model_prices(force_refresh)
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
                print("Invalid or inaccessible cache/ETag file, fetching from URL...")

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

    def calculate_prompt_cost(self, model: str) -> Dict:
        """
        Return input/output costs per token for all matching models.

        Args:
            model (str): Model name (can be partial or regex pattern).

        Returns:
            Dict: JSON object with model names and input/output costs per token.
        """
        matched_models = self._search_model_name(model)
        return {match["model"]: {
            "input_cost_per_token": match["input_cost_per_token"],
            "output_cost_per_token": match["output_cost_per_token"]
        } for match in matched_models}

    def count_tokens(self, model: str) -> Dict:
        """
        Return input/output costs per token for all matching models.

        Args:
            model (str): Model name (can be partial or regex pattern).

        Returns:
            Dict: JSON object with model names and input/output costs per token.
        """
        matched_models = self._search_model_name(model)
        return {match["model"]: {
            "input_cost_per_token": match["input_cost_per_token"],
            "output_cost_per_token": match["output_cost_per_token"]
        } for match in matched_models}

    def get_model_costs(self, model: str) -> Dict:
        """
        Get the input/output cost details for all matching models.

        Args:
            model (str): Model name (can be partial or regex pattern).

        Returns:
            Dict: JSON object with input/output cost details for all matching models.
        """
        matched_models = self._search_model_name(model)
        return {match["model"]: {
            "input_cost_per_token": match["input_cost_per_token"],
            "output_cost_per_token": match["output_cost_per_token"]
        } for match in matched_models}