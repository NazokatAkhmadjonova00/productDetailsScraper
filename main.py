import numpy as np
import pandas as pd
import json

import os
import re

import signal
import sys

import psycopg2

import requests
import bs4 as BeautifulSoup

import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
import time

# Import config and database connector
from config import DB_CONFIG, REQUEST_SETTINGS, PROJECT_DESC, PROJECT_SETTINGS, DATA_PATHS

from db import DatabaseConnector

from models.device_importer import DeviceImporter
from models.operator_importer import OperatorImporter
from models.certificate_importer import CertificateImporter

logging.basicConfig(
    filename="logs/import.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.warning(f"Starting {PROJECT_DESC['project_name']} v{PROJECT_DESC['version']} by {PROJECT_DESC['author']}")

# Global interrupt flag
stop_requested = False

def handle_interrupt(signum, frame):
    global stop_requested
    logging.warning("Interrupt signal received. Stopping fetch after current batch...")
    stop_requested = True

# Signal handler
signal.signal(signal.SIGINT, handle_interrupt)

def save_last_page(page, name):
    """Saves the last processed page number to a file.
    """
    if name == "devices":
        with open(DATA_PATHS["last_page_file"], "w") as f:
            f.write(str(page))
    elif name == "operators":
        with open(DATA_PATHS["last_operator_page_file"], "w") as f:
            f.write(str(page))
    elif name == "certificates":
        with open(DATA_PATHS["last_certificate_page_file"], "w") as f:
            f.write(str(page))

def load_last_page(name):
    try:
        if name == "devices":
            path = DATA_PATHS["last_page_file"]
        elif name == "operators":
            path = DATA_PATHS["last_operator_page_file"]
        elif name == "certificates":
            path = DATA_PATHS["last_certificate_page_file"]
        else:
            return 0

        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read().strip()
                if content:
                    return int(content)
                else:
                    logging.warning(f"{name}: Datei ist leer. Starte bei Seite 0.")
                    return 0
        else:
            logging.warning(f"{name}: Keine Datei gefunden. Starte bei Seite 0.")
            return 0
    except Exception as e:
        logging.error(f"Fehler beim Laden der letzten Seite ({name}): {e}")
        return 0

def process_device_page(page, device_importer):
    """
    Fetched one page from api and processes the devices.
    """
    params = REQUEST_SETTINGS["device"]["params"].copy()
    params["page"] = page

    try:
        response = requests.get(
            REQUEST_SETTINGS["device"]["base_url"],
            params=params,
            timeout=10,
            headers=REQUEST_SETTINGS["headers"]
        )

        if response.status_code != 200:
            logging.warning(f"[Device Page {page}] Response {response.status_code}: {response.text}")
            return 0

        data = response.json()
        entries = data.get("content", [])
        inserted = 0

        for device in entries:
            if not isinstance(device, dict):
                logging.warning(f"Unexpected device type on page {page}: {type(device)}")
                continue
            uuid = device.get("uuid")
            eudamed_id = device.get("primaryDi")
            basic_udi_di = device.get("basicUdi")
            actor_id = device.get("manufacturerSrn")
            
            url = REQUEST_SETTINGS["device"]["basic_udi_detail_url"].format(uuid=uuid)
            actor_id_url = REQUEST_SETTINGS["device"]["actor_url"].format(actor_id=actor_id)
            # get device actor information
            response_actor = requests.get(actor_id_url, headers=REQUEST_SETTINGS["headers"], timeout=10)
            if response_actor.status_code == 200:
                try:
                    content = response_actor.json().get("content", {})
                    
                    # Handle different response types from API
                    if isinstance(content, list) and content:
                        actor_data = content[0]  # Take first item if it's a list
                    elif isinstance(content, dict):
                        actor_data = content
                    else:
                        logging.warning(f"Unexpected content type for actor {actor_id}: {type(content)}")
                        actor_data = {}
                        
                    # get actor_url
                    if actor_data and isinstance(actor_data, dict):
                        actor_data["details_url"] = REQUEST_SETTINGS["operators"]["detail_url"].format(uuid=actor_data.get("uuid"))
                        device_importer.insert_operator_if_needed(actor_data)
                    else:
                        logging.warning(f"No valid actor data found for {actor_id}")
                except Exception as e:
                    logging.error(f"Error processing actor data for {actor_id}: {e}")
            else:
                logging.warning(f"ERROR: No actor details for {actor_id} (Status {response_actor.status_code})")


            prepared = {
                "uuid": uuid,
                "basic_udi_id": eudamed_id,
                "udi_id": basic_udi_di,
                "version": device.get("versionNumber"),
                "trade_name": device.get("tradeName"),
                "risk_class": device.get("riskClass", {}).get("code", "").split(".")[-1],
                "manufacturer": device.get("manufacturerName"),
                "actor_id": actor_id,
                "details_url": url
            }

            device_importer.insert_device(prepared)

            # Detail data fetch
            # basic UDI and udiDi detail URL
            udi_detail_url = REQUEST_SETTINGS["device"]["udiDi_detail_url"].format(uuid=uuid)
            basic_udi_detail_url = REQUEST_SETTINGS["device"]["basic_udi_detail_url"].format(uuid=uuid)

            detail_response = requests.get(udi_detail_url, headers=REQUEST_SETTINGS["headers"], timeout=10)
            basic_udi_response = requests.get(basic_udi_detail_url, headers=REQUEST_SETTINGS["headers"], timeout=10)
            if detail_response.status_code == 200 and basic_udi_response.status_code == 200:
                basic_device_details = basic_udi_response.json()
                device_details = detail_response.json()
                device_importer.insert_device_details(basic_device_details, device_details, uuid)
                logging.info(f"Inserted device details for {uuid}")
            else:
                logging.warning(f"ERROR: No details for {uuid} (Status {detail_response.status_code})")
                logging.warning(f"ERROR: No basic UDI details for {uuid} (Status {basic_udi_response.status_code})")

            inserted += 1


        return inserted

    except Exception as e:
        logging.error(f"ERROR - DEVICE PAGE {page}: {e}")
        return 0

def fetch_devices_parallel(db, max_pages=100, max_workers=5, resume_from=0):
    device_importer = DeviceImporter(db)
    total_inserted = 0
    logging.info(f"Starting parallel fetch for {max_pages} pages with {max_workers} workers...")
    if resume_from >= max_pages:
        logging.warning("Resume page is greater than or equal to max pages. Exiting.")
        # correction of max_pages to avoid infinite loop
        max_pages = max_pages + resume_from
        logging.info(f"Setting max_pages to {max_pages} to avoid infinite loop.")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_device_page, page, device_importer): page
            for page in range(resume_from, max_pages)
        }

        empty_pages = 0
        last_success_page = 0

        for future in tqdm(as_completed(futures), total=len(futures), desc="Device Pages Processed"):
            page = futures[future]
            
            if stop_requested:
                break
            
            try:
                inserted = future.result()
                logging.info(f"PAGE {page}: {inserted} DEVICES INSERTED")
                total_inserted += inserted

                if inserted > 0:
                    empty_pages = 0
                    last_success_page = page
                    save_last_page(page, "devices")
                else:
                    empty_pages += 1
                    if empty_pages >= 50:
                        logging.info(f"Stopping fetch after {empty_pages} empty pages. Last success: page {last_success_page}")
                        break

            except Exception as e:
                logging.error(f"ERROR - DEVICE PAGE {page}: {e}")
            finally:
                if stop_requested:
                    logging.info("Interrupted by user. Saving last successful page...")
                    if last_success_page is not None:
                        save_last_page(last_success_page, "devices")

                logging.info(f"TOTAL INSERTED: {total_inserted} DEVICES")

def process_operators_page(page, operator_importer, actor_type):
    """
    Fetched one page from api and processes the operators.
    """
    params = REQUEST_SETTINGS["operators"]["params"].copy()
    params["actorTypeCode"] = actor_type
    params["page"] = page

    try:
        response = requests.get(
            REQUEST_SETTINGS["operators"]["base_url"],
            params=params,
            timeout=10,
            headers=REQUEST_SETTINGS["headers"]
        )

        if response.status_code != 200:
            logging.warning(f"ERROR - OPERATORS PAGE {page}: {response.status_code}")
            return 0

        entries = response.json().get("content", [])
        logging.debug(f"Operators page {page}: Got {len(entries)} entries of type {type(entries)}")
        inserted = 0

        for operator in entries:
            # Debug: Check what type of data we're getting
            if not isinstance(operator, dict):
                logging.warning(f"Unexpected operator type on page {page}: {type(operator)} - {operator}")
                continue
            
            actor_id = operator.get("eudamedIdentifier")
            if not actor_id:
                logging.warning(f"Skipping operator on page {page}: No eudamedIdentifier found")
                continue
                
            version = operator.get("versionNumber")
            role = operator.get("actorType", {}).get("code", "").split(".")[-1]
            name = operator.get("name")
            abbreviated_name = operator.get("abbreviatedName")
            city = operator.get("cityName")
            country = operator.get("countryName", "")
            uuid = operator.get("uuid")
            
            if not uuid:
                logging.warning(f"Skipping operator on page {page}: No UUID found for actor_id {actor_id}")
                continue
                
            url = REQUEST_SETTINGS["operators"]["detail_url"].format(uuid=uuid)

            prepared = {
                "uuid": uuid,
                "actor_id": actor_id,
                "version": version,
                "role": role,
                "name": name,
                "abbreviated_name": abbreviated_name,
                "city": city,
                "country": country,
                "details_url": url
            }

            operator_importer.insert_operator(prepared)

            # Details fetch
            detail_response = requests.get(
                url,
                headers=REQUEST_SETTINGS["headers"],
                timeout=10
            )
            if detail_response.status_code == 200:
                try:
                    response_json = detail_response.json()
                    if "actorDataPublicView" not in response_json:
                        logging.error(f"No 'actorDataPublicView' in response for UUID {uuid}: {json.dumps(response_json, indent=2)}")
                        continue
                    operator_details = response_json.get("actorDataPublicView", {})

                    if not operator_details:
                        logging.warning(f"No 'actorDataPublicView' found for UUID {uuid}")
                        continue
                        
                    if not isinstance(operator_details, dict):
                        logging.error(f"Invalid 'actorDataPublicView' type for UUID {uuid}: {type(operator_details)}")
                        continue

                    operator_importer.insert_operator_details(operator_details)
                    
                except Exception as e:
                    logging.error(f"JSON decode failed for operator detail UUID {uuid}: {e}")
                    continue
            else:
                logging.warning(f"ERROR: No details for UUID {uuid} (Status {detail_response.status_code})")


            inserted += 1

        return inserted

    except Exception as e:
        logging.error(f"ERROR - OPERATORS PAGE {page}: {e}")
        return 0

def fetch_operators_parallel(db, max_pages=1000, max_workers=5, resume_from=0):
    operator_importer = OperatorImporter(db)
    total_inserted = 0
    logging.info(f"Starting parallel fetch for {max_pages} pages with {max_workers} workers...")

    # iterate over all actor types
    actor_types = REQUEST_SETTINGS["operators"]["actor_types"]


    for actor_type in actor_types:
        logging.info(f"Processed actor_type: {actor_type}")
        
        empty_pages = 0
        last_success_page = 0

        if resume_from >= max_pages:
            logging.warning("Resume page is greater than or equal to max pages. Exiting.")
            # correction of max_pages to avoid infinite loop
            max_pages = max_pages + resume_from
            logging.info(f"Setting max_pages to {max_pages} to avoid infinite loop.")
            

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_operators_page, page, operator_importer, actor_type): page
                for page in range(resume_from, max_pages)
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc=f"{actor_type} Operator Pages Processed"):
                page = futures[future]
                if stop_requested:
                    break
                
                try:
                    inserted = future.result()
                    logging.info(f"PAGE {page}: {inserted} OPERATORS INSERTED")
                    total_inserted += inserted

                    if inserted > 0:
                        empty_pages = 0
                        last_success_page = page
                        save_last_page(page, "operators")
                    else:
                        empty_pages += 1
                        if empty_pages >= 50:
                            logging.info(f"Stopping fetch after {empty_pages} empty pages. Last success: page {last_success_page}")
                            break

                except Exception as e:
                    logging.error(f"ERROR - OPERATORS PAGE {page}: {e}")

                
        if stop_requested:
            logging.info("Interrupted by user. Saving last successful page...")
            if last_success_page is not None:
                save_last_page(last_success_page, "operators")
                
    logging.info(f"TOTAL INSERTED: {total_inserted} OPERATORS")

