-- ========================
-- TABELLE: Operators
-- ========================
CREATE TABLE operators (
    actor_id TEXT PRIMARY KEY,
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
    actor_id TEXT NOT NULL REFERENCES operators(actor_id),
    role TEXT,
    country TEXT,
    name TEXT,
    abbreviated_name TEXT,
    vat_number TEXT,
    eori TEXT,
    national_trade_register TEXT,
    confirmation_date DATE
);

CREATE TABLE operator_address (
    id SERIAL PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES operators(actor_id),
    street TEXT,
    street_number TEXT,
    address_line_2 TEXT,
    po_box TEXT,
    city TEXT,
    zip_code TEXT,
    country TEXT,
    latitude TEXT,
    longitude TEXT
);

CREATE TABLE operator_contact (
    id SERIAL PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES operators(actor_id),
    email TEXT,
    phone TEXT,
    website TEXT
);

CREATE TABLE person_responsible (
    id SERIAL PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES operators(actor_id),
    first_name TEXT,
    last_name TEXT,
    mail TEXT,
    phone TEXT,
    responsible_for TEXT,
    street TEXT,
    street_number TEXT,
    address_line_2 TEXT,
    po_box TEXT,
    city TEXT,
    zip_code TEXT,
    country TEXT,
    latitude TEXT,
    longitude TEXT
);

CREATE TABLE competent_authority (
    id SERIAL PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES operators(actor_id),
    name TEXT,
    address TEXT,
    country TEXT,
    mail TEXT,
    phone TEXT
);


-- ========================
-- TABELLE: Devices
-- ========================

CREATE TABLE devices (
	eudamed_id TEXT PRIMARY KEY,
    udi_id TEXT,
    version TEXT,
    trade_name TEXT,
    risk_class TEXT,
    manufacturer TEXT,
    actor_id TEXT REFERENCES operators(actor_id),
	issuing_entity TEXT,
    intended_purpose TEXT,
    details_url TEXT
);

CREATE TABLE device_basic_udi_detail (
    id SERIAL PRIMARY KEY,
    eudamed_id TEXT REFERENCES devices(eudamed_id),
    applicable_legislation TEXT,
	procedure_pack_device_itself TEXT,
	authorised_representative TEXT,
	risk_class TEXT,
	
	implantable BOOLEAN,
	is_suture_or_implant_part BOOLEAN,
    measuring_function BOOLEAN,
    reusable_surgical_instrument BOOLEAN,
    active_device BOOLEAN,
	intended_to_administer_or_remove_medicinal_product BOOLEAN,

    device_model TEXT,
    device_name TEXT,
	
	contains_human_tissues BOOLEAN,
    contains_animal_tissues BOOLEAN,

    contains_medicinal_substance BOOLEAN,
    contains_blood_derived_medicinal_substance BOOLEAN
);

CREATE TABLE device_udi_di_details (
    id SERIAL PRIMARY KEY,
    eudamed_id TEXT REFERENCES devices(eudamed_id),
    
    udi_di_code TEXT,
    status TEXT,
    udi_di_secondary TEXT,
    
    nomenclature_code TEXT,
    trade_name TEXT,
    reference_number TEXT,
    direct_marking_di BOOLEAN,
    quantity_of_device INTEGER,
    
    type_of_udi_pi TEXT,
    additional_product_description TEXT,
    additional_info_url TEXT,

	clinical_sizes TEXT,
	
    labelled_single_use BOOLEAN,
    needs_sterilisation_before_use BOOLEAN,
    labelled_as_sterile BOOLEAN,
    contains_latex BOOLEAN,
    
    storage_conditions TEXT,
    reprocessed_single_use BOOLEAN,
    intended_non_medical_use BOOLEAN,
    
    market_member_state TEXT,
	related_devices TEXT
);

CREATE TABLE market_distribution (
    id SERIAL PRIMARY KEY,
    eudamed_id TEXT REFERENCES devices(eudamed_id),
    country TEXT,
    start_date DATE,
    end_date DATE
);

CREATE TABLE device_type_codes (
    id SERIAL PRIMARY KEY,
    eudamed_id TEXT REFERENCES devices(eudamed_id),
    code TEXT,
    description TEXT
);


CREATE TABLE horizontal_codes (
    id SERIAL PRIMARY KEY,
    eudamed_id TEXT REFERENCES devices(eudamed_id),
    code TEXT,
    description TEXT
);


-- ========================
-- TABELLE: Certificates
-- ========================

CREATE TABLE notified_bodies (
    notified_body_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT,
    address TEXT,
    phone TEXT,
    email TEXT
);

CREATE TABLE certificates (
    certificate_id TEXT PRIMARY KEY,
    certificate_version TEXT,
    certificate_type TEXT,
    
    manufacturer_actor_id TEXT REFERENCES operators(actor_id),
    auth_rep_actor_id TEXT REFERENCES operators(actor_id),
	
    notified_body_id TEXT NOT NULL REFERENCES notified_bodies(notified_body_id),
    
	status TEXT,

    start_date DATE,
    expiry_date DATE,

    details_url TEXT
);

CREATE TABLE certificate_details (
    id SERIAL PRIMARY KEY,
    certificate_id TEXT REFERENCES certificates(certificate_id),
    
    applicable_legislation TEXT,
    certificate_type TEXT,
    certificate_identifier TEXT,
    
    issue_date DATE,
    validity_start_date DATE,
    expiry_date DATE,
    
    certificate_status TEXT,
    certificate_languages TEXT, 
    
    certificate_document_name TEXT,
    certificate_document_lang TEXT,
    certificate_document_path TEXT  
);

CREATE TABLE certificate_udi (
    id SERIAL PRIMARY KEY,
    certificate_id TEXT REFERENCES certificates(certificate_id),
    eudamed_id TEXT REFERENCES devices(eudamed_id)
);

CREATE TABLE certificate_sscp (
    id SERIAL PRIMARY KEY,
    certificate_id TEXT REFERENCES certificates(certificate_id),
    
    sscp_reference TEXT, 
    revision_number TEXT,
    issue_date DATE,

    master_document_name TEXT,   
    master_document_version TEXT,
    master_document_status TEXT, 
    upload_date DATE,

    notified_body_id TEXT REFERENCES notified_bodies(notified_body_id)
);

CREATE TABLE sscp_basic_udi (
    id SERIAL PRIMARY KEY,
    sscp_id INTEGER REFERENCES certificate_sscp(id),
    eudamed_id TEXT REFERENCES devices(eudamed_id)
);
