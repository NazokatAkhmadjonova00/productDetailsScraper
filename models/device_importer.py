
import logging
import json

class DeviceImporter:
    def __init__(self, db):
        self.db = db

    def insert_device(self, device):
        eudamed_id = device.get("basic_udi_id")
        uuid = device.get("uuid")
        if not uuid:
            logging.warning("No UUID found for device, skipping insertion.")
            return
        
        if self.device_exists(uuid):
            logging.info(f"Device with UUID {uuid} already exists.")
            return
        
                
        insert_device_query = """
        INSERT INTO devices (
            uuid,
            eudamed_id,
            udi_id,
            version,
            trade_name,
            risk_class,
            manufacturer,
            actor_id,
            details_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (uuid) DO UPDATE SET
            eudamed_id = EXCLUDED.eudamed_id,
            udi_id = EXCLUDED.udi_id,
            version = EXCLUDED.version,
            trade_name = EXCLUDED.trade_name,
            risk_class = EXCLUDED.risk_class,
            manufacturer = EXCLUDED.manufacturer,
            actor_id = EXCLUDED.actor_id,
            details_url = EXCLUDED.details_url;
        """
        params = (
            uuid,
            eudamed_id,
            device.get("udi_id"),
            device.get("version"),
            device.get("trade_name"),
            device.get("risk_class"),
            device.get("manufacturer"),
            device.get("actor_id"),
            device.get("details_url")
        )

        self.db.execute(insert_device_query, params)

    def insert_operator_if_needed(self, actor):
        uuid = actor.get("uuid")
        actor_id = actor.get("eudamedIdentifier")

        # check if actor exists
        check_query = "SELECT 1 FROM operators WHERE uuid = %s LIMIT 1;"
        self.db.cursor.execute(check_query, (uuid,))
        if self.db.cursor.fetchone() is not None:
            logging.info(f"Operator with UUID {uuid} already exists.")
            return
        
        if uuid is None or actor_id is None:
            logging.warning(f"Missing data in operator: uuid={uuid}, actor_id={actor_id}")
            return


        insert_operator_query = """
            INSERT INTO operators (
                uuid,
                actor_id,
                version,
                role,
                name,
                abbreviated_name,
                city_name,
                country,
                details_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (uuid) DO NOTHING;
        """

        params = (
            uuid,
            actor_id,
            actor.get("versionNumber"),
            actor.get("roleName"),
            actor.get("name"),
            actor.get("abbreviatedName"),
            actor.get("cityName"),
            actor.get("countryName"),
            actor.get("detailsUrl")
        )

        self.db.execute(insert_operator_query, params)

    def device_exists(self, uuid):
        try:
            check_query = "SELECT 1 FROM devices WHERE uuid = %s LIMIT 1;"
            self.db.cursor.execute(check_query, (uuid,))
            if self.db.cursor.description is not None:
                result = self.db.cursor.fetchone()
                return result is not None
            else:
                logging.warning(f"Cursor description is None while checking device {uuid}")
                return False
        except Exception as e:
            logging.error(f"Error checking device existence for {uuid}: {e}")
            return False
        
    def insert_device_if_needed(self, uuid):
        if not uuid:
            logging.warning("No UUID provided for device, skipping insertion.")
            return
        
        if self.device_exists(uuid):
            logging.info(f"Device with UUID {uuid} already exists.")
            return
        
        insert_device_query = """
        INSERT INTO devices (uuid) VALUES (%s)
        ON CONFLICT (uuid) DO NOTHING;
        """
        
        self.db.execute(insert_device_query, (uuid,))

    
    def insert_device_details(self, basicUdiData, udiDiData, uuid):
        """
        Inserts detailed device information into device_udi_di_details and market_distribution.
        """
        if not uuid:
            logging.warning("No UUID found for device, skipping details insertion.")
            return

        self.insert_device_if_needed(uuid)
        primary_di = udiDiData.get("primaryDi")
        if not isinstance(primary_di, dict):
            logging.warning("Missing or invalid 'primaryDi' in udiDiData, skipping details insertion.")
            return
        eudamed_id = primary_di.get("code")

        if not eudamed_id:
            logging.warning("No EUDAMED ID found for device, skipping details insertion.")
            return
        

        try:
            # === INSERT INTO device_basic_udi_detail ===
            basic_uuid = basicUdiData.get("uuid")

            legislation_list = basicUdiData.get("applicableLegislation", [])
            legislation = legislation_list[0].get("code", "") if legislation_list and isinstance(legislation_list[0], dict) else ""

            procedure_pack_device_itself = basicUdiData.get("device")
            auth_rep = basicUdiData.get("authorisedRepresentative")
            authorised_representative = auth_rep.get("srn") if auth_rep and isinstance(auth_rep, dict) else None
            risk_class_basic = basicUdiData.get("riskClass", {}).get("code", "").split(".")[-1]

            implantable = str(basicUdiData.get("implantable"))
            is_suture_or_implant_part = str(basicUdiData.get("sutures"))
            measuring_function = str(basicUdiData.get("measuringFunction"))
            reusable_surgical_instrument = str(basicUdiData.get("reusable"))
            active_device = str(basicUdiData.get("active"))
            intended_to_administer_or_remove_medicinal_product = str(basicUdiData.get("administeringMedicine"))

            device_model = basicUdiData.get("deviceModel")
            device_name = basicUdiData.get("deviceName")

            contains_human_tissues = str(basicUdiData.get("humanTissues"))
            contains_animal_tissues = str(basicUdiData.get("animalTissues"))

            contains_medicinal_substance = str(basicUdiData.get("medicinalProduct"))
            contains_blood_derived_medicinal_substance = str(basicUdiData.get("microbialSubstances"))

            insert_basic_query = """
                INSERT INTO device_basic_udi_detail (
                    device_uuid,
                    basic_uuid,
                    eudamed_id,
                    applicable_legislation,
                    procedure_pack_device_itself,
                    authorised_representative,
                    risk_class,
                    implantable,
                    is_suture_or_implant_part,
                    measuring_function,
                    reusable_surgical_instrument,
                    active_device,
                    intended_to_administer_or_remove_medicinal_product,
                    device_model,
                    device_name,
                    contains_human_tissues,
                    contains_animal_tissues,
                    contains_medicinal_substance,
                    contains_blood_derived_medicinal_substance
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """

            self.db.execute(insert_basic_query, (
                uuid,
                basic_uuid,
                eudamed_id,
                legislation,
                procedure_pack_device_itself,
                authorised_representative,
                risk_class_basic,
                implantable,
                is_suture_or_implant_part,
                measuring_function,
                reusable_surgical_instrument,
                active_device,
                intended_to_administer_or_remove_medicinal_product,
                device_model,
                device_name,
                contains_human_tissues,
                contains_animal_tissues,
                contains_medicinal_substance,
                contains_blood_derived_medicinal_substance
            ))


            # === INSERT INTO device_udi_di_details ===
            udi_uuid = udiDiData.get("uuid")
            
            # Handle nested device status safely
            device_status = udiDiData.get("deviceStatus")
            if device_status and isinstance(device_status, dict):
                status_type = device_status.get("type")
                if status_type and isinstance(status_type, dict):
                    status = status_type.get("code", "").split(".")[-1]
                else:
                    status = ""
            else:
                status = ""
                
            udi_di_secondary = udiDiData.get("secondaryDi")

            # Handle nomenclature safely
            nomenclatures = udiDiData.get("cndNomenclatures")
            if nomenclatures and isinstance(nomenclatures, dict):
                nomenclature_code = nomenclatures.get("code", "")
                description = nomenclatures.get("description")
                if description and isinstance(description, dict):
                    texts = description.get("texts", [])
                    if texts and isinstance(texts, list) and texts:
                        nomenclature_code += ": " + texts[0].get("text", "")
            else:
                nomenclature_code = ""
                
            # Handle trade name safely
            trade_name_obj = udiDiData.get("tradeName")
            if trade_name_obj and isinstance(trade_name_obj, dict):
                texts = trade_name_obj.get("texts", [])
                if texts and isinstance(texts, list) and texts:
                    trade_name = texts[0].get("text", "")
                else:
                    trade_name = ""
            else:
                trade_name = ""

            reference_number = udiDiData.get("reference")
            direct_marking_di = str(udiDiData.get("directMarking"))
            quantity_of_device = udiDiData.get("baseQuantity")

            udi_pi_type = udiDiData.get("udPiType", {})
            type_of_udi_pi = ", ".join([v for v in udi_pi_type.values() if v]) if isinstance(udi_pi_type, dict) else ""

            # Handle additional description safely
            additional_desc = udiDiData.get("additionalDescription")
            if additional_desc and isinstance(additional_desc, dict):
                texts = additional_desc.get("texts", [])
                if texts and isinstance(texts, list) and texts:
                    additional_product_description = texts[0].get("text", "")
                else:
                    additional_product_description = ""
            else:
                additional_product_description = ""
                
            additional_info_url = udiDiData.get("additionalInformationUrl")

            clinical_sizes_raw = udiDiData.get("clinicalSizes", [])
            clinical_sizes = ""

            if isinstance(clinical_sizes_raw, list) and clinical_sizes_raw:
                cs0 = clinical_sizes_raw[0]
                if isinstance(cs0, dict):
                    max_val = str(cs0.get("maximumValue", ""))
                    min_val = str(cs0.get("minimumValue", ""))
                    if max_val and min_val:
                        clinical_sizes = f"{min_val} - {max_val}"
                    elif cs0.get("value"):
                        clinical_sizes = str(cs0.get("value"))
                    elif cs0.get("text"):
                        clinical_sizes = str(cs0.get("text"))
            elif isinstance(clinical_sizes_raw, dict):
                max_val = str(clinical_sizes_raw.get("maximumValue", ""))
                min_val = str(clinical_sizes_raw.get("minimumValue", ""))
                if max_val and min_val:
                    clinical_sizes = f"{min_val} - {max_val}"
                elif clinical_sizes_raw.get("value"):
                    clinical_sizes = str(clinical_sizes_raw.get("value"))
                elif clinical_sizes_raw.get("text"):
                    clinical_sizes = str(clinical_sizes_raw.get("text"))
            elif isinstance(clinical_sizes_raw, str):
                clinical_sizes = clinical_sizes_raw.strip()

            labelled_single_use = str(udiDiData.get("singleUse"))
            needs_sterilisation_before_use = str(udiDiData.get("sterilization"))
            labelled_as_sterile = str(udiDiData.get("sterile"))
            contains_latex = str(udiDiData.get("latex"))

            storage_conditions = ""

            shc_list = udiDiData.get("storageHandlingConditions", [])
            if shc_list:
                description = shc_list[0].get("description", {})

                if isinstance(description, dict):
                    storage_conditions = description.get("texts", [{}])[0].get("text", "")
                elif isinstance(description, str):
                    storage_conditions = description

            reprocessed_single_use = str(udiDiData.get("reprocessed"))
            intended_non_medical_use = str(udiDiData.get("annexXVIApplicable"))

            # Handle placedOnTheMarket safely
            placed_on_market = str(udiDiData.get("placedOnTheMarket"))
            market_member_state = placed_on_market.get("name") if placed_on_market and isinstance(placed_on_market, dict) else None
            related_devices = None

            insert_detail_query = """
                INSERT INTO device_udi_di_details (
                    device_uuid,
                    udi_uuid,
                    eudamed_id,
                    status,
                    udi_di_secondary,
                    nomenclature_code,
                    trade_name,
                    reference_number,
                    direct_marking_di,
                    quantity_of_device,
                    type_of_udi_pi,
                    additional_product_description,
                    additional_info_url,
                    clinical_sizes,
                    labelled_single_use,
                    needs_sterilisation_before_use,
                    labelled_as_sterile,
                    contains_latex,
                    storage_conditions,
                    reprocessed_single_use,
                    intended_non_medical_use,
                    market_member_state,
                    related_devices
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            self.db.execute(insert_detail_query, (
                uuid,
                udi_uuid, 
                eudamed_id,
                status,
                udi_di_secondary,
                nomenclature_code,
                trade_name,
                reference_number,
                direct_marking_di,
                quantity_of_device,
                type_of_udi_pi,
                additional_product_description,
                additional_info_url,
                clinical_sizes,
                labelled_single_use,
                needs_sterilisation_before_use,
                labelled_as_sterile,
                contains_latex,
                storage_conditions,
                reprocessed_single_use,
                intended_non_medical_use,
                market_member_state,
                related_devices
            ))

            # === INSERT INTO market_distribution ===
            market_info = udiDiData.get("marketInfoLink")
            if market_info and isinstance(market_info, dict):
                ms_where_available = market_info.get("msWhereAvailable")
                if ms_where_available and isinstance(ms_where_available, list):
                    for entry in ms_where_available:
                        if not isinstance(entry, dict):
                            continue
                            
                        country_obj = entry.get("country")
                        country = country_obj.get("name") if country_obj and isinstance(country_obj, dict) else None
                        start_date = entry.get("startDate")
                        end_date = entry.get("endDate")

                        insert_market_query = """
                        INSERT INTO market_distribution (
                            device_uuid,
                            eudamed_id,
                            country,
                            start_date,
                            end_date
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        );
                        """
                        self.db.execute(insert_market_query, (
                            uuid,
                            eudamed_id,
                            country,
                            start_date,
                            end_date
                        ))

            logging.info(f"Device Details for {eudamed_id} inserted successfully.")

        except Exception as e:
            logging.error(f"Error inserting device details ({eudamed_id}): {e}")
