# ============================================================
# HSE Hospital Wait Times — NTPF Data Downloader
# ============================================================
# Author:      Ishan Kasare
# GitHub:      https://github.com/Ishankasare/HSE-Hospital-Wait-Times-Analysis
# LinkedIn:    https://www.linkedin.com/in/ishan-kasare/
#
# Description:
#   Downloads all open data CSV files from the NTPF website
#   (National Treatment Purchase Fund) for years 2019-2026.
#   These are the official Irish hospital waiting list files.
#
# Data Source:
#   https://www.ntpf.ie/waiting-list-data/open-data/
#
# Run:
#   python src/download_data.py
# ============================================================

import requests
import os
import logging
import time

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/download.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── All NTPF open data CSV URLs ──────────────────────────────
# Source: https://www.ntpf.ie/waiting-list-data/open-data/
DATA_FILES = {
    # 2026
    "OP_Hospital_2026":    "https://www.ntpf.ie/app/uploads/2026/03/OpenData_OPNational01_2026.csv",
    "OP_Specialty_2026":   "https://www.ntpf.ie/app/uploads/2026/03/OpenData_OPNational02_2026.csv",
    "IPDC_Hospital_2026":  "https://www.ntpf.ie/app/uploads/2026/03/OpenData_IPDCNational01_2026.csv",
    "IPDC_Specialty_2026": "https://www.ntpf.ie/app/uploads/2026/03/OpenData_IPDCNational02_2026.csv",
    "IPDC_AdultChild_2026":"https://www.ntpf.ie/app/uploads/2026/03/OpenData_IPDCNational03_2026.csv",
    "GI_Hospital_2026":    "https://www.ntpf.ie/app/uploads/2026/03/OpenData_IPDCNational04_2026.csv",

    # 2025
    "OP_Hospital_2025":    "https://www.ntpf.ie/app/uploads/2026/01/OpenData_OPNational01_2025.csv",
    "OP_Specialty_2025":   "https://www.ntpf.ie/app/uploads/2026/01/OpenData_OPNational02_2025.csv",
    "IPDC_Hospital_2025":  "https://www.ntpf.ie/app/uploads/2026/01/OpenData_IPDCNational01_2025.csv",
    "IPDC_Specialty_2025": "https://www.ntpf.ie/app/uploads/2026/01/OpenData_IPDCNational02_2025.csv",
    "IPDC_AdultChild_2025":"https://www.ntpf.ie/app/uploads/2026/01/OpenData_IPDCNational03_2025.csv",
    "GI_Hospital_2025":    "https://www.ntpf.ie/app/uploads/2026/01/OpenData_IPDCNational04_2025.csv",

    # 2024
    "OP_Hospital_2024":    "https://www.ntpf.ie/app/uploads/2025/01/OpenData_OPNational01_2024-1.csv",
    "OP_Specialty_2024":   "https://www.ntpf.ie/app/uploads/2025/01/OpenData_OPNational02_2024-1.csv",
    "IPDC_Hospital_2024":  "https://www.ntpf.ie/app/uploads/2025/01/OpenData_IPDCNational01_2024-1.csv",
    "IPDC_Specialty_2024": "https://www.ntpf.ie/app/uploads/2025/01/OpenData_IPDCNational02_2024-1.csv",
    "IPDC_AdultChild_2024":"https://www.ntpf.ie/app/uploads/2025/01/OpenData_IPDCNational03_2024-1.csv",
    "GI_Hospital_2024":    "https://www.ntpf.ie/app/uploads/2025/01/OpenData_IPDCNational04_2024-1.csv",

    # 2023
    "OP_Hospital_2023":    "https://www.ntpf.ie/app/uploads/2024/10/OpenData_OPNational01_2023-2.csv",
    "OP_Specialty_2023":   "https://www.ntpf.ie/app/uploads/2024/10/OpenData_OPNational02_2023-1.csv",
    "IPDC_Hospital_2023":  "https://www.ntpf.ie/app/uploads/2024/10/OpenData_IPDCNational01_2023.csv",
    "IPDC_Specialty_2023": "https://www.ntpf.ie/app/uploads/2024/10/OpenData_IPDCNational02_2023-1.csv",

    # 2022
    "OP_Hospital_2022":    "https://www.ntpf.ie/app/uploads/2024/10/OpenData_OPNational01_2022.csv",
    "OP_Specialty_2022":   "https://www.ntpf.ie/app/uploads/2024/10/OpenData_OPNational02_2022-1.csv",
    "IPDC_Hospital_2022":  "https://www.ntpf.ie/app/uploads/2024/10/OpenData_IPDCNational01_2022.csv",
    "IPDC_Specialty_2022": "https://www.ntpf.ie/app/uploads/2024/10/OpenData_IPDCNational02_2022.csv",

    # 2021
    "OP_Hospital_2021":    "https://www.ntpf.ie/app/uploads/2024/10/OpenData_OPNational01_2021-1.csv",
    "IPDC_Hospital_2021":  "https://www.ntpf.ie/app/uploads/2024/10/OpenData_IPDCNational01_2021.csv",

    # 2020
    "OP_Hospital_2020":    "https://www.ntpf.ie/app/uploads/2024/10/OP-Waiting-List-by-Group-Hospital-2020.csv",
    "IPDC_Hospital_2020":  "https://www.ntpf.ie/app/uploads/2024/10/IPDC-Waiting-List-By-Group-Hospital-2020.csv",

    # 2019
    "OP_Hospital_2019":    "https://www.ntpf.ie/app/uploads/2025/02/OP-Waiting-List-by-Group-Hospital-2019.csv",
    "IPDC_Hospital_2019":  "https://www.ntpf.ie/app/uploads/2025/02/IPDC-Waiting-List-by-Group-Hospital-2019.csv",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def download_all():
    log.info("=" * 60)
    log.info("NTPF Data Downloader — Starting")
    log.info(f"Downloading {len(DATA_FILES)} files")
    log.info("=" * 60)

    success = 0
    failed = []

    for name, url in DATA_FILES.items():
        filepath = f"data/raw/{name}.csv"

        # Skip if already downloaded
        if os.path.exists(filepath):
            log.info(f"Already exists — skipping: {name}")
            success += 1
            continue

        try:
            log.info(f"Downloading: {name}")
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(r.content)

            log.info(f"Saved: {filepath} ({len(r.content):,} bytes)")
            success += 1
            time.sleep(1)  # be polite to the server

        except Exception as e:
            log.error(f"Failed: {name} — {e}")
            failed.append(name)

    log.info("=" * 60)
    log.info(f"Download complete: {success} succeeded, {len(failed)} failed")
    if failed:
        log.warning(f"Failed files: {failed}")
    log.info("=" * 60)


if __name__ == "__main__":
    download_all()
