import os
import re
import pandas as pd
import requests
from typing import Dict, Any, List, Optional

# In-memory caches to prevent repeated files reads and redundant API calls
_csv_cache: Dict[str, pd.DataFrame] = {}
_query_cache: Dict[str, Any] = {}

# Common country name aliases and mappings to match user free-text inputs
COUNTRY_ALIASES = {
    "us": "United States",
    "usa": "United States",
    "united states of america": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "uae": "United Arab Emirates",
    "korea": "Korea, Rep.",
    "south korea": "Korea, Rep.",
    "russia": "Russian Federation",
    "china": "China",
    "india": "India",
    "germany": "Germany",
    "france": "France",
    "japan": "Japan",
    "canada": "Canada",
    "australia": "Australia",
    "brazil": "Brazil",
    "sweden": "Sweden",
    "singapore": "Singapore",
    "israel": "Israel",
    "netherlands": "Netherlands",
    "spain": "Spain",
    "italy": "Italy",
    "switzerland": "Switzerland",
}

class DataProvider:
    """Base class for data providers (CSV, API, etc.)"""
    def get_data(self, **kwargs) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

class CSVDataProvider(DataProvider):
    """Loads and queries local CSV datasets with in-memory caching and intelligent matching."""
    def __init__(self, filename: str, data_dir: str = "data"):
        self.filename = filename
        self.filepath = os.path.normpath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), data_dir, filename)
        )

    def _load_csv(self) -> Optional[pd.DataFrame]:
        global _csv_cache
        if self.filepath in _csv_cache:
            return _csv_cache[self.filepath]
        
        if not os.path.exists(self.filepath):
            print(f"[DataService] Warning: CSV file not found at {self.filepath}")
            return None
            
        try:
            df = pd.read_csv(self.filepath)
            _csv_cache[self.filepath] = df
            print(f"[DataService] Loaded CSV dataset: {self.filename} ({len(df)} rows)")
            return df
        except Exception as e:
            print(f"[DataService] Error reading CSV file {self.filepath}: {e}")
            return None

    def get_data(self, **kwargs) -> Optional[Dict[str, Any]]:
        df = self._load_csv()
        if df is None or df.empty:
            return None

        # Build case-insensitive map of dataframe columns
        col_map = {col.lower(): col for col in df.columns}
        matched_df = df.copy()

        for raw_k, raw_val in kwargs.items():
            k_lower = raw_k.strip().lower()
            target_col = None
            if k_lower in col_map:
                target_col = col_map[k_lower]
            elif k_lower in ["country", "market", "nation"]:
                for alt in ["country", "economy", "countrynewwb", "tablename", "cabr"]:
                    if alt in col_map:
                        target_col = col_map[alt]
                        break
            if not target_col:
                continue

            val_str = str(raw_val).strip()
            if not val_str:
                continue

            val_lower = val_str.lower()
            # Clean punctuation from search string
            val_clean = re.sub(r"[^\w\s]", "", val_lower).strip()

            # If searching by Country, resolve aliases
            if k_lower in ["country", "market", "nation"]:
                if val_clean in COUNTRY_ALIASES:
                    val_lower = COUNTRY_ALIASES[val_clean].lower()
                    val_clean = re.sub(r"[^\w\s]", "", val_lower).strip()

            col_series = matched_df[target_col].astype(str).str.strip()
            col_series_lower = col_series.str.lower()
            col_series_clean = col_series_lower.str.replace(r"[^\w\s]", "", regex=True)

            # 1. Exact match (case-insensitive)
            exact_mask = (col_series_lower == val_lower) | (col_series_clean == val_clean)
            if exact_mask.any():
                matched_df = matched_df[exact_mask]
                continue

            # 2. Substring match: dataframe value contained in search string OR search string contained in dataframe value
            # e.g., "European Commercial Satellite Launch Market in Germany" contains "germany"
            sub_mask = col_series_lower.str.contains(re.escape(val_clean), regex=True, na=False)
            if not sub_mask.any():
                # Check if input string contains the country/company name in the dataset
                contained_mask = col_series_clean.apply(
                    lambda x: bool(x and len(x) >= 3 and x in val_clean)
                )
                if contained_mask.any():
                    sub_mask = contained_mask

            if sub_mask.any():
                matched_df = matched_df[sub_mask]
                continue

            # 3. Word token overlap match (e.g. "Apple Inc" vs "Apple", "Microsoft Corp" vs "Microsoft")
            val_tokens = set(val_clean.split())
            if val_tokens:
                token_mask = col_series_clean.apply(
                    lambda x: bool(set(str(x).split()) & val_tokens)
                )
                if token_mask.any():
                    matched_df = matched_df[token_mask]
                    continue

            # If no matches found for this filter, return None (or fallback if empty)
            return None

        if matched_df.empty:
            return None

        # Return first matched row as a clean dictionary
        row = matched_df.iloc[0]
        res = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                res[col] = None
            else:
                if isinstance(val, (int, float, str, bool)):
                    res[col] = val
                else:
                    res[col] = str(val)
        return res

