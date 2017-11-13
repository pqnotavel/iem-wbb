#!/usr/bin/env python3 
# _*_ encoding: utf-8 _*_ 

from argparse import ArgumentParser 
from getpass import getpass 
from os import system 
from psycopg2 import connect 
from psycopg2 import Error 
from sys import exit

# Argument parser 
parser = ArgumentParser() 

# Argument help strings 
help_d = 'Database' 
help_H = 'Hostname or IP address' 
help_p = 'Port' 
help_u = 'Username' 
help_w = 'With password prompt'

# Arguments creation 
parser.add_argument('-d', '--database', type=str, help=help_d, action='store', metavar='dbname', dest='dbname', default='postgres') 
parser.add_argument('-H', '--host', type=str, help=help_H, action='store', metavar='dbserver', dest='host', default=None) 
parser.add_argument('-p', '--port', type=int, help=help_p, action='store', metavar='port_number', dest='port', default=5432) 
parser.add_argument('-u', '--user', type=str, help=help_u, action='store', metavar='username', dest='user', default='postgres') 
parser.add_argument('-w', '--with-pass', help=help_w, action='store_true', dest='password') 

# Parsed arguments 
args = parser.parse_args()

# Test if password prompt is required
if args.password: 
	args.password = getpass('Database user password: ') 
else: 
	args.password = None 

# Connection string variable (initially as a list) 
conn_str = [] 

# Take all provided paramaters and make the connection string 
for k, v in vars(args).items(): 
	if v: 
		str_tmp = "{} = '{}'".format(k, v) 
		conn_str.append(str_tmp) 
conn_str = ' '.join(conn_str)

# SQL string for PREPARE command 
sql_prepare = """ PREPARE q_user (text, text) AS SELECT crypt($2, password) = password FROM tb_user WHERE username = $1; """ 

# SQL string for EXECUTE command 
sql_execute = "EXECUTE q_user('{}', '{}');" 

# When occur authentication error... 
def user_pw_error(connection): 
	print('nError: Invalid user and password combination!') 
	connection.close() 
	exit(1)

try: 
	# Connection 
	conn = connect(conn_str) 

	# Cursor creation to execute SQL commands 
	cursor = conn.cursor() 

	# Execute the SQL string in database 
	cursor.execute(sql_prepare) 

	# Clear Screen 
	system('clear') 

	# Get user and password of the application 
	app_user = input('nApplication user: ') 
	app_user_pw = getpass('Application user password: ') 

	# Execute the SQL string in database 
	cursor.execute(sql_execute.format(app_user, app_user_pw))

	# The result of the string SQL execution 
	res = cursor.fetchone() 
	try: 
		# User login validation 
		if res[0]: 
			print('nAcessed!') 
		else: 
			raise 
	except: 
		user_pw_error(conn) 
except Error as e: 
	print('nAn error has occurred!') 
	print(format(e)) 
	exit(1) 

# Close the database connection 
conn.close()
