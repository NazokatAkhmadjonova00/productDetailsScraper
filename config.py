# DB configuration file
DB_CONFIG = {
    "dbname": "eudamed",
    "user": "postgres",
    "password": "Nwa471995",
    "host": "localhost",
    "port": "5432"
}

# Datapath for the database configuration
DATA_PATHS = {
    "log_file": "./logs/import.log",
    "last_page_file": "./state/last_page.txt",
    "last_operator_page_file": "./state/last_operator_page.txt",
    "last_certificate_page_file": "./state/last_certificate_page.txt",
    # Add separate files for each actor type
    "last_operator_manufacturer_page_file": "./state/last_operator_manufacturer_page.txt",
    "last_operator_authorizedrepresentative_page_file": "./state/last_operator_authorizedrepresentative_page.txt",
    "last_operator_importer_page_file": "./state/last_operator_importer_page.txt",
    "last_operator_distributor_page_file": "./state/last_operator_distributor_page.txt"
}

# Project description 
PROJECT_DESC = {
    "project_name": "EUDAMED Device Details Importer",
    "version": "1.0.0",
    "author": "Felix Haas",
    "description": "Scraper for EUDAMED Data Platform Operator, Device and Certificate details."
}

# Project Modi
PROJECT_SETTINGS = {
    "debug": True,
    "dry_run": False,
    "log_errors": True
}

# === Scraper / Requests Settings ===
# config.py (Erweiterung)

REQUEST_SETTINGS = {
    "base_search_url": "https://ec.europa.eu/tools/eudamed/#/screen/search-device/",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://ec.europa.eu/tools/eudamed/"
    },
    "timeout": 1,
    "language": "en",
    "device": {
        "base_url": "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData",
        "params": {
            "page": 0,
            "pageSize": 50,
            "sort": ["primaryDi,desc", "versionNumber,DESC"],
            "deviceStatusCode": "refdata.device-model-status.on-the-market",
            "languageIso2Code": "en",
            "iso2Code": "en"
        },
        "udiDi_detail_url": "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData/{uuid}?customError=null&languageIso2Code=en",
        "basic_udi_detail_url": "https://ec.europa.eu/tools/eudamed/api/devices/basicUdiData/{uuid}?customError=null&languageIso2Code=en",
        "actor_url": "https://ec.europa.eu/tools/eudamed/api/eos?srn={actor_id}&languageIso2Code=en"
    },
    "operators": {
        "base_url": "https://ec.europa.eu/tools/eudamed/api/eos",
        "actor_types": [
            "refdata.actor-type.importer",
            "refdata.actor-type.manufacturer",
            "refdata.actor-type.system-procedure-pack-producer",
            "refdata.actor-type.authorised-representative"
        ],
        "params": {
            "page": 0,
            "pageSize": 50,
            "sort": ["srn,asc", "versionNumber,DESC"],
            "languageIso2Code": "en",
            "rnd": "dynamic" 
        },
        "detail_url": "https://ec.europa.eu/tools/eudamed/api/actors/{uuid}/publicInformation?languageIso2Code=en"
        
    },
    "certificates": {
        "base_url": "https://ec.europa.eu/tools/eudamed/api/certificates/search/",
        "params": {
            "page": 0,
            "pageSize": 50,
            "sort": ["notifiedBodySrn,asc"],
            "entityTypeCode": "certificate.certificates",
            "languageIso2Code": "en",
            "iso2Code": "en"
        },
        "detail_url": "https://ec.europa.eu/tools/eudamed/api/certificates/{uuid}?languageIso2Code=en",
        "document_url": "https://ec.europa.eu/tools/eudamed/api/documents/{uuid}"
    }

}


# === Tabellen-Mapping ===
TABLES = {
    "devices": "devices",
    "operators": "operators",
    "certificates": "certificates"
}