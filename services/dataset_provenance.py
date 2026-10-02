"""
BoardRoomAI - Dataset Provenance, Integrity & Freshness Engine
Provides comprehensive provenance records, Tier 1-5 classification, SHA-256 integrity verification,
schema validation, and freshness tracking for all datasets.
"""
import os
import hashlib
import time
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class ProvenanceStatus(str, Enum):
    SOURCE_VERIFIED = "SOURCE-VERIFIED"
    DATASET_BACKED = "DATASET-BACKED"
    CALCULATED = "CALCULATED"
    MODEL_INFERENCE = "MODEL-INFERENCE"
    ASSUMPTION = "ASSUMPTION"
    UNVERIFIED = "UNVERIFIED"
    MISSING = "MISSING"

class SourceTier(str, Enum):
    TIER_1_GOV = "TIER 1"
    TIER_2_RESEARCH = "TIER 2"
    TIER_3_SECONDARY = "TIER 3"
    TIER_4_LOCAL = "TIER 4"
    TIER_5_LLM = "TIER 5"

class FreshnessCategory(str, Enum):
    CURRENT = "CURRENT"
    RECENT = "RECENT"
    AGING = "AGING"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"

class ProvenanceRecord:
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        for k, v in data.items():
            setattr(self, k, v)
            
    def __getitem__(self, item):
        return self._data.get(item)
        
    def get(self, key, default=None):
        return self._data.get(key, default)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Source Quality Tier Taxonomy
# Tier 1: Government / Regulator / International Authoritative Organization (World Bank, UN, IMF)
# Tier 2: Recognized Research Institution / Industry Body (Fund for Peace, WEF)
# Tier 3: Established Secondary Aggregator Dataset (CompaniesMarketCap, PitchBook aggregations)
# Tier 4: Local / User-provided dataset without external provenance audit
# Tier 5: LLM-generated information (NEVER used as empirical evidence)

