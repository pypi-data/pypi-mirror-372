CREATE TYPE IF NOT EXISTS vertebrae AS ENUM ('S1', 'L5', 'L4', 'L3', 'L2', 'L1', 'T12', 'T11', 'T10', 'T9', 'T8', 'T7', 'T6', 'T5', 'T4', 'T3', 'T2', 'T1', 'C7', 'C6', 'C5', 'C4', 'C3', 'C2', 'C1');
CREATE TYPE IF NOT EXISTS aorta_regions AS ENUM ('whole', 'root', 'asc', 'arch', 'desc', 'up_abd', 'lw_abd');
CREATE TYPE IF NOT EXISTS tissue_volume_region AS ENUM ('total', 'abdominal', 'chest');
CREATE TYPE IF NOT EXISTS tissue_type AS ENUM ('subq_fat', 'visc_fat', 'skeletal_muscle', 'body', 'body_extremities');
CREATE TYPE IF NOT EXISTS tissue_measurement AS ENUM ('area_cm2', 'border_ratio', 'raw_perimeter_cm', 'ellipse_perimeter_cm', 'circle_perimeter_cm');
CREATE TYPE IF NOT EXISTS diameter_measurement AS ENUM ('max', 'min', 'mid', 'proximal', 'distal');

CREATE TABLE IF NOT EXISTS conversions (
    series_uid VARCHAR CHECK (LENGTH(series_uid) <= 64), 
    study_uid VARCHAR CHECK (LENGTH(series_uid) <= 64), 
    nifti VARCHAR, 
    modality VARCHAR CHECK (LENGTH(modality) <= 5), 
    mrn VARCHAR CHECK (LENGTH(mrn) <= 10), 
    accession VARCHAR CHECK (LENGTH(accession) <= 12), 
    series_name VARCHAR, 
    series_number INTEGER, 
    scan_date DATE, 
    original_series_name VARCHAR, 
    study_description VARCHAR, 
    ct_direction VARCHAR, 
    image_type VARCHAR, 
    sex VARCHAR, 
    age INTEGER, 
    birth_date DATE, 
    height_m REAL, 
    weight_kg REAL, 
    pregnancy_status INTEGER, 
    pixel_length_mm REAL, 
    pixel_width_mm REAL, 
    slice_thickness_mm REAL, 
    manufacturer VARCHAR, 
    model VARCHAR, 
    kvp REAL, 
    sequence_name VARCHAR, 
    protocol_name VARCHAR, 
    contrast_bolus_agent VARCHAR, 
    contrast_bolus_route VARCHAR, 
    contrast_bolus_volume REAL, 
    dicom_folder VARCHAR, 
    conversion_date VARCHAR, 
    PRIMARY KEY (series_uid)
);

CREATE TABLE IF NOT EXISTS segmentations (
    nifti VARCHAR, 
    series_uid varchar(64), 
    task USMALLINT, 
    seg_file VARCHAR, 
    seg_date VARCHAR, 
    status VARCHAR, 
    failed_error VARCHAR, 
    PRIMARY KEY (nifti, task, seg_date)
);

CREATE TABLE IF NOT EXISTS metadata (
    nifti VARCHAR, 
    series_uid varchar(64), 
    study_uid varchar(64), 
    output_stats_file VARCHAR, 
    modality VARCHAR, 
    mrn VARCHAR CHECK (LENGTH(mrn) <= 10), 
    accession VARCHAR CHECK (LENGTH(accession) <= 12), 
    series_name VARCHAR, 
    series_number USMALLINT, 
    scan_date DATE, 
    original_series_name VARCHAR, 
    study_description VARCHAR, 
    ct_direction VARCHAR, 
    abdominal_scan INTEGER, 
    chest_scan INTEGER, 
    correct_vertebrae_order INTEGER, 
    lowest_vertebra vertebrae, 
    highest_vertebra vertebrae, 
    image_type VARCHAR, 
    sex VARCHAR, 
    age USMALLINT, 
    birth_date DATE, 
    height_m REAL, 
    weight_kg REAL, 
    pregnancy_status INTEGER, 
    pixel_length_mm REAL, 
    pixel_width_mm REAL, 
    slice_thickness_mm REAL, 
    manufacturer VARCHAR, 
    model VARCHAR, 
    kvp REAL, 
    sequence_name VARCHAR,
    protocol_name VARCHAR, 
    contrast_bolus_agent VARCHAR, 
    contrast_bolus_route VARCHAR, 
    contrast_bolus_volume REAL, 
    dicom_folder VARCHAR, 
    conversion_date VARCHAR, 
    PRIMARY KEY (nifti)
);

CREATE TABLE IF NOT EXISTS vol_int (
                nifti VARCHAR, series_uid varchar(64), structure VARCHAR, volume_cm3 REAL, hu_mean REAL, hu_std_dev REAL, PRIMARY KEY (nifti, structure)
            );
CREATE TABLE IF NOT EXISTS contrast (
                nifti VARCHAR, series_uid varchar(64), phase VARCHAR, probability REAL, pi_time REAL, pi_time_std REAL, PRIMARY KEY (nifti)
            );
CREATE TABLE IF NOT EXISTS vertebrae (
                nifti VARCHAR, series_uid varchar(64), vertebra vertebrae, midline INTEGER, PRIMARY KEY (nifti, vertebra)
            );
CREATE TABLE IF NOT EXISTS aorta_metrics (
                nifti VARCHAR, series_uid varchar(64), region aorta_regions, entire_region TINYINT, length_mm REAL, tortuosity_index REAL, icm REAL, n_inflections INTEGER, peria_volume_cm3 REAL, peria_ring_volume_cm3 REAL, peria_fat_volume_cm3 REAL, peria_hu_mean REAL, peria_hu_std REAL, calc_volume_mm3 REAL, calc_agatston REAL, calc_count INTEGER, is_120_kvp INTEGER, mean_diameter_mm REAL, mean_roundness REAL, mean_flatness REAL, PRIMARY KEY (nifti, region)
            );
CREATE TABLE IF NOT EXISTS aorta_diameters (
                nifti VARCHAR, series_uid varchar(64), region aorta_regions, measure diameter_measurement, mean_diameter_mm REAL, major_diameter_mm REAL, minor_diameter_mm REAL, area_mm2 REAL, roundness REAL, flatness REAL, rel_distance REAL, entire_region INTEGER, PRIMARY KEY (nifti, region, measure)
            );
CREATE TABLE IF NOT EXISTS tissues_volumetric (
                nifti VARCHAR, series_uid varchar(64), region tissue_volume_region, structure tissue_type, volume_cm3 REAL, hu_mean REAL, hu_std_dev REAL, PRIMARY KEY (nifti, region, structure)
            );
CREATE TABLE IF NOT EXISTS tissues_vertebral (
                nifti VARCHAR, series_uid varchar(64), vertebra vertebrae, structure tissue_type, measurement tissue_measurement, value REAL, PRIMARY KEY (nifti, vertebra, structure, measurement)
            );
CREATE TABLE IF NOT EXISTS iliac (
                nifti VARCHAR, series_uid varchar(64), side VARCHAR, length_mm REAL, location diameter_measurement,  metric VARCHAR, value REAL, PRIMARY KEY (nifti, side, location, metric)
)
