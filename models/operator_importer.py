import logging
from unittest import result
import psycopg2

class OperatorImporter:
    def __init__(self, db):
        self.db = db

    def insert_operator(self, operator):
        uuid = operator.get("uuid")
        if not uuid:
            logging.warning("No UUID found for operator, skipping insertion.")
            return
            
        actor_id = operator.get("actor_id")  # Changed from eudamedIdentifier to actor_id
        if not actor_id:
            logging.warning(f"No actor_id found for operator {uuid}, skipping insertion.")
            return

        
        if self.operator_exists(uuid):
            self.add_basic_informations(uuid, operator)
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
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (uuid) DO UPDATE SET
                actor_id = EXCLUDED.actor_id,
                version = EXCLUDED.version,
                role = EXCLUDED.role,
                name = EXCLUDED.name,
                abbreviated_name = EXCLUDED.abbreviated_name,
                city_name = EXCLUDED.city_name,
                country = EXCLUDED.country,
                details_url = EXCLUDED.details_url;
        """

        params = (
            uuid,
            actor_id,
            operator.get("version"),
            operator.get("role"),
            operator.get("name"),
            operator.get("abbreviated_name"),
            operator.get("city"),  # Changed from city_name to city
            operator.get("country"),
            operator.get("details_url")
        )

        self.db.execute(insert_operator_query, params)
        logging.info(f"Inserted operator {uuid}.")

    def operator_exists(self, uuid):
        try:
            query = "SELECT 1 FROM operators WHERE uuid = %s LIMIT 1;"
            self.db.cursor.execute(query, (uuid,))
            
            # Nur fetchone(), wenn wirklich was geholt werden kann
            if self.db.cursor.description is not None:
                result = self.db.cursor.fetchone()
                return result is not None

            logging.warning(f"Cursor description is None when checking operator {uuid}")
            return False

        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e).lower():
                logging.warning(f"No results to fetch while checking operator {uuid}")
            else:
                logging.error(f"Database error while checking operator {uuid}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while checking operator {uuid}: {e}")
            return False


    
    def add_basic_informations(self, uuid, operator):
        update_query = """
            UPDATE operators
            SET
                actor_id = %s,
                version = %s,
                role = %s,
                name = %s,
                abbreviated_name = %s,
                city_name = %s,
                country = %s,
                details_url = %s
            WHERE uuid = %s
        """
        params = (
            operator.get("actor_id"),  # Changed from eudamedIdentifier
            operator.get("version"),
            operator.get("role"),
            operator.get("name"),
            operator.get("abbreviated_name"),
            operator.get("city"),  # Changed from city_name
            operator.get("country"),
            operator.get("details_url"),
            uuid
        )

        self.db.execute(update_query, params)


    def insert_operator_details(self, operator):

        if not operator:
            logging.warning("No operator data provided, skipping details insertion.")
            return
        
        if not isinstance(operator, dict):
            logging.error(f"Invalid operator object (type {type(operator)}): {operator}")
            return

        
        actor_id = operator.get("eudamedIdentifier")

        if not actor_id:
            logging.error("No actor ID found in operator data, skipping details insertion.")
            return
        
        uuid = operator.get("uuid")

        if not uuid:
            logging.warning("No UUID found for operator, skipping details insertion.")
            return
        
        try:
            # ==== operator_identification ====
            type_obj = operator.get("type")
            if isinstance(type_obj, dict):
                code = type_obj.get("code", "")
                role = code.split(".")[-1] if code else ""
            else:
                role = ""

            if not role:
                logging.warning(f"No role found for operator {actor_id}. Setting to 'unknown'.")
                role = "unknown"

            country = operator.get("actorAddress", {}).get("country", {}).get("name", "")
            
            # Handle name field - it can be either a string or a nested dict
            name_field = operator.get("name", "")
            if isinstance(name_field, dict):
                texts = name_field.get("texts", [])
                if isinstance(texts, list) and texts and isinstance(texts[0], dict):
                    name = texts[0].get("text", "")
                else:
                    name = ""
            elif isinstance(name_field, str):
                name = name_field
            else:
                name = ""

            # same for abbreviated_name
            abbreviated_name_field = operator.get("abbreviatedName", "")
            if isinstance(abbreviated_name_field, dict):
                texts = abbreviated_name_field.get("texts", [])
                if isinstance(texts, list) and texts and isinstance(texts[0], dict):
                    abbreviated_name = texts[0].get("text", "")
                else:
                    abbreviated_name = ""
            elif isinstance(abbreviated_name_field, str):
                abbreviated_name = abbreviated_name_field
            else:
                abbreviated_name = ""

            operator_identification_query = """
                INSERT INTO operator_identification (
                    operator_uuid,
                    actor_id,
                    role,
                    country,
                    name,
                    abbreviated_name,
                    vat_number,
                    eori,
                    trade_register,
                    confirmation_date
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """
            operator_identification_params = (
                uuid,
                actor_id,
                role,
                country,
                name,
                abbreviated_name,
                operator.get("europeanVatNumber") or "",
                operator.get("eori"),
                operator.get("tradeRegister"),
                operator.get("lastUpdateDate")
            )

            self.db.execute(operator_identification_query, operator_identification_params)

            # ==== operator_address ====
            operator_address_query = """
                INSERT INTO operator_address (
                    operator_uuid,
                    actor_id,
                    street,
                    street_number,
                    address_line_2,
                    post_box,
                    city,
                    zip_code,
                    country,
                    latitude,
                    longitude
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """

            operator_address_params = (
                uuid,
                actor_id,
                operator.get("actorAddress", {}).get("streetName", ""),
                operator.get("actorAddress", {}).get("buildingNumber", ""),
                operator.get("actorAddress", {}).get("addressLine2", ""),
                operator.get("actorAddress", {}).get("postbox", ""),
                operator.get("actorAddress", {}).get("postalZone", ""),
                operator.get("actorAddress", {}).get("cityName", ""),
                country,
                operator.get("actorAddress", {}).get("latitude", ""),
                operator.get("actorAddress", {}).get("longitude", "")
            )

            self.db.execute(operator_address_query, operator_address_params)

            # ==== operator_contact ====
            operator_contact_query = """
                INSERT INTO operator_contact (
                    operator_uuid,
                    actor_id,
                    email,
                    phone,
                    website
                ) VALUES (
                    %s, %s, %s, %s, %s
                );
            """

            operator_contact_params = (
                uuid,
                actor_id,
                operator.get("electronicMail", ""),
                operator.get("telephone", ""),
                operator.get("website", "")
            )
            self.db.execute(operator_contact_query, operator_contact_params)

            # ==== person_responsible ====
            person_responsible_query = """
                INSERT INTO person_responsible (
                    operator_uuid,
                    actor_id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    responsible_for,
                    street,
                    street_number,
                    address_line_2,
                    post_box,
                    city,
                    zip_code,
                    country,
                    latitude,
                    longitude
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """

            responsible = operator.get("regulatoryComplianceResponsibles", [])
            
            if isinstance(responsible, list) and responsible:
                responsible = responsible[0]
            else:
                responsible = {}

            geo = responsible.get("geographicalAddress")
            geo = geo if isinstance(geo, dict) else {}


            person_responsible_params = (
                uuid,
                actor_id,
                responsible.get("firstName", ""),
                responsible.get("familyName", ""),
                responsible.get("electronicMail", ""),
                responsible.get("telephone", ""),
                responsible.get("position", ""),
                geo.get("streetName", ""),
                geo.get("buildingNumber", ""),
                geo.get("addressLine2", ""),
                geo.get("postbox", ""),
                geo.get("postalZone", ""),
                geo.get("cityName", ""),
                geo.get("country", {}).get("name", ""),
                geo.get("latitude", ""),
                geo.get("longitude", "")
            )
            self.db.execute(person_responsible_query, person_responsible_params)

            # ==== competent_authority ====
            competent_authority_query = """
                INSERT INTO competent_authority (
                    operator_uuid,
                    actor_id,
                    name,
                    street,
                    street_number,
                    address_line_2,
                    post_box,
                    postal_code,
                    city,
                    country,
                    email,
                    phone
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """

            competent_authority_params = (
                uuid,
                actor_id,
                operator.get("validatorName", ""),
                operator.get("validatorAddress", {}).get("streetName", ""),
                operator.get("validatorAddress", {}).get("buildingNumber", ""),
                operator.get("validatorAddress", {}).get("addressLine2", ""),
                operator.get("validatorAddress", {}).get("postbox", ""),
                operator.get("validatorAddress", {}).get("postalZone", ""),
                operator.get("validatorAddress", {}).get("cityName", ""),
                operator.get("validatorAddress", {}).get("country", {}).get("name", ""),
                operator.get("validatorEmail", ""),
                operator.get("validatorTelephone", "")
            )

            self.db.execute(competent_authority_query, competent_authority_params)

            logging.info(f"Inserted details for operator {actor_id} successfully.")
        except Exception as e:
            logging.error(f"Error inserting details for operator {actor_id}: {e}")
            raise e
        

