DROP DATABASE IF EXISTS IEM_WBB;

CREATE DATABASE IEM_WBB;

\c iem_wbb

CREATE TABLE pacients(id serial PRIMARY KEY, name text, sex char(5), age smallint, height numeric(3,2), weight numeric(5,2), imc numeric(3,1));
CREATE TABLE exams(id SERIAL PRIMARY KEY, APs NUMERIC(16,15)[], MLs NUMERIC(16,15)[], date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), pac_id INT REFERENCES pacients(id));
CREATE TABLE devices(id SERIAL PRIMARY KEY,name VARCHAR(50),mac VARCHAR(17), is_default BOOLEAN);