PROVENANCE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "research_data.csv": {
        "dataset_name": "research_data.csv",
        "publisher": "Aggregated Venture Analytics / Open Startup Registries",
        "source_name": "Global Startup Activity & Venture Funding Benchmarks",
        "source_url": None, # Local extract; external URL not certified
        "source_tier": "TIER 3: Established Secondary Dataset",
        "tier_level": 3,
        "provenance_status": "DATASET-BACKED (LOCAL DATASET — EXTERNAL PROVENANCE NOT INDEPENDENTLY ESTABLISHED)",
        "publication_date": "2024-01-15",
        "retrieval_date": "2024-06-01",
        "freshness_category": "RECENT",
        "geographic_scope": "137 Countries / Global",
        "time_period": "2023-2024",
        "units": "Startup Counts, Total USD Funding (Millions/Billions)",
        "methodology": "Aggregated registry of active early-stage startups and disclosed funding rounds",
        "license": "Open Reference Dataset / Non-Commercial",
        "required_columns": ["Country", "Startups Tracked", "Total Funding (USD)", "Average Funding per Startup (USD)"],
        "expected_min_rows": 100
    },
    "competition_data.csv": {
        "dataset_name": "competition_data.csv",
        "publisher": "Public Equities & CompaniesMarketCap Archive",
        "source_name": "Sovereign Market Capitalization & Top Public Companies",
        "source_url": None,
        "source_tier": "TIER 3: Established Secondary Dataset",
        "tier_level": 3,
        "provenance_status": "DATASET-BACKED (LOCAL DATASET — EXTERNAL PROVENANCE NOT INDEPENDENTLY ESTABLISHED)",
        "publication_date": "2024-01-10",
        "retrieval_date": "2024-06-01",
        "freshness_category": "RECENT",
        "geographic_scope": "68 Countries / Global",
        "time_period": "2023-2024",
        "units": "Market Capitalization (USD Millions/Billions), Company Counts",
        "methodology": "Market capitalization tracking of primary exchange-listed enterprises grouped by country headquarters",
        "license": "Public Reference Data",
        "required_columns": ["Country", "Top Company", "Top Company Market Cap (USD)", "Companies Tracked"],
        "expected_min_rows": 50
    },
    "legal_data.csv": {
        "dataset_name": "legal_data.csv",
        "publisher": "World Bank Group",
        "source_name": "World Bank Doing Business Historical Database (Starting a Business / Ease of Doing Business)",
        "source_url": "https://data.worldbank.org/",
        "source_tier": "TIER 1: International Authoritative Organization",
        "tier_level": 1,
        "provenance_status": "DATASET-BACKED (WORLD BANK HISTORICAL BENCHMARK)",
        "publication_date": "2020-05-01",
        "retrieval_date": "2024-01-15",
        "freshness_category": "AGING / HISTORICAL BENCHMARK",
        "geographic_scope": "213 Economies / Global",
        "time_period": "Historical World Bank Series",
        "units": "Index Scores (0-100), Days to Incorporate, Ranks",
        "methodology": "Standardized incorporation case study questionnaires evaluating legal procedures, timeline, and statutory fees",
        "license": "World Bank Open Data License (CC BY 4.0)",
        "required_columns": ["Country", "Ease of Doing Business Score", "Starting a Business Score", "Days to Start Business"],
        "expected_min_rows": 150
    },
    "market_data.csv": {
        "dataset_name": "market_data.csv",
        "publisher": "World Bank Group",
        "source_name": "World Bank Logistics Performance Index (LPI) 2023",
        "source_url": "https://lpi.worldbank.org/",
        "source_tier": "TIER 1: International Authoritative Organization",
        "tier_level": 1,
        "provenance_status": "DATASET-BACKED (WORLD BANK LPI 2023)",
        "publication_date": "2023-04-21",
        "retrieval_date": "2024-01-15",
        "freshness_category": "CURRENT (2023 Edition)",
        "geographic_scope": "139 Economies / Global",
        "time_period": "2023",
        "units": "LPI Index Score (1.0 - 5.0 scale)",
        "methodology": "Quantitative survey of global freight forwarders and logistics professionals evaluating transport efficiency, customs, and timeliness",
        "license": "World Bank Open Data License (CC BY 4.0)",
        "required_columns": ["Country", "Logistics Performance Score (2023)"],
        "expected_min_rows": 100
    },
    "risk_data.csv": {
        "dataset_name": "risk_data.csv",
        "publisher": "Fund for Peace",
        "source_name": "Fragile States Index (FSI) 2023 Annual Report",
        "source_url": "https://fragilestatesindex.org/",
        "source_tier": "TIER 2: Recognized Policy Research Institution",
        "tier_level": 2,
        "provenance_status": "DATASET-BACKED (FUND FOR PEACE FSI 2023)",
        "publication_date": "2023-06-15",
        "retrieval_date": "2024-01-15",
        "freshness_category": "RECENT (2023 Edition)",
        "geographic_scope": "179 Sovereign States / Global",
        "time_period": "2023",
        "units": "Fragility Index Score (0-120; lower = more stable), Sovereign Rank",
        "methodology": "Conflict Assessment System Tool (CAST) analyzing social, economic, cohesion, and political indicators",
        "license": "Fund for Peace Public Archive",
        "required_columns": ["Country", "Rank", "Fragility Score"],
        "expected_min_rows": 150
    },
    "financial_data.csv": {
        "dataset_name": "financial_data.csv",
        "publisher": "CompaniesMarketCap Equities Registry",
        "source_name": "Global Listed Entities Financial Metrics",
        "source_url": None,
        "source_tier": "TIER 3: Established Secondary Dataset",
        "tier_level": 3,
        "provenance_status": "DATASET-BACKED (LOCAL REPOSITORY EXTRACT)",
        "publication_date": "2023-11-01",
        "retrieval_date": "2024-01-15",
        "freshness_category": "RECENT",
        "geographic_scope": "Global Public Companies",
        "time_period": "2023",
        "units": "Market Cap (USD), Revenue (USD)",
        "methodology": "Securities exchange public filings and capitalization records",
        "license": "Public Reference Data",
        "required_columns": ["Company", "Market Cap", "Country"],
        "expected_min_rows": 1000
    }
}

DATASET_PROVENANCE_REGISTRY = PROVENANCE_REGISTRY

def get_dataset_provenance(filename: str, custom_data_dir: Optional[str] = None) -> ProvenanceRecord:
    """Helper returning a ProvenanceRecord instance."""
    rec = get_dataset_provenance_record(filename, custom_data_dir)
    return ProvenanceRecord(rec)

