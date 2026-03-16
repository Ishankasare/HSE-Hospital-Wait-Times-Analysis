# ============================================================
# HSE Hospital Wait Times — Data Cleaning Pipeline
# ============================================================
# Author:      Ishan Kasare
# GitHub:      https://github.com/Ishankasare/HSE-Hospital-Wait-Times-Analysis
# LinkedIn:    https://www.linkedin.com/in/ishan-kasare/
#
# Description:
#   Cleans and merges all downloaded NTPF CSV files into
#   3 unified analytical tables:
#     - op_waiting.csv     : Outpatient waiting list by hospital/month
#     - ipdc_waiting.csv   : Inpatient/Day Case by hospital/month
#     - specialty_waiting.csv : All waits by specialty over time
#
# Run AFTER download_data.py:
#   python src/clean_data.py
# ============================================================

import pandas as pd
import os
import glob
import logging
import sqlite3
import re

os.makedirs("data/processed", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/cleaning.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

DB_PATH = "data/hse_waits.db"


# ── Wait band columns used by NTPF ──────────────────────────
# These are the standard column names in NTPF open data files
WAIT_BANDS = [
    "0-6 Months", "6-12 Months", "12-18 Months",
    "18+ Months", "Grand Total"
]

# Alternative older column names used pre-2021
WAIT_BANDS_ALT = [
    "0 - 3 Months", "3 - 6 Months", "6 - 9 Months",
    "9 - 12 Months", "12 - 15 Months", "15 - 18 Months",
    "18+ Months", "Grand Total"
]


def detect_columns(df: pd.DataFrame) -> dict:
    """Detect which column names this file uses."""
    cols = [c.strip() for c in df.columns]
    mapping = {}

    # Try to find hospital/group column
    for candidate in ["Hospital", "Group/Hospital", "Hospital Name", "Group", "Hospital Group"]:
        if candidate in cols:
            mapping["hospital"] = candidate
            break

    # Try to find specialty column
    for candidate in ["Specialty", "Speciality", "Specialty Name"]:
        if candidate in cols:
            mapping["specialty"] = candidate
            break

    # Try to find archive date / month column
    for candidate in ["Archive Date", "ArchiveDate", "Month Year", "Report Date", "Date"]:
        if candidate in cols:
            mapping["date"] = candidate
            break

    # Find total column
    for candidate in ["Grand Total", "Total", "Total Waiting"]:
        if candidate in cols:
            mapping["total"] = candidate
            break

    return mapping


def clean_numeric(val) -> float:
    """Convert a value to numeric, handling commas and blanks."""
    if pd.isna(val):
        return 0.0
    s = str(val).replace(",", "").strip()
    if s in ["", "-", "N/A", "n/a", "*"]:
        return 0.0
    try:
        return float(s)
    except:
        return 0.0


def parse_ntpf_date(val) -> pd.Timestamp:
    """Parse NTPF date formats — they use DD/MM/YYYY."""
    try:
        return pd.to_datetime(str(val), dayfirst=True)
    except:
        return pd.NaT


def extract_year_from_filename(filename: str) -> int:
    """Extract year from filename like OP_Hospital_2024.csv"""
    match = re.search(r"(\d{4})", os.path.basename(filename))
    return int(match.group(1)) if match else 0


def load_op_files() -> pd.DataFrame:
    """Load and merge all Outpatient (OP) by hospital files."""
    log.info("Loading Outpatient files...")
    files = sorted(glob.glob("data/raw/OP_Hospital_*.csv"))
    frames = []

    for f in files:
        year = extract_year_from_filename(f)
        try:
            df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
            df.columns = [c.strip() for c in df.columns]
            col_map = detect_columns(df)

            if not col_map.get("hospital"):
                log.warning(f"No hospital column found in {f}, skipping")
                continue

            # Standardise to common schema
            out = pd.DataFrame()
            out["hospital"] = df[col_map["hospital"]].astype(str).str.strip()
            out["specialty"] = df[col_map["specialty"]].astype(str).str.strip() if col_map.get("specialty") else "All Specialties"
            out["date"] = df[col_map["date"]].apply(parse_ntpf_date) if col_map.get("date") else pd.NaT
            out["year"] = year
            out["wait_type"] = "Outpatient"

            # Total waiting
            if col_map.get("total"):
                out["total_waiting"] = df[col_map["total"]].apply(clean_numeric)
            else:
                # Sum all numeric columns as fallback
                num_cols = df.select_dtypes(include="number").columns
                out["total_waiting"] = df[num_cols].sum(axis=1)

            # Wait band columns — try to find them
            for band in ["0-6 Months", "6-12 Months", "12-18 Months", "18+ Months"]:
                if band in df.columns:
                    out[band] = df[band].apply(clean_numeric)
                else:
                    out[band] = 0.0

            out["pct_over_12m"] = out.apply(
                lambda r: round((r["18+ Months"] / r["total_waiting"] * 100), 1)
                if r["total_waiting"] > 0 else 0.0, axis=1
            )

            frames.append(out)
            log.info(f"Loaded OP Hospital {year}: {len(out)} rows")

        except Exception as e:
            log.error(f"Error loading {f}: {e}")

    if not frames:
        log.warning("No OP hospital files loaded")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result = result[result["hospital"].str.lower() != "nan"]
    result = result[result["total_waiting"] > 0]
    log.info(f"Total OP rows after merge: {len(result)}")
    return result


def load_ipdc_files() -> pd.DataFrame:
    """Load and merge all Inpatient/Day Case (IPDC) by hospital files."""
    log.info("Loading IPDC files...")
    files = sorted(glob.glob("data/raw/IPDC_Hospital_*.csv"))
    frames = []

    for f in files:
        year = extract_year_from_filename(f)
        try:
            df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
            df.columns = [c.strip() for c in df.columns]
            col_map = detect_columns(df)

            if not col_map.get("hospital"):
                log.warning(f"No hospital column in {f}, skipping")
                continue

            out = pd.DataFrame()
            out["hospital"] = df[col_map["hospital"]].astype(str).str.strip()
            out["specialty"] = df[col_map["specialty"]].astype(str).str.strip() if col_map.get("specialty") else "All Specialties"
            out["date"] = df[col_map["date"]].apply(parse_ntpf_date) if col_map.get("date") else pd.NaT
            out["year"] = year
            out["wait_type"] = "Inpatient/Day Case"

            if col_map.get("total"):
                out["total_waiting"] = df[col_map["total"]].apply(clean_numeric)
            else:
                num_cols = df.select_dtypes(include="number").columns
                out["total_waiting"] = df[num_cols].sum(axis=1)

            for band in ["0-6 Months", "6-12 Months", "12-18 Months", "18+ Months"]:
                if band in df.columns:
                    out[band] = df[band].apply(clean_numeric)
                else:
                    out[band] = 0.0

            out["pct_over_12m"] = out.apply(
                lambda r: round((r["18+ Months"] / r["total_waiting"] * 100), 1)
                if r["total_waiting"] > 0 else 0.0, axis=1
            )

            frames.append(out)
            log.info(f"Loaded IPDC Hospital {year}: {len(out)} rows")

        except Exception as e:
            log.error(f"Error loading {f}: {e}")

    if not frames:
        log.warning("No IPDC files loaded")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result = result[result["hospital"].str.lower() != "nan"]
    result = result[result["total_waiting"] > 0]
    log.info(f"Total IPDC rows after merge: {len(result)}")
    return result


def load_specialty_files() -> pd.DataFrame:
    """Load and merge all specialty-level files."""
    log.info("Loading Specialty files...")
    files = sorted(glob.glob("data/raw/OP_Specialty_*.csv") + glob.glob("data/raw/IPDC_Specialty_*.csv"))
    frames = []

    for f in files:
        year = extract_year_from_filename(f)
        wait_type = "Outpatient" if "OP_" in os.path.basename(f) else "Inpatient/Day Case"
        try:
            df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
            df.columns = [c.strip() for c in df.columns]
            col_map = detect_columns(df)

            if not col_map.get("specialty"):
                log.warning(f"No specialty column in {f}, skipping")
                continue

            out = pd.DataFrame()
            out["specialty"] = df[col_map["specialty"]].astype(str).str.strip()
            out["date"] = df[col_map["date"]].apply(parse_ntpf_date) if col_map.get("date") else pd.NaT
            out["year"] = year
            out["wait_type"] = wait_type

            if col_map.get("total"):
                out["total_waiting"] = df[col_map["total"]].apply(clean_numeric)
            else:
                num_cols = df.select_dtypes(include="number").columns
                out["total_waiting"] = df[num_cols].sum(axis=1)

            frames.append(out)
            log.info(f"Loaded Specialty {wait_type} {year}: {len(out)} rows")

        except Exception as e:
            log.error(f"Error loading {f}: {e}")

    if not frames:
        log.warning("No specialty files loaded")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result = result[result["specialty"].str.lower() != "nan"]
    result = result[result["total_waiting"] > 0]
    log.info(f"Total specialty rows after merge: {len(result)}")
    return result


def save_to_sqlite(op_df, ipdc_df, spec_df):
    """Save all cleaned tables to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    if not op_df.empty:
        op_df.to_sql("op_waiting", conn, if_exists="replace", index=False)
        log.info(f"Saved op_waiting: {len(op_df)} rows")
    if not ipdc_df.empty:
        ipdc_df.to_sql("ipdc_waiting", conn, if_exists="replace", index=False)
        log.info(f"Saved ipdc_waiting: {len(ipdc_df)} rows")
    if not spec_df.empty:
        spec_df.to_sql("specialty_waiting", conn, if_exists="replace", index=False)
        log.info(f"Saved specialty_waiting: {len(spec_df)} rows")
    conn.close()


def save_to_csv(op_df, ipdc_df, spec_df):
    """Save cleaned tables as CSV for Power BI."""
    if not op_df.empty:
        op_df.to_csv("data/processed/op_waiting.csv", index=False)
    if not ipdc_df.empty:
        ipdc_df.to_csv("data/processed/ipdc_waiting.csv", index=False)
    if not spec_df.empty:
        spec_df.to_csv("data/processed/specialty_waiting.csv", index=False)
    log.info("CSV files saved to data/processed/")


def run_pipeline():
    log.info("=" * 60)
    log.info("HSE Wait Times — Data Cleaning Pipeline")
    log.info("=" * 60)

    raw_files = glob.glob("data/raw/*.csv")
    if not raw_files:
        log.error("No raw files found. Run src/download_data.py first.")
        return

    log.info(f"Found {len(raw_files)} raw files to process")

    op_df = load_op_files()
    ipdc_df = load_ipdc_files()
    spec_df = load_specialty_files()

    save_to_sqlite(op_df, ipdc_df, spec_df)
    save_to_csv(op_df, ipdc_df, spec_df)

    log.info("=" * 60)
    log.info("Cleaning pipeline complete")
    log.info(f"  Outpatient rows:         {len(op_df):,}")
    log.info(f"  Inpatient/DC rows:       {len(ipdc_df):,}")
    log.info(f"  Specialty rows:          {len(spec_df):,}")
    log.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()
