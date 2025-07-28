import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import re

class MyClass:
    def __init__(self):
        pass

    def my_method(self):
        pass

    def my_other_method(self):
        pass

    def load_data(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        return pd.DataFrame(data)
    
class Device_list:
    def __init__(self, devices=None):
        if devices is None:
            self.devices = []
        else:
            self.devices = devices

    def add_device(self, device):
        self.devices.append(device)

    def remove_device(self, device_id):
        self.devices = [device for device in self.devices if device.udi_id != device_id]

    def get_device(self, device_id):
        for device in self.devices:
            if device.udi_id == device_id:
                return device
        return None

    def to_dataframe(self):
        data = [device.to_dict() for device in self.devices]
        return pd.DataFrame(data)
    
    def load_from_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        self.devices = [Device.from_dict(device) for device in data]

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump([device.to_dict() for device in self.devices], file, indent=4)
        return self.devices

class Device:
    def __init__(self, udi_id, version, basic_udi_id, trade_name, risk_class, manufacturer, actor_id, details_url, uuid=None):
        self.udi_id = udi_id
        self.version = version
        self.basic_udi_id = basic_udi_id
        self.trade_name = trade_name
        self.risk_class = risk_class
        self.manufacturer = manufacturer
        self.actor_id = actor_id
        self.details_url = details_url
        self.uuid = uuid
    
    def display_details(self):
        details = f"UDI ID: {self.udi_id}\nVersion: {self.version}\nBasic UDI ID: {self.basic_udi_id}\nTrade Name: {self.trade_name}\n" \
                  f"Risk Class: {self.risk_class}\nManufacturer: {self.manufacturer}\nActor ID: {self.actor_id}\nDetails URL: {self.details_url}"
        print(details)

    def to_dict(self):
        return {
            "udi_id": self.udi_id,
            "version": self.version,
            "basic_udi_id": self.basic_udi_id,
            "trade_name": self.trade_name,
            "risk_class": self.risk_class,
            "manufacturer": self.manufacturer,
            "actor_id": self.actor_id,
            "details_url": self.details_url,
            "ManufacturesDetails": self.manufacturer.to_dict() if isinstance(self.manufacturer, Device.ManufacturesDetails) else None,
            "BasicUDI_Details": self.basic_udi_id.to_dict() if isinstance(self.basic_udi_id, Device.BasicUDI_Details) else None,
            "UDI_DI_details": self.udi_id.to_dict() if isinstance(self.udi_id, Device.UDI_DI_details) else None,
            "market_distribution": self.market_distribution.to_dict() if hasattr(self, 'market_distribution') and isinstance(self.market_distribution, Device.market_distribution) else None,
            "certificates": self.certificates.to_dict() if hasattr(self, 'certificates') and isinstance(self.certificates, Device.certificates) else None
        }

    class ManufacturesDetails:
        def __init__(self, actor_id, actor_name, address, country, phone, mail):
            self.actor_id = actor_id
            self.actor_name = actor_name
            self.address = address
            self.country = country
            self.phone = phone
            self.mail = mail

        def display_details(self):
            details = f"ID: {self.actor_id}\nName: {self.actor_name}\nAddress: {self.address}\nCountry: {self.country}\nPhone: {self.phone}\nEmail: {self.mail}"
            print(details)
        
        def to_dict(self):
            return {
                "actor_id": self.actor_id,
                "actor_name": self.actor_name,
                "address": self.address,
                "country": self.country,
                "phone": self.phone,
                "mail": self.mail
            }
        
        @classmethod
        def from_dict(cls, data):
            return cls(
                actor_id=data.get("actor_id"),
                actor_name=data.get("actor_name"),
                address=data.get("address"),
                country=data.get("country"),
                phone=data.get("phone"),
                mail=data.get("mail")
            )
        
        def save_to_file(self, file_path):
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)

        @classmethod
        def load_from_file(cls, file_path):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            return cls.from_dict(data)
        
    class BasicUDI_Details:
        def __init__(self, udi_id, applicable_legislation, kit, system, authorized_representatives, risk_class, implantable, suture_else, measuring_function,
                    reusable_surgical, active_device, admin_or_remove_medical_product, device_model, device_name, human_tissue, animal_tissue, presence_of_medicinal_substance, presence_of_blood_or_plasma):
            self.udi_id = udi_id
            self.applicable_legislation = applicable_legislation
            self.kit = kit
            self.system = system
            self.authorized_representatives = authorized_representatives
            self.risk_class = risk_class
            self.implantable = implantable
            self.suture_else = suture_else
            self.measuring_function = measuring_function
            self.reusable_surgical = reusable_surgical
            self.active_device = active_device
            self.admin_or_remove_medical_product = admin_or_remove_medical_product
            self.device_model = device_model
            self.device_name = device_name
            self.human_tissue = human_tissue
            self.animal_tissue = animal_tissue
            self.presence_of_medicinal_substance = presence_of_medicinal_substance
            self.presence_of_blood_or_plasma = presence_of_blood_or_plasma

        def display_details(self):
            details = f"UDI ID: {self.udi_id}\nApplicable Legislation: {self.applicable_legislation}\nKit: {self.kit}\nSystem: {self.system}\n" \
                    f"Authorized Representatives: {self.authorized_representatives}\nRisk Class: {self.risk_class}\nImplantable: {self.implantable}\n" \
                    f"Suture Else: {self.suture_else}\nMeasuring Function: {self.measuring_function}\nReusable Surgical: {self.reusable_surgical}\n" \
                    f"Active Device: {self.active_device}\nAdmin or Remove Medical Product: {self.admin_or_remove_medical_product}\n" \
                    f"Device Model: {self.device_model}\nDevice Name: {self.device_name}\nHuman Tissue: {self.human_tissue}\n" \
                    f"Animal Tissue: {self.animal_tissue}\nPresence of Medicinal Substance: {self.presence_of_medicinal_substance}\n" \
                    f"Presence of Blood or Plasma: {self.presence_of_blood_or_plasma}"
            print(details)

        def to_dict(self):
            return {
                "udi_id": self.udi_id,
                "applicable_legislation": self.applicable_legislation,
                "kit": self.kit,
                "system": self.system,
                "authorized_representatives": self.authorized_representatives,
                "risk_class": self.risk_class,
                "implantable": self.implantable,
                "suture_else": self.suture_else,
                "measuring_function": self.measuring_function,
                "reusable_surgical": self.reusable_surgical,
                "active_device": self.active_device,
                "admin_or_remove_medical_product": self.admin_or_remove_medical_product,
                "device_model": self.device_model,
                "device_name": self.device_name,
                "human_tissue": self.human_tissue,
                "animal_tissue": self.animal_tissue,
                "presence_of_medicinal_substance": self.presence_of_medicinal_substance,
                "presence_of_blood_or_plasma": self.presence_of_blood_or_plasma
            }

        @classmethod
        def from_dict(cls, data):
            return cls(
                udi_id=data.get("udi_id"),
                applicable_legislation=data.get("applicable_legislation"),
                kit=data.get("kit"),
                system=data.get("system"),
                authorized_representatives=data.get("authorized_representatives"),
                risk_class=data.get("risk_class"),
                implantable=data.get("implantable"),
                suture_else=data.get("suture_else"),
                measuring_function=data.get("measuring_function"),
                reusable_surgical=data.get("reusable_surgical"),
                active_device=data.get("active_device"),
                admin_or_remove_medical_product=data.get("admin_or_remove_medical_product"),
                device_model=data.get("device_model"),
                device_name=data.get("device_name"),
                human_tissue=data.get("human_tissue"),
                animal_tissue=data.get("animal_tissue"),
                presence_of_medicinal_substance=data.get("presence_of_medicinal_substance"),
                presence_of_blood_or_plasma=data.get("presence_of_blood_or_plasma")
            )

        def save_to_file(self, file_path):
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)

        @classmethod
        def load_from_file(cls, file_path):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            return cls.from_dict(data)

    class UDI_DI_details:
        def __init__(self, UDI_DI_code, status, secondary_UDI_code, nomenclature_code, name, 
                    catalog_number, direct_marking_DI, unit_of_use_DI, quantity_of_device, type_of_UDI_PI, additional_product_description,
                    additional_url, clinical_sizes, labelled_singleuse, max_number_of_reuse, sterilization_need, sterile, containing_latex, storage_handling_conditions,
                    reprocessed_single_use, other_purpose_then_medical, member_state_EU_market):
            self.UDI_DI_code = UDI_DI_code
            self.status = status
            self.secondary_UDI_code = secondary_UDI_code
            self.nomenclature_code = nomenclature_code
            self.name = name
            self.catalog_number = catalog_number
            self.direct_marking_DI = direct_marking_DI
            self.unit_of_use_DI = unit_of_use_DI
            self.quantity_of_device = quantity_of_device
            self.type_of_UDI_PI = type_of_UDI_PI
            self.additional_product_description = additional_product_description
            self.additional_url = additional_url
            self.clinical_sizes = clinical_sizes
            self.labelled_singleuse = labelled_singleuse
            self.max_number_of_reuse = max_number_of_reuse
            self.sterilization_need = sterilization_need
            self.sterile = sterile
            self.containing_latex = containing_latex
            self.storage_handling_conditions = storage_handling_conditions
            self.reprocessed_single_use = reprocessed_single_use
            self.other_purpose_then_medical = other_purpose_then_medical
            self.member_state_EU_market = member_state_EU_market

        def display_details(self):
            details = f"UDI DI Code: {self.UDI_DI_code}\nStatus: {self.status}\nSecondary UDI Code: {self.secondary_UDI_code}\n" \
                    f"Nomenclature Code: {self.nomenclature_code}\nName: {self.name}\nCatalog Number: {self.catalog_number}\n" \
                    f"Direct Marking DI: {self.direct_marking_DI}\nUnit of Use DI: {self.unit_of_use_DI}\nQuantity of Device: {self.quantity_of_device}\n" \
                    f"Type of UDI PI: {self.type_of_UDI_PI}\nAdditional Product Description: {self.additional_product_description}\n" \
                    f"Additional URL: {self.additional_url}\nClinical Sizes: {self.clinical_sizes}\nLabelled Single Use: {self.labelled_singleuse}\n" \
                    f"Max Number of Reuse: {self.max_number_of_reuse}\nSterilization Need: {self.sterilization_need}\nSterile: {self.sterile}\n" \
                    f"Containing Latex: {self.containing_latex}\nStorage Handling Conditions: {self.storage_handling_conditions}\n" \
                    f"Reprocessed Single Use: {self.reprocessed_single_use}\nOther Purpose than Medical: {self.other_purpose_then_medical}\n" \
                    f"Member State EU Market: {self.member_state_EU_market}"
            print(details)

        def to_dict(self):
            return {
                "UDI_DI_code": self.UDI_DI_code,
                "status": self.status,
                "secondary_UDI_code": self.secondary_UDI_code,
                "nomenclature_code": self.nomenclature_code,
                "name": self.name,
                "catalog_number": self.catalog_number,
                "direct_marking_DI": self.direct_marking_DI,
                "unit_of_use_DI": self.unit_of_use_DI,
                "quantity_of_device": self.quantity_of_device,
                "type_of_UDI_PI": self.type_of_UDI_PI,
                "additional_product_description": self.additional_product_description,
                "additional_url": self.additional_url,
                "clinical_sizes": self.clinical_sizes,
                "labelled_singleuse": self.labelled_singleuse,
                "max_number_of_reuse": self.max_number_of_reuse,
                "sterilization_need": self.sterilization_need,
                "sterile": self.sterile,
                "containing_latex": self.containing_latex,
                "storage_handling_conditions": self.storage_handling_conditions,
                "reprocessed_single_use": self.reprocessed_single_use,
                "other_purpose_then_medical": self.other_purpose_then_medical,
                "member_state_EU_market": self.member_state_EU_market
            }

        @classmethod
        def from_dict(cls, data):
            return cls(
                UDI_DI_code=data.get("UDI_DI_code"),
                status=data.get("status"),
                secondary_UDI_code=data.get("secondary_UDI_code"),
                nomenclature_code=data.get("nomenclature_code"),
                name=data.get("name"),
                catalog_number=data.get("catalog_number"),
                direct_marking_DI=data.get("direct_marking_DI"),
                unit_of_use_DI=data.get("unit_of_use_DI"),
                quantity_of_device=data.get("quantity_of_device"),
                type_of_UDI_PI=data.get("type_of_UDI_PI"),
                additional_product_description=data.get("additional_product_description"),
                additional_url=data.get("additional_url"),
                clinical_sizes=data.get("clinical_sizes"),
                labelled_singleuse=data.get("labelled_singleuse"),
                max_number_of_reuse=data.get("max_number_of_reuse"),
                sterilization_need=data.get("sterilization_need"),
                sterile=data.get("sterile"),
                containing_latex=data.get("containing_latex"),
                storage_handling_conditions=data.get("storage_handling_conditions"),
                reprocessed_single_use=data.get("reprocessed_single_use"),
                other_purpose_then_medical=data.get("other_purpose_then_medical"),
                member_state_EU_market=data.get("member_state_EU_market")
            )

        def save_to_file(self, file_path):
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)

        @classmethod
        def load_from_file(cls, file_path):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            return cls.from_dict(data)

    class market_distribution:
        def __init__(self, states):
            self.states = states

        def display_distribution(self):
            print("Market Distribution States:")
            for state in self.states:
                print(f"- {state}")
        def to_dict(self):
            return {
                "states": self.states
            }

        @classmethod
        def from_dict(cls, data):
            return cls(
                states=data.get("states", [])
            )

        def save_to_file(self, file_path):
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)

        @classmethod
        def load_from_file(cls, file_path):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            return cls.from_dict(data)
        
    class certificates:
        def __init__(self, notified_body_id, notified_body_name, notified_body_country, 
                    manufacturing_id, manufacturing_organisatiion_name, manufactuer_adress, country, 
                    application_legislation, certificate_type, certificate_identifier, status, issue_date, starting_certificate_validity_date, date_of_expiry,
                    certificate_language, certificate_documents, device_in_sterile_conditions, device_as_integral_part, animal_tissue, human_tissue, annex_listed, conditions_limitations):
            self.notified_body_id = notified_body_id
            self.notified_body_name = notified_body_name
            self.notified_body_country = notified_body_country
            self.manufacturing_id = manufacturing_id
            self.manufacturing_organisatiion_name = manufacturing_organisatiion_name
            self.manufactuer_adress = manufactuer_adress
            self.country = country
            self.application_legislation = application_legislation
            self.certificate_type = certificate_type
            self.certificate_identifier = certificate_identifier
            self.status = status
            self.issue_date = issue_date
            self.starting_certificate_validity_date = starting_certificate_validity_date
            self.date_of_expiry = date_of_expiry
            self.certificate_language = certificate_language
            self.certificate_documents = certificate_documents
            self.device_in_sterile_conditions = device_in_sterile_conditions
            self.device_as_integral_part = device_as_integral_part
            self.animal_tissue = animal_tissue
            self.human_tissue = human_tissue
            self.annex_listed = annex_listed
            self.conditions_limitations = conditions_limitations

        def display_details(self):
            details = f"Notified Body ID: {self.notified_body_id}\nNotified Body Name: {self.notified_body_name}\nNotified Body Country: {self.notified_body_country}\n" \
                    f"Manufacturing ID: {self.manufacturing_id}\nManufacturing Organisation Name: {self.manufacturing_organisatiion_name}\n" \
                    f"Manufacturer Address: {self.manufactuer_adress}\nCountry: {self.country}\nApplication Legislation: {self.application_legislation}\n" \
                    f"Certificate Type: {self.certificate_type}\nCertificate Identifier: {self.certificate_identifier}\nStatus: {self.status}\n" \
                    f"Issue Date: {self.issue_date}\nStarting Certificate Validity Date: {self.starting_certificate_validity_date}\n" \
                    f"Date of Expiry: {self.date_of_expiry}\nCertificate Language: {self.certificate_language}\nCertificate Documents: {self.certificate_documents}\n" \
                    f"Device in Sterile Conditions: {self.device_in_sterile_conditions}\nDevice as Integral Part: {self.device_as_integral_part}\n" \
                    f"Animal Tissue: {self.animal_tissue}\nHuman Tissue: {self.human_tissue}\nAnnex Listed: {self.annex_listed}\nConditions Limitations: {self.conditions_limitations}"
            print(details)

        def to_dict(self):
            return {
                "notified_body_id": self.notified_body_id,
                "notified_body_name": self.notified_body_name,
                "notified_body_country": self.notified_body_country,
                "manufacturing_id": self.manufacturing_id,
                "manufacturing_organisatiion_name": self.manufacturing_organisatiion_name,
                "manufactuer_adress": self.manufactuer_adress,
                "country": self.country,
                "application_legislation": self.application_legislation,
                "certificate_type": self.certificate_type,
                "certificate_identifier": self.certificate_identifier,
                "status": self.status,
                "issue_date": self.issue_date,
                "starting_certificate_validity_date": self.starting_certificate_validity_date,
                "date_of_expiry": self.date_of_expiry,
                "certificate_language": self.certificate_language,
                "certificate_documents": self.certificate_documents,
                "device_in_sterile_conditions": self.device_in_sterile_conditions,
                "device_as_integral_part": self.device_as_integral_part,
                "animal_tissue": self.animal_tissue,
                "human_tissue": self.human_tissue,
                "annex_listed": self.annex_listed,
                "conditions_limitations": self.conditions_limitations
            }

        @classmethod
        def from_dict(cls, data):
            return cls(
                notified_body_id=data.get("notified_body_id"),
                notified_body_name=data.get("notified_body_name"),
                notified_body_country=data.get("notified_body_country"),
                manufacturing_id=data.get("manufacturing_id"),
                manufacturing_organisatiion_name=data.get("manufacturing_organisatiion_name"),
                manufactuer_adress=data.get("manufactuer_adress"),
                country=data.get("country"),
                application_legislation=data.get("application_legislation"),
                certificate_type=data.get("certificate_type"),
                certificate_identifier=data.get("certificate_identifier"),
                status=data.get("status"),
                issue_date=data.get("issue_date"),
                starting_certificate_validity_date=data.get("starting_certificate_validity_date"),
                date_of_expiry=data.get("date_of_expiry"),
                certificate_language=data.get("certificate_language"),
                certificate_documents=data.get("certificate_documents"),
                device_in_sterile_conditions=data.get("device_in_sterile_conditions"),
                device_as_integral_part=data.get("device_as_integral_part"),
                animal_tissue=data.get("animal_tissue"),
                human_tissue=data.get("human_tissue"),
                annex_listed=data.get("annex_listed"),
                conditions_limitations=data.get("conditions_limitations")
            )

        def save_to_file(self, file_path):
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)

        @classmethod
        def load_from_file(cls, file_path):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist.")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            return cls.from_dict(data)
        
