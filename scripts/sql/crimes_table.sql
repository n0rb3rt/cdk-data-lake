CREATE DATABASE IF NOT EXISTS octank;

CREATE TABLE IF NOT EXISTS octank.crimes (
    `id` bigint,
    `case number` varchar(255),
    `date` varchar(255),
    `block` varchar(255),
    `iucr` varchar(255),
    `primary type` varchar(255),
    `description` varchar(255),
    `location description` varchar(255),
    `arrest` boolean,
    `domestic` boolean,
    `beat` bigint,
    `district` bigint,
    `ward` bigint,
    `community area` bigint,
    `fbi code` varchar(255),
    `x coordinate` bigint,
    `y coordinate` bigint,
    `year` bigint,
    `updated on` varchar(255),
    `latitude` double,
    `longitude` double,
    `location` varchar(255)
);

LOAD DATA FROM S3 PREFIX 's3://jnme-ab3-v1-ingest/crimes/precinct=001'
INTO TABLE octank.crimes
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
IGNORE 1 LINES;
