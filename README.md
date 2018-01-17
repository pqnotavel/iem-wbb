Copyright (C) 2017 Raí Sales Pereira Bizerra

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
  
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
  
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

-----------------------------------------------------------------------------------------------------------------------
IEM_WBB
-----------------------------------------------------------------------------------------------------------------------

DESCRIPTION
-----------------------------------------------------------------------------------------------------------------------
System for instrumentation of medical examinations, wii balance board version.

REQUIREMENTS
-----------------------------------------------------------------------------------------------------------------------
Packages - sudo apt-get install flex bison libbluetooth-dev libcwiid-dev python-gobject python3-tk python3-dev

PostgreSQL - https://www.postgresql.org/download/linux/ubuntu/

Python3 - sudo apt-get install python3

pip - 	1. Download get-pip.py at https://bootstrap.pypa.io/get-pip.py
		2. sudo python3 get-pip.py

Python3 modules - 	sudo pip3 install awk flex pybluez xlrd xlwt xlutils matplotlib psycopg2
			cwiid - https://github.com/azzra/python3-wiimote

POSTGRESQL CONFIGURATION
-----------------------------------------------------------------------------------------------------------------------
Step 1 - Changing UNIX postgres password

	First of all, you have to set/change the password of the new UNIX user (postgres) with the following command:
	
		sudo passwd postgres

	You will be asked to type and retype the new UNIX password.

Step 2. Accessing UNIX postgres account in the terminal

	To access UNIX postgres account in the terminal, you will use the following command:

		su - postgres

	You will be asked to type the postgres password created on the first step.

Step 3. Changing the password of PostgreSQL default user

	After setting/changing the UNIX postgres password, you have to change the password of PostgreSQL default user, also named as postgres. To do so, you will use the following commands:

		psql
		ALTER ROLE postgres WITH PASSWORD 'postgres';

Step 4. Creating iem_wbb DATABASE

	To create the appication database in PostgreSQL, you will use the file "scripts.sql". Still inside psql and knowing the path to "scripts.sql", type in the terminal:

		\i /path_to_scripts.sql/scripts.sql

	You will see returns like these in the terminal:

		DROP DATABASE
		CREATE DATABASE
		Você está conectado agora ao banco de dados "iem_wbb" como usuário "postgres".
		CREATE EXTENSION
		CREATE TABLE
		CREATE TABLE
		CREATE TABLE
		CREATE TABLE
		BEGIN
		INSERT 0 1
		INSERT 0 1
		INSERT 0 1
		COPY 1
		COMMIT

EXECUTION
-----------------------------------------------------------------------------------------------------------------------
python3 iem-wbb.py