class APIDataProvider(DataProvider):
    """Queries external REST APIs with timeout, caching, and fallback handling."""
    def __init__(self, endpoint_url: str, api_key_env: Optional[str] = None):
        self.endpoint_url = endpoint_url
        self.api_key_env = api_key_env

    def get_data(self, **kwargs) -> Optional[Dict[str, Any]]:
        api_key = os.getenv(self.api_key_env) if self.api_key_env else None
        
        if not self.endpoint_url or "api.example.com" in self.endpoint_url:
            return None
            
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        try:
            response = requests.get(self.endpoint_url, params=kwargs, headers=headers, timeout=4.0)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"[DataService] API request failed: {e}")
            return None

class DataRegistry:
    """Registry that maps data types to list of providers."""
    def __init__(self):
        self._registry: Dict[str, List[DataProvider]] = {}

    def register(self, data_type: str, provider: DataProvider):
        normalized_type = data_type.strip().lower()
        if normalized_type not in self._registry:
            self._registry[normalized_type] = []
        self._registry[normalized_type].append(provider)

    def get_providers(self, data_type: str) -> List[DataProvider]:
        return self._registry.get(data_type.strip().lower(), [])

# Instantiate and configure the global registry
registry = DataRegistry()

# 1. Register All Local CSV Data Providers
registry.register("Market Data", CSVDataProvider("market_data.csv"))
registry.register("Logistics Data", CSVDataProvider("market_data.csv"))
registry.register("Competition Data", CSVDataProvider("competition_data.csv"))
registry.register("Research Data", CSVDataProvider("research_data.csv"))
registry.register("Legal Data", CSVDataProvider("legal_data.csv"))
registry.register("Country Data", CSVDataProvider("country_data.csv"))
registry.register("Risk Data", CSVDataProvider("risk_data.csv"))
registry.register("Financial Data", CSVDataProvider("financial_data.csv"))
registry.register("Entrepreneurship Data", CSVDataProvider("entrepreneurship_data.csv"))

# 2. Register External API Providers (Placeholders for user API integrations)
registry.register("Market Data", APIDataProvider("https://api.example.com/market"))
registry.register("Country Data", APIDataProvider("https://api.example.com/country"))

def get_data(data_type: str, **kwargs) -> dict:
    """
    Central data access entrypoint.
    Queries all registered data providers for the category, merges results,
    caches calculations, and filters missing/none values.
    
    Returns a dict schema:
    {
        "status": "success" | "unavailable",
        "source": str,
        "data": dict
    }
    """
    global _query_cache
    
    cache_key = f"{data_type.strip().lower()}:{sorted(kwargs.items())}"
    if cache_key in _query_cache:
        return _query_cache[cache_key]
        
    providers = registry.get_providers(data_type)
    if not providers:
        result = {"status": "unavailable", "source": "None", "data": {}}
        _query_cache[cache_key] = result
        return result
        
    merged_data = {}
    sources = []
    
    for provider in providers:
        try:
            prov_data = provider.get_data(**kwargs)
            if prov_data:
                merged_data.update(prov_data)
                source_name = "CSV" if isinstance(provider, CSVDataProvider) else "API"
                sources.append(source_name)
        except Exception as e:
            print(f"[DataService] Provider execution error: {e}")
            
    if merged_data:
        source_str = "Merged(" + "+".join(set(sources)) + ")" if len(set(sources)) > 1 else sources[0]
        clean_data = {k: v for k, v in merged_data.items() if v is not None}
        result = {
            "status": "success",
            "source": source_str,
            "data": clean_data
        }
    else:
        result = {
            "status": "unavailable",
            "source": "None",
            "data": {}
        }
        
    _query_cache[cache_key] = result
    return result