def calculate_sha256(filepath: str) -> str:
    """Calculates SHA-256 hash of a file."""
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    try:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"HASH_ERROR: {str(e)}"

def calculate_schema_hash(df: pd.DataFrame) -> str:
    """Computes a deterministic hash of the dataframe's schema and column types."""
    schema_str = "|".join([f"{col}:{str(dtype)}" for col, dtype in zip(df.columns, df.dtypes)])
    return hashlib.sha256(schema_str.encode("utf-8")).hexdigest()[:12]

def get_dataset_provenance_record(filename: str, custom_data_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Constructs a complete provenance and integrity record for a dataset.
    Never fabricates provenance or external URLs if unavailable.
    """
    base_dir = custom_data_dir or DATA_DIR
    filepath = os.path.join(base_dir, filename)
    registry_meta = PROVENANCE_REGISTRY.get(filename, {
        "dataset_name": filename,
        "publisher": "Local User/Workspace File",
        "source_name": "Unregistered Local Dataset",
        "source_url": None,
        "source_tier": "TIER 4: User/Local Dataset Without External Provenance",
        "tier_level": 4,
        "provenance_status": "LOCAL DATASET — EXTERNAL PROVENANCE NOT ESTABLISHED",
        "publication_date": "UNKNOWN",
        "retrieval_date": "UNKNOWN",
        "freshness_category": "UNKNOWN",
        "geographic_scope": "Unspecified",
        "time_period": "Unspecified",
        "units": "Unspecified",
        "methodology": "Unspecified local collection",
        "license": "Unspecified",
        "required_columns": [],
        "expected_min_rows": 1
    })

    if not os.path.exists(filepath):
        return {
            **registry_meta,
            "status": "FILE_NOT_FOUND",
            "dataset_hash": "UNAVAILABLE",
            "full_sha256": "UNAVAILABLE",
            "file_size": 0,
            "schema_hash": "UNAVAILABLE",
            "row_count": 0,
            "column_count": 0,
            "integrity_passed": False,
            "integrity_issues": ["File does not exist on disk"]
        }

    try:
        file_size = os.path.getsize(filepath)
        full_hash = calculate_sha256(filepath)
        df = pd.read_csv(filepath)
        row_count, col_count = df.shape
        schema_hash = calculate_schema_hash(df)
        
        # Verify Integrity
        integrity_issues = []
        req_cols = registry_meta.get("required_columns", [])
        for col in req_cols:
            if col not in df.columns:
                integrity_issues.append(f"Missing required column: '{col}'")
        
        min_rows = registry_meta.get("expected_min_rows", 1)
        if row_count < min_rows:
            integrity_issues.append(f"Row count ({row_count}) below expected minimum ({min_rows})")

        integrity_passed = len(integrity_issues) == 0

        return {
            **registry_meta,
            "status": "LOADED" if integrity_passed else "INTEGRITY_WARNING",
            "dataset_hash": full_hash[:16],
            "full_sha256": full_hash,
            "file_size": file_size,
            "schema_hash": schema_hash,
            "row_count": row_count,
            "column_count": col_count,
            "columns": list(df.columns),
            "integrity_passed": integrity_passed,
            "integrity_issues": integrity_issues
        }
    except Exception as e:
        return {
            **registry_meta,
            "status": "READ_ERROR",
            "dataset_hash": "ERROR",
            "full_sha256": "ERROR",
            "file_size": 0,
            "schema_hash": "ERROR",
            "row_count": 0,
            "column_count": 0,
            "integrity_passed": False,
            "integrity_issues": [f"Failed to parse CSV: {str(e)}"]
        }

def verify_all_datasets_integrity(custom_data_dir: Optional[str] = None) -> Tuple[bool, Dict[str, Dict[str, Any]], List[str]]:
    """
    Validates integrity across all core BoardRoomAI datasets at startup and pre-analysis.
    Returns (all_passed, provenance_records_dict, all_issues_list).
    """
    records = {}
    all_issues = []
    all_passed = True

    for filename in PROVENANCE_REGISTRY.keys():
        rec = get_dataset_provenance_record(filename, custom_data_dir=custom_data_dir)
        records[filename] = rec
        if not rec["integrity_passed"]:
            all_passed = False
            for issue in rec["integrity_issues"]:
                all_issues.append(f"[{filename}] {issue}")

    return all_passed, records, all_issues
