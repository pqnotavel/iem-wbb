DROP DATABASE IF EXISTS test;

CREATE DATABASE test;

\c test

CREATE EXTENSION pgcrypto;

CREATE TABLE tb_user( username varchar(50) PRIMARY KEY, password VARCHAR(72) NOT NULL);
WITH x AS ( 
	SELECT 
		'foo'::text AS user, 
		'123'::text AS pw, 
		gen_salt('md5')::text AS salt ) 

INSERT INTO tb_user (username, password) 
	SELECT 
		x.user, 
		crypt(x.pw, x.salt)

	FROM x;