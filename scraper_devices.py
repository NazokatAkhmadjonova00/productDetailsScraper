from urllib import response
import numpy as np
import pandas as pd

import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup
import tqdm as tq

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Add the classes directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '03_classes'))

# load Device class only
try:
    from classes import Device, Device_list

except ImportError:
    # Alternative import method
    import importlib.util
    spec = importlib.util.spec_from_file_location("classes", "03_classes/classes.py")
    classes_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(classes_module)
    
    Device = classes_module.Device
    Device_list = classes_module.Device_list



def get_device_details():

    device_collection = Device_list()

    # check for existing data
    dirc = os.path.join(os.path.dirname(__file__), '02_data')
    file_path = os.path.join(dirc, 'device_details.json')

    if os.path.exists(file_path):
        device_collection.load_from_file(file_path)
        print(f"Loaded existing device details from {file_path}")
        print(f"Device count: {len(device_collection.devices)}")

    # set initial page range
    if len(device_collection.devices) > 0:
        start_page = len(device_collection.devices) // 50
    else:
        start_page = 0
    # dynamic endpage detection
    max_page = 50000

    # dynamic end detection
    pages_found = 0
    last_found_page = 0

    # create a progress bar
    pbar = tq.tqdm(range(start_page, max_page), desc="Scraping Device Details", unit="page")

    for page in pbar:
        # update progress bar description
        pbar.set_description(f"Scraping Device Details - Page {page + 1}")
        # API endpoint 
        url = "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData"
        params = {
            "page": page,
            "pageSize": 50,
            "size": 50,
            "iso2Code": "en",
            "sort": ["primaryDi,desc", "versionNumber,DESC"],
            "deviceStatusCode": "refdata.device-model-status.on-the-market",
            "languageIso2Code": "en"
        }

        response = requests.get(url, params=params)
        data = response.json()["content"]

        for item in data:
            udi_id = item.get("primaryDi")
            version = item.get("versionNumber")
            basic_udi_id = item.get("basicUdi")
            trade_name = item.get("tradeName")
            risk_class_full = item.get("riskClass", {}).get("code", "")
            risk_class = risk_class_full.split(".")[-1] if risk_class_full else ""
            manufacturer = item.get("manufacturerName")
            actor_id = item.get("manufacturerSrn")
            uuid = item.get("uuid")
            details_url = f"https://ec.europa.eu/tools/eudamed/#/screen/device-detail/{uuid}"

            device = Device(
                udi_id=udi_id,
                version=version,
                basic_udi_id=basic_udi_id,
                trade_name=trade_name,
                risk_class=risk_class,
                manufacturer=manufacturer,
                actor_id=actor_id,
                uuid=uuid,
                details_url=details_url
            )

            # check if device already exists in collection
            if device not in device_collection.devices:
                device_collection.add_device(device)
            else:
                print(f"Device already exists: {device.trade_name} (UDI: {device.udi_id})")

        
        # save progress after each page
        device_collection.save_to_file(file_path)

        # check if we have reached the maximum page limit
        if page >= max_page:
            print(f"Reached maximum page limit of {max_page}. Stopping scraping.")
            break

        # check if no new devices were found
        if len(data) == 0:
            print(f"No new devices found on page {page + 1}. Stopping scraping.")
            break
        
        # update progress bar
        pbar.update(1)
        pages_found += 1
        last_found_page = page


    # update end_page for next run
    end_page = last_found_page + 1
    print(f"Scraping completed. Total pages found: {pages_found}. Last page processed: {last_found_page + 1}")
    print(f"Next run will start from page {end_page}")

    # save final collection
    device_collection.save_to_file(file_path)
    print(f"Final device details saved to {file_path}")

    # save last page found number
    last_page_file = os.path.join(dirc, 'last_page_found.txt')

    with open(last_page_file, 'w') as f:
        f.write(str(end_page))
        print(f"Last page found saved to {last_page_file}")
    
    return

def main():
    # get device details
    get_device_details()

if __name__ == "__main__":
    main()

