"""
BoardRoomAI - Complete Dataset Cleaning Script
Converts raw downloaded datasets into the clean CSVs expected by BoardRoomAI agents:
1. financial_data.csv (Market Cap, Revenue for 6000+ companies)
2. risk_data.csv (Fragility Score, Rank, Security, Economy, Legitimacy)
3. market_data.csv (World Bank Logistics Performance Index Score 1-5)
4. country_data.csv (Region, Income Group)
5. competition_data.csv (Top Company, Symbol, Market Cap, Companies Tracked)
6. research_data.csv (Startup ecosystem funding, tracked startups, average funding)
7. legal_data.csv (Ease of doing business rank/score, enforcing contracts, start business)
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def clean_financial_data():
    """
    Source: company_data.csv (100 companies with Revenue) +
    companiesmarketcap.com...csv (6,000 global companies with Market Cap and Symbol)
    """
    path_main = os.path.join(DATA_DIR, "company_data.csv")
    path_mcap = os.path.join(
        DATA_DIR,
        "companiesmarketcap.com - Companies ranked by Market Cap - CompaniesMarketCap.com.csv",
    )

    records = {}

    # 1. Load 6,000 global companies from marketcap file
    if os.path.exists(path_mcap):
        df_mcap = pd.read_csv(path_mcap)
        for _, row in df_mcap.iterrows():
            name = str(row.get("Name", "")).strip()
            symbol = str(row.get("Symbol", "")).strip()
            mcap_val = row.get("marketcap")

            if not name or pd.isna(name):
                continue

            # Format market cap nicely
            mcap_str = "N/A"
            if pd.notna(mcap_val):
                try:
                    val_num = float(mcap_val)
                    if val_num >= 1e12:
                        mcap_str = f"${val_num / 1e12:.2f}T"
                    elif val_num >= 1e9:
                        mcap_str = f"${val_num / 1e9:.2f}B"
                    elif val_num >= 1e6:
                        mcap_str = f"${val_num / 1e6:.2f}M"
                    else:
                        mcap_str = f"${val_num:,.0f}"
                except Exception:
                    mcap_str = str(mcap_val)

            records[name.lower()] = {
                "Company": name,
                "Symbol": symbol,
                "Market Cap": mcap_str,
                "Revenue": "N/A",
                "Country": str(row.get("country", "")).strip(),
            }

    # 2. Overlay richer company_data.csv (which contains verified Revenue)
    if os.path.exists(path_main):
        df_comp = pd.read_csv(path_main)
        for _, row in df_comp.iterrows():
            name = str(row.get("Company Name", "")).strip()
            if not name or pd.isna(name):
                continue
            mcap = str(row.get("Market Cap", "N/A")).strip()
            rev = str(row.get("Revenue", "N/A")).strip()

            key = name.lower()
            if key in records:
                records[key]["Market Cap"] = mcap
                records[key]["Revenue"] = rev
            else:
                records[key] = {
                    "Company": name,
                    "Symbol": "",
                    "Market Cap": mcap,
                    "Revenue": rev,
                    "Country": "Global",
                }

    final_df = pd.DataFrame(list(records.values()))
    out_path = os.path.join(DATA_DIR, "financial_data.csv")
    final_df.to_csv(out_path, index=False)
    print(f"[OK] financial_data.csv written ({len(final_df)} rows) -> matches on 'Company'")


def clean_risk_data():
    """Source: FSI-2023-DOWNLOAD.xlsx (Fragile States Index)"""
    path = os.path.join(DATA_DIR, "FSI-2023-DOWNLOAD.xlsx")
    df = pd.read_excel(path)

    keep_cols = [
        "Country", "Rank", "Total",
        "C1: Security Apparatus", "E1: Economy",
        "P1: State Legitimacy", "X1:External Intervention"
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols]

    df = df.rename(columns={
        "Total": "Fragility Score",
        "X1:External Intervention": "External Intervention Score"
    })

    out_path = os.path.join(DATA_DIR, "risk_data.csv")
    df.to_csv(out_path, index=False)
    print(f"[OK] risk_data.csv written ({len(df)} rows) -> matches on 'Country'")


def clean_market_data():
    """
    Source: LPIEXCEL.xlsx (World Bank Logistics Performance Index)
    Filters specifically for 'Overall score' (1 to 5 scale), avoiding ranks.
    """
    path = os.path.join(DATA_DIR, "LPIEXCEL.xlsx")
    df = pd.read_excel(path)

    # Filter for Overall Score (1=low to 5=high)
    mask = df["Indicator Name"].str.contains("Overall score", case=False, na=False) & (
        ~df["Indicator Name"].str.contains("bound", case=False, na=False)
    )
    overall = df[mask].copy()

    overall = overall[["Country Name", "Country Code", "2023"]].copy()
    overall = overall.rename(columns={
        "Country Name": "Country",
        "2023": "Logistics Performance Score (2023)"
    })
    overall = overall.dropna(subset=["Logistics Performance Score (2023)"])

    out_path = os.path.join(DATA_DIR, "market_data.csv")
    overall.to_csv(out_path, index=False)
    print(f"[OK] market_data.csv written ({len(overall)} rows) -> matches on 'Country'")


def clean_country_data():
    """Source: Metadata_Country_API_LP.LPI.OVRL.XQ...csv (Region, Income Group by country)"""
    path = os.path.join(
        DATA_DIR, "Metadata_Country_API_LP.LPI.OVRL.XQ_DS2_en_csv_v2_4688.csv"
    )
    df = pd.read_csv(path)

    df = df.rename(columns={"TableName": "Country"})
    df = df[["Country", "Country Code", "Region", "IncomeGroup"]]
    df = df.dropna(subset=["Region"])

    out_path = os.path.join(DATA_DIR, "country_data.csv")
    df.to_csv(out_path, index=False)
    print(f"[OK] country_data.csv written ({len(df)} rows) -> matches on 'Country'")


def clean_competition_data():
    """
    Source: companiesmarketcap.com...csv
    Computes top market leader per country, symbol, market cap, and total tracked companies.
    """
    path = os.path.join(
        DATA_DIR,
        "companiesmarketcap.com - Companies ranked by Market Cap - CompaniesMarketCap.com.csv",
    )
    df = pd.read_csv(path)

    results = []
    # Group by country
    for country, group in df.groupby("country"):
        country_clean = str(country).strip()
        if not country_clean or country_clean.lower() == "nan":
            continue

        sorted_group = group.sort_values(by="Rank", ascending=True)
        top_row = sorted_group.iloc[0]

        top_company = str(top_row.get("Name", "N/A"))
        top_symbol = str(top_row.get("Symbol", "N/A"))
        mcap_val = top_row.get("marketcap")

        if pd.notna(mcap_val):
            val_num = float(mcap_val)
            if val_num >= 1e12:
                mcap_str = f"${val_num / 1e12:.2f}T"
            elif val_num >= 1e9:
                mcap_str = f"${val_num / 1e9:.2f}B"
            else:
                mcap_str = f"${val_num:,.0f}"
        else:
            mcap_str = "N/A"

        top_3_names = sorted_group["Name"].head(3).tolist()
        top_competitors_str = ", ".join(top_3_names)

        results.append({
            "Country": country_clean,
            "Top Company": top_company,
            "Top Company Symbol": top_symbol,
            "Top Company Market Cap (USD)": mcap_str,
            "Companies Tracked": len(sorted_group),
            "Top Competitors": top_competitors_str,
        })

    out_df = pd.DataFrame(results)
    out_path = os.path.join(DATA_DIR, "competition_data.csv")
    out_df.to_csv(out_path, index=False)
    print(f"[OK] competition_data.csv written ({len(out_df)} rows) -> matches on 'Country'")


def clean_research_data():
    """
    Source: big_startup_secsees_dataset.csv (66,000+ startups)
    Aggregates startup ecosystem funding, counts, and averages by country.
    """
    startup_path = os.path.join(DATA_DIR, "big_startup_secsees_dataset.csv")
    country_path = os.path.join(
        DATA_DIR, "Metadata_Country_API_LP.LPI.OVRL.XQ_DS2_en_csv_v2_4688.csv"
    )

    df_startups = pd.read_csv(startup_path, low_memory=False)

    # Clean funding column
    df_startups["funding_cleaned"] = pd.to_numeric(
        df_startups["funding_total_usd"].astype(str).str.replace(",", "").str.strip(),
        errors="coerce",
    ).fillna(0.0)

    # Build Country Code -> Country Name mapping
    code_to_country = {}
    if os.path.exists(country_path):
        df_c = pd.read_csv(country_path)
        for _, r in df_c.iterrows():
            code = str(r.get("Country Code", "")).strip().upper()
            cname = str(r.get("TableName", "")).strip()
            if code and cname:
                code_to_country[code] = cname

    # Additional standard ISO codes
    code_to_country.update({
        "USA": "United States",
        "GBR": "United Kingdom",
        "CAN": "Canada",
        "IND": "India",
        "CHN": "China",
        "FRA": "France",
        "DEU": "Germany",
        "ISR": "Israel",
        "ESP": "Spain",
        "AUS": "Australia",
        "NLD": "Netherlands",
        "RUS": "Russian Federation",
        "SGP": "Singapore",
        "SWE": "Sweden",
        "BRA": "Brazil",
        "IRL": "Ireland",
        "JPN": "Japan",
        "ITA": "Italy",
        "KOR": "Korea, Rep.",
        "CHE": "Switzerland",
    })

    results = []
    for code, group in df_startups.groupby("country_code"):
        code_clean = str(code).strip().upper()
        if not code_clean or code_clean == "NAN":
            continue

        cname = code_to_country.get(code_clean, code_clean)
        count = len(group)
        tot_funding = group["funding_cleaned"].sum()
        avg_funding = tot_funding / max(count, 1)

        # Format funding nicely
        if tot_funding >= 1e9:
            tot_str = f"{tot_funding / 1e9:.2f} Billion"
        elif tot_funding >= 1e6:
            tot_str = f"{tot_funding / 1e6:.2f} Million"
        else:
            tot_str = f"{tot_funding:,.0f}"

        if avg_funding >= 1e6:
            avg_str = f"{avg_funding / 1e6:.2f} Million"
        else:
            avg_str = f"{avg_funding:,.0f}"

        results.append({
            "Country": cname,
            "Country Code": code_clean,
            "Startups Tracked": f"{count:,}",
            "Total Funding (USD)": tot_str,
            "Average Funding per Startup (USD)": avg_str,
        })

    out_df = pd.DataFrame(results)
    out_path = os.path.join(DATA_DIR, "research_data.csv")
    out_df.to_csv(out_path, index=False)
    print(f"[OK] research_data.csv written ({len(out_df)} rows) -> matches on 'Country'")


def clean_legal_data():
    """
    Source: Historical-data---COMPLETE-dataset-with-scores.xlsx
    World Bank Ease of Doing Business dataset (Year 2020, header on row 4 / index 3).
    """
    path = os.path.join(
        DATA_DIR, "Historical-data---COMPLETE-dataset-with-scores.xlsx"
    )
    df = pd.read_excel(path, sheet_name="All Data", header=3)

    # Filter for 2020 latest data
    df_2020 = df[df["DB Year"] == 2020].copy()

    df_2020 = df_2020.rename(columns={
        "Economy": "Country",
        "Country code": "Country Code",
        "Ease of doing business rank": "Ease of Doing Business Rank",
        "Ease of doing business score (DB17-20 methodology)": "Ease of Doing Business Score",
        "Rank-Starting a business": "Starting a Business Rank",
        "Score-Starting a business": "Starting a Business Score",
        "Time - Men (days)": "Days to Start Business",
        "Score-Enforcing contracts (DB17-20 methodology)": "Enforcing Contracts Score",
        "Score-Resolving insolvency": "Resolving Insolvency Score",
        "Region": "Region",
        "Income group": "IncomeGroup",
    })

    cols = [
        "Country", "Country Code", "Region", "IncomeGroup",
        "Ease of Doing Business Rank", "Ease of Doing Business Score",
        "Starting a Business Rank", "Starting a Business Score",
        "Days to Start Business", "Enforcing Contracts Score",
        "Resolving Insolvency Score",
    ]
    cols = [c for c in cols if c in df_2020.columns]
    res_df = df_2020[cols].copy()

    # Round float columns
    for col in ["Ease of Doing Business Score", "Starting a Business Score", "Enforcing Contracts Score", "Resolving Insolvency Score"]:
        if col in res_df.columns:
            res_df[col] = res_df[col].apply(lambda x: round(x, 1) if pd.notna(x) else x)

    out_path = os.path.join(DATA_DIR, "legal_data.csv")
    res_df.to_csv(out_path, index=False)
    print(f"[OK] legal_data.csv written ({len(res_df)} rows) -> matches on 'Country'")


if __name__ == "__main__":
    print("Cleaning and generating BoardRoomAI datasets...\n")
    clean_financial_data()
    clean_risk_data()
    clean_market_data()
    clean_country_data()
    clean_competition_data()
    clean_research_data()
    clean_legal_data()
    print("\nAll datasets generated successfully!")