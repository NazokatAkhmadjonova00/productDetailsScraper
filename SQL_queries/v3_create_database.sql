-- ========================
-- DROP ALL EXISTING TABLES
-- ========================
DROP TABLE IF EXISTS
    sscp_basic_udi,
    certificate_details,
    certificate_udi,
    certificate_sscp,
    certificates,
    notified_bodies,
    horizontal_codes,
    device_type_codes,
    market_distribution,
    device_udi_di_details,
    device_basic_udi_detail,
    devices,
    competent_authority,
    person_responsible,
    operator_contact,
    operator_address,
    operator_identification,
    operators;

-- ========================
-- CREATE TABLES
-- ========================

-- === Operators ===
CREATE TABLE operators (
    uuid TEXT PRIMARY KEY,
    actor_id TEXT UNIQUE,
    version TEXT,
    role TEXT,
    name TEXT,
    abbreviated_name TEXT,
    city_name TEXT,
    country TEXT,
    details_url TEXT
);

CREATE TABLE operator_identification (
    id SERIAL PRIMARY KEY,
    operator_uuid TEXT REFERENCES operators(uuid),
    actor_id TEXT,
    role TEXT,
    country TEXT,
    name TEXT,
    abbreviated_name TEXT,
    vat_number TEXT,
    eori TEXT,
    trade_register TEXT,
    confirmation_date DATE
);

CREATE TABLE operator_address (
    id SERIAL PRIMARY KEY,
    operator_uuid TEXT REFERENCES operators(uuid),
    actor_id TEXT,
    street TEXT,
    street_number TEXT,
    address_line_2 TEXT,
    post_box TEXT,
    city TEXT,
    zip_code TEXT,
    country TEXT,
    latitude TEXT,
    longitude TEXT
);

CREATE TABLE operator_contact (
    id SERIAL PRIMARY KEY,
    operator_uuid TEXT REFERENCES operators(uuid),
    actor_id TEXT,
    email TEXT,
    phone TEXT,
    website TEXT
);

CREATE TABLE person_responsible (
    id SERIAL PRIMARY KEY,
    operator_uuid TEXT REFERENCES operators(uuid),
    actor_id TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    responsible_for TEXT,
    street TEXT,
    street_number TEXT,
    address_line_2 TEXT,
    post_box TEXT,
    city TEXT,
    zip_code TEXT,
    country TEXT,
    latitude TEXT,
    longitude TEXT
);

CREATE TABLE competent_authority (
    id SERIAL PRIMARY KEY,
    operator_uuid TEXT REFERENCES operators(uuid),
    actor_id TEXT,
    name TEXT,
    street TEXT,
	street_number INTEGER,
	address_line_2 TEXT,
	post_box TEXT,
	postal_code TEXT,
	city TEXT,
    country TEXT,
    email TEXT,
    phone TEXT
);

-- === Devices ===
CREATE TABLE devices (
    uuid TEXT PRIMARY KEY,
    eudamed_id TEXT,
    udi_id TEXT,
    version TEXT,
    trade_name TEXT,
    risk_class TEXT,
    manufacturer TEXT,
    actor_id TEXT,
    issuing_entity TEXT,
    intended_purpose TEXT,
    details_url TEXT
);

CREATE TABLE device_basic_udi_detail (
    id SERIAL PRIMARY KEY,
    device_uuid TEXT REFERENCES devices(uuid),
	eudamed_id TEXT,
    applicable_legislation TEXT,
    procedure_pack_device_itself TEXT,
    authorised_representative TEXT,
    risk_class TEXT,
    implantable TEXT,
    is_suture_or_implant_part TEXT,
    measuring_function TEXT,
    reusable_surgical_instrument TEXT,
    active_device TEXT,
    intended_to_administer_or_remove_medicinal_product TEXT,
    device_model TEXT,
    device_name TEXT,
    contains_human_tissues TEXT,
    contains_animal_tissues TEXT,
    contains_medicinal_substance TEXT,
    contains_blood_derived_medicinal_substance TEXT
);

CREATE TABLE device_udi_di_details (
    id SERIAL PRIMARY KEY,
    device_uuid TEXT REFERENCES devices(uuid),
	eudamed_id TEXT,
    udi_di_code TEXT,
    status TEXT,
    udi_di_secondary TEXT,
    nomenclature_code TEXT,
    trade_name TEXT,
    reference_number TEXT,
    direct_marking_di TEXT,
    quantity_of_device INTEGER,
    type_of_udi_pi TEXT,
    additional_product_description TEXT,
    additional_info_url TEXT,
    clinical_sizes TEXT,
    labelled_single_use TEXT,
    needs_sterilisation_before_use TEXT,
    labelled_as_sterile TEXT,
    contains_latex TEXT,
    storage_conditions TEXT,
    reprocessed_single_use TEXT,
    intended_non_medical_use TEXT,
    market_member_state TEXT,
    related_devices TEXT
);

CREATE TABLE market_distribution (
    id SERIAL PRIMARY KEY,
	device_uuid TEXT REFERENCES devices(uuid),
	eudamed_id TEXT,
    country TEXT,
    start_date DATE,
    end_date DATE
);


-- === Certificates ===
CREATE TABLE notified_bodies (
    notified_body_id TEXT PRIMARY KEY,
    uuid TEXT UNIQUE,
    name TEXT,
    country TEXT,
    address TEXT,
    phone TEXT,
    email TEXT
);

CREATE TABLE certificates (
    uuid TEXT PRIMARY KEY,
    certificate_id TEXT,
    certificate_version TEXT,
    certificate_type TEXT,
    actor_id TEXT,
    authorizedRepresentativeSrns TEXT,
    notified_body_id TEXT REFERENCES notified_bodies(notified_body_id),
    status TEXT,
    start_date DATE,
    expiry_date DATE,
    details_url TEXT
);

CREATE TABLE certificate_details (
    id SERIAL PRIMARY KEY,
    certificate_uuid TEXT REFERENCES certificates(uuid),
	certificate_id TEXT,
    applicable_legislation TEXT,
    certificate_type TEXT,
    certificate_identifier TEXT,
    issue_date DATE,
    validity_start_date DATE,
    expiry_date DATE,
    certificate_status TEXT,
    certificate_language TEXT, 
    certificate_document_name TEXT,
    certificate_document_lang TEXT,
    certificate_document_path TEXT  
);

CREATE TABLE certificate_udi (
    id SERIAL PRIMARY KEY,
    certificate_uuid TEXT REFERENCES certificates(uuid),
    intended_purpose TEXT
);

CREATE TABLE certificate_sscp (
    sscp_reference TEXT PRIMARY KEY,
    certificate_uuid TEXT REFERENCES certificates(uuid),
	certificate_id TEXT,
    revision_number TEXT,
    issue_date DATE,
    master_document_path TEXT,   
    upload_date DATE,
    notified_body_id TEXT REFERENCES notified_bodies(notified_body_id)
);

CREATE TABLE sscp_basic_udi (
    id SERIAL PRIMARY KEY,
    sscp_reference TEXT REFERENCES certificate_sscp(sscp_reference),
    eudamed_id TEXT
);

CREATE TABLE device_type_codes (
	certificate_udi_id TEXT PRIMARY KEY,
    certificate_uuid TEXT REFERENCES certificates(uuid),
    code TEXT,
    description TEXT
);

CREATE TABLE horizontal_codes (
	certificate_udi_id TEXT PRIMARY KEY,
    certificate_uuid TEXT REFERENCES certificates(uuid),
    code TEXT,
    description TEXT
);