def process_certificates_page(page, certificate_importer):
    """
    Fetched one page from api and processes the certificates.
    """
    params = REQUEST_SETTINGS["certificates"]["params"].copy()
    params["page"] = page
    

    try:
        response = requests.get(
            REQUEST_SETTINGS["certificates"]["base_url"],
            params=params,
            timeout=10,
            headers=REQUEST_SETTINGS["headers"]
        )

        if response.status_code != 200:
            logging.warning(f"ERROR - CERTIFICATES PAGE {page}: {response.status_code}")
            return 0

        entries = response.json().get("content", [])
        inserted = 0

        for certificate in entries:
            uuid = certificate.get("uuid")
            if not uuid:
                logging.warning(f"Skipping certificate on page {page}: No UUID found.")
                continue
            
            url = REQUEST_SETTINGS["certificates"]["detail_url"].format(uuid=uuid)
            certificate["detailsUrl"] = url

            certificate_importer.insert_certificate(certificate)

            # Details fetch
            detail_response = requests.get(
                url,
                headers=REQUEST_SETTINGS["headers"],
                timeout=10
            )
            if detail_response.status_code == 200:
                certificate_details = detail_response.json()
                certificate_importer.insert_certificate_details(certificate_details, REQUEST_SETTINGS["certificates"]["document_url"].format(uuid=uuid))
            else:
                logging.warning(f"ERROR: No details for {uuid} (Status {detail_response.status_code})")

            inserted += 1

        logging.info(f"Processed page {page} with {inserted} certificates.")
        return inserted
    except Exception as e:
        logging.error(f"ERROR - CERTIFICATES PAGE {page}: {e}")
        return 0

def fetch_certificates_parallel(db, max_pages=1000, max_workers=5, resume_from=0):
    certificate_importer = CertificateImporter(db)
    total_inserted = 0
    logging.info(f"Starting parallel fetch for {max_pages} pages with {max_workers} workers...")

    if resume_from >= max_pages:
        logging.warning("Resume page is greater than or equal to max pages. Exiting.")
        # correction of max_pages to avoid infinite loop
        max_pages = max_pages + resume_from
        logging.info(f"Setting max_pages to {max_pages} to avoid infinite loop.")

    
    empty_pages = 0
    last_success_page = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_certificates_page, page, certificate_importer): page
            for page in range(resume_from, max_pages)
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Certificate Pages Processed"):
            page = futures[future]
            try:
                inserted = future.result()
                logging.info(f"PAGE {page}: {inserted} CERTIFICATES INSERTED")
                total_inserted += inserted
                if stop_requested:
                    break

                if inserted > 0:
                    empty_pages = 0
                    last_success_page = page
                    save_last_page(page, "certificates")
                else:
                    empty_pages += 1
                    if empty_pages >= 50:
                        logging.info(f"Stopping fetch after {empty_pages} empty pages. Last success: page {last_success_page}")
                        break

            except Exception as e:
                logging.error(f"ERROR - CERTIFICATES PAGE {page}: {e}")

            finally:
                if stop_requested:
                    logging.info("Interrupted by user. Saving last successful page...")
                    if last_success_page is not None:
                        save_last_page(last_success_page, "certificates")
                logging.info(f"TOTAL INSERTED: {total_inserted} CERTIFICATES")

def operator_connector():
    """connect operator with DB for parallel processing"""
    db = DatabaseConnector()
    logging.info("Database connection established for operator function.")

    #resume_from_operators = load_last_page("operators")
    max_pages = 5000
    fetch_operators_parallel(db, max_pages=max_pages, max_workers=5, resume_from=0)
    
    db.close()

def device_connector():
    """connect device with DB for parallel processing"""
    db = DatabaseConnector()
    logging.info("Database connection established for device function.")

    # first real run without resume
    #resume_from_devices = load_last_page("devices")
    devices_max_pages = 70000
    
    fetch_devices_parallel(db, max_pages=devices_max_pages, max_workers=5, resume_from=0)
    
    db.close()

def certificate_connector():
    """connect certificate with DB for parallel processing"""
    db = DatabaseConnector()
    logging.info("Database connection established for certificate function.")

    # first real run without resume
    #resume_from_certificates = load_last_page("certificates")
    certificate_max_pages = 5000
    
    fetch_certificates_parallel(db, max_pages=certificate_max_pages, max_workers=5, resume_from=0)
    
    db.close()

if __name__ == "__main__":
    
    start = time.time()
    logging.info("Starting fetch...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(device_connector): "device",
            executor.submit(operator_connector): "operator",
            executor.submit(certificate_connector): "certificate"
        }

        for future in as_completed(futures):
            try:
                future.result()  # Wait for the future to complete
            except Exception as e:
                logging.error(f"Error in future: {e}")

    end = time.time()
    
    print(f"Device fetch completed in {end - start:.2f} seconds.")
    logging.info(f"Device fetch completed in {end - start:.2f} seconds.")
    logging.info("Closing database connection.")
