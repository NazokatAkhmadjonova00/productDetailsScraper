import logging
from unittest import result

class CertificateImporter:
    def __init__(self, db):
        self.db = db

    def insert_certificate(self, certificate):
        uuid = certificate.get("uuid")
        if not uuid:
            logging.warning("Certificate UUID is missing, skipping insert.")
            return
        
        certificate_id = certificate.get("certificateNumber", "")
        
        notified_body_id = certificate.get("notifiedBodySrn", "")

        # details_url = REQUEST_SETTINGS["certificates"]["detail_url"].format(uuid=uuid)
        details_url = certificate.get("detailsUrl", "")
        
        # check if notified body exists
        self.check_notified_body_id(notified_body_id)

        certificate_query = """
        INSERT INTO certificates (
            uuid,
            certificate_id,
            certificate_version,
            certificate_type,
            actor_id,
            authorizedRepresentativeSrns,
            notified_body_id,
            status,
            start_date,
            expiry_date,
            details_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (uuid) DO UPDATE SET
            certificate_id = EXCLUDED.certificate_id,
            certificate_version = EXCLUDED.certificate_version,
            certificate_type = EXCLUDED.certificate_type,
            actor_id = EXCLUDED.actor_id,
            authorizedRepresentativeSrns = EXCLUDED.authorizedRepresentativeSrns,
            notified_body_id = EXCLUDED.notified_body_id,
            status = EXCLUDED.status,
            start_date = EXCLUDED.start_date,
            expiry_date = EXCLUDED.expiry_date,
            details_url = EXCLUDED.details_url;
        """
        certificate_params = (
            uuid,
            certificate_id,
            certificate.get("versionNumber", ""),
            certificate.get("certificateType", {}).get("code", "").split(".")[-1],
            certificate.get("actorSrn", ""),
            certificate.get("authorizedRepresentativeSrns", []),
            notified_body_id,
            certificate.get("certificateStatus", {}).get("code", "").split(".")[-1],
            certificate.get("issueDate", None),
            certificate.get("expiryDate", None),
            details_url
        )

        self.db.execute(certificate_query, certificate_params)

    def check_notified_body_id(self, notified_body_id):
        """
        Check if the notified body ID exists in the database.
        If not, log a warning.
        """
        if self.notified_body_exists(notified_body_id):
            logging.warning(f"Notified body with ID {notified_body_id} does exist.")
        
        # if the notified body does not exist, insert it
        notified_body_insert_query = """
        INSERT INTO notified_bodies (notified_body_id)
        VALUES (%s)
        ON CONFLICT (notified_body_id) DO NOTHING;
        """
        self.db.execute(notified_body_insert_query, (notified_body_id,))

    def notified_body_exists(self, notified_body_id: str) -> bool:
        try:
            query = "SELECT 1 FROM notified_bodies WHERE notified_body_id = %s LIMIT 1;"
            self.db.cursor.execute(query, (notified_body_id,))
            return self.db.cursor.fetchone() is not None
        except Exception as e:
            logging.warning(f"Check failed for notified body {notified_body_id}: {e}")
            return False

    def certificate_exists(self, uuid):
        try:
            query = "SELECT COUNT(*) FROM certificates WHERE uuid = %s"
            self.db.cursor.execute(query, (uuid,))
            result = self.db.cursor.fetchone()
            return result[0] > 0 if result else False
        except Exception as e:
            logging.warning(f"Check failed for certificate {uuid}: {e}")
            return False


    def insert_certificate_details(self, certificate, document_url):
        """
        Insert certificate details into the database.
        """
        uuid = certificate.get("uuid")
        if not uuid:
            logging.warning("Certificate UUID is missing, skipping details insert.")
            return
        
        certificate_id = certificate.get("certificateNumber", "")
        notified_body_id = certificate.get("notifiedBody", {}).get("srn", "")

        try:
            # ==== insert notified_body ====
            notified_body = certificate.get("notifiedBody", {})
            nb_uuid = notified_body.get("uuid", "")
            nb_id = notified_body.get("srn", "")
            nb_name = notified_body.get("name", "")
            nb_country = notified_body.get("countryName", "")
            nb_address = notified_body.get("geographicalAddress", "")
            nb_phone = notified_body.get("telephone", "")
            nb_mail = notified_body.get("electronicMail", "")

            notified_body_query = """
            INSERT INTO notified_bodies (
                notified_body_id, uuid, name, country, address, phone, email
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (notified_body_id) DO UPDATE SET
                uuid = EXCLUDED.uuid,
                name = EXCLUDED.name,
                country = EXCLUDED.country,
                address = EXCLUDED.address,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email
            """

            notified_body_params = (
                nb_id,
                nb_uuid,
                nb_name,
                nb_country,
                nb_address,
                nb_phone,
                nb_mail
            )

            self.db.execute(notified_body_query, notified_body_params)

            # ==== insert certificate_details ====
            application_legislation = certificate.get("applicableLegislation", {}).get("code", "").split(".")[-1]
            certificate_type = certificate.get("type", {}).get("code", "").split(".")[-1]
            certificate_identifier = certificate.get("certificateId", "")
            issue_date = certificate.get("issueDate", None)
            validity_start_date = certificate.get("startingValidityDate", None)
            expiry_date = certificate.get("expiryDate", None)
            certificate_status = certificate.get("status", {}).get("code", "").split(".")[-1]
            languages = certificate.get("languages", [{}])
            if isinstance(languages, list) and languages:
                certificate_language = languages[0].get("name", "")
            else:
                certificate_language = languages

            documents = certificate.get("documents", [])
            if documents and isinstance(documents, list):
                first_doc = documents[0]
                certificate_document_name = first_doc.get("originalFileName", "")
                certificate_document_language = first_doc.get("languages", [{}])[0].get("name", "")
                doc_uuid = first_doc.get("uuid")
            else:
                certificate_document_name = ""
                certificate_document_language = ""
                doc_uuid = None

            certificate_document_path = document_url + doc_uuid if doc_uuid else ""


            certificate_details_query = """
            INSERT INTO certificate_details (
                certificate_uuid,
                certificate_id,
                applicable_legislation,
                certificate_type,
                certificate_identifier,
                issue_date,
                validity_start_date,
                expiry_date,
                certificate_status,
                certificate_language,
                certificate_document_name,
                certificate_document_lang,
                certificate_document_path
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
            """
            certificate_details_params = (
                uuid,
                certificate_id,
                application_legislation,
                certificate_type,
                certificate_identifier,
                issue_date,
                validity_start_date,
                expiry_date,
                certificate_status,
                certificate_language,
                certificate_document_name,
                certificate_document_language,
                certificate_document_path
            )

            self.db.execute(certificate_details_query, certificate_details_params)

            # ==== insert certificate_udi ====
            scopes = certificate.get("scopes")
            if not scopes or not isinstance(scopes, list):
                logging.error(f"No valid scopes found for certificate {uuid}, skipping UDI insert.")
                scopes = []
            if not scopes:
                logging.error(f"No scopes found for certificate {uuid}, skipping UDI insert.")
                return

            for product in scopes:
                certificate_uuid = uuid
                intended_purpose = product.get("intendedPurpose", {}).get("text", "")

                basic_udi = product.get("basicUdiData", {})
                if isinstance(basic_udi, dict):
                    udi_di_uuid = basic_udi.get("uuid", "")
                elif isinstance(basic_udi, list):
                    udi_di_uuid = basic_udi[0].get("uuid", "")
                elif basic_udi is None:
                    udi_di_uuid = product.get("deviceGroupIdentification", "")
                else:
                    udi_di_uuid = ""



                certificate_udi_query = """
                INSERT INTO certificate_udi (
                    certificate_uuid,
                    devices,
                    intended_purpose
                ) VALUES (
                    %s, %s, %s
                );
                """
                certificate_udi_params = (
                    certificate_uuid,
                    udi_di_uuid,
                    intended_purpose
                )

                self.db.execute(certificate_udi_query, certificate_udi_params)

                # ==== insert device_type_code ====
                device_type_codes = product.get("deviceTypeCodes", [{}])
                if isinstance(device_type_codes, list) and device_type_codes:
                    device_type_code_entry = device_type_codes[0]
                elif isinstance(device_type_codes, dict):
                    device_type_code_entry = device_type_codes
                else:
                    device_type_code_entry = {}
                    
                certificate_udi_id = device_type_code_entry.get("uuid", "")
                code = device_type_code_entry.get("code", "")
                description = device_type_code_entry.get("description", {}).get("text", "")

                device_type_codes_query = """
                INSERT INTO device_type_codes (
                    certificate_udi_id,
                    certificate_uuid,
                    code,
                    description
                ) VALUES (
                    %s, %s, %s, %s
                )
                ON CONFLICT (certificate_udi_id) DO UPDATE SET
                    certificate_uuid = EXCLUDED.certificate_uuid,
                    code = EXCLUDED.code,
                    description = EXCLUDED.description;
                """
                device_type_codes_params = (
                    certificate_udi_id,
                    certificate_uuid,
                    code,
                    description
                )
                self.db.execute(device_type_codes_query, device_type_codes_params)

                # ==== insert horizontal_codes ====
                horizontal_codes = product.get("horizontalDeviceTypeCodes", [{}])
                for entry in horizontal_codes or []:
                    code = entry.get("code", "")
                    description = entry.get("description", {}).get("text", "")
                    entry_uuid = entry.get("uuid", "")

                    horizontal_codes_query = """
                    INSERT INTO horizontal_codes (
                        certificate_udi_id,
                        certificate_uuid,
                        code,
                        description
                    ) VALUES (%s, %s, %s, %s)
                    ON CONFLICT (certificate_udi_id) DO UPDATE SET
                        certificate_uuid = EXCLUDED.certificate_uuid,
                        code = EXCLUDED.code,
                        description = EXCLUDED.description;
                    """
                    horizontal_codes_params = (
                        entry_uuid,
                        certificate_uuid,
                        code,
                        description
                    )
                    self.db.execute(horizontal_codes_query, horizontal_codes_params)
                
                # ==== insert sscps ====
                sscps = product.get("sscps", [])
                for entry in sscps or []:
                    sscps_reference = entry.get("referenceNumber", "")
                    revision_number = entry.get("revisionNumber", "")
                    issue_date = entry.get("issueDate", None)
                    sscp_doc = entry.get("sscpDocuments", [])
                    if sscp_doc and isinstance(sscp_doc, list):
                        doc_entry = sscp_doc[0].get("document", {})
                        master_document_path = document_url + doc_entry.get("uuid", "")
                        upload_date = sscp_doc[0].get("uploadDate", None)
                    else:
                        master_document_path = ""
                        upload_date = None


                    sscp_query = """
                    INSERT INTO certificate_sscp (
                        sscp_reference,
                        certificate_uuid,
                        certificate_id,
                        revision_number,
                        issue_date,
                        master_document_path,
                        upload_date,
                        notified_body_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (sscp_reference) DO UPDATE SET
                        certificate_uuid = EXCLUDED.certificate_uuid,
                        certificate_id = EXCLUDED.certificate_id,
                        revision_number = EXCLUDED.revision_number,
                        issue_date = EXCLUDED.issue_date,
                        master_document_path = EXCLUDED.master_document_path,
                        upload_date = EXCLUDED.upload_date,
                        notified_body_id = EXCLUDED.notified_body_id;
                    """
                    sscp_params = (
                        sscps_reference,
                        certificate_uuid,
                        certificate_id,
                        revision_number,
                        issue_date,
                        master_document_path,
                        upload_date,
                        notified_body_id
                    )
                    self.db.execute(sscp_query, sscp_params)

            logging.info(f"Certificate {uuid} inserted successfully.")
        except Exception as e:
            logging.error(f"Error inserting certificate {uuid}: {e}")
            raise e
        else:
            logging.info(f"Certificate {uuid} inserted successfully with details.")
        finally:
            # Commit the transaction if everything was successful
            self.db.commit()

                
