#Copyright (C) 2007 L. Donnie Smith

PACKAGE_NAME = CWiid
PACKAGE_TARNAME = cwiid
PACKAGE_VERSION = 3.0.0
PACKAGE_STRING = CWiid 3.0.0
PACKAGE_BUGREPORT = https://github.com/azzra/python3-wiimote/issues

prefix = /usr/local
exec_prefix = ${prefix}

sysconfdir = ${prefix}/etc
libdir = ${exec_prefix}/lib

datarootdir = ${prefix}/share
mandir = ${datarootdir}/man
docdir = ${datarootdir}/doc/${PACKAGE_TARNAME}

CC = gcc
AWK = mawk
LEX = flex
YACC = bison -y
PYTHON = python3

COMMON = /home/rai/Documentos/iem-wbb/python3-wiimote/common

ifdef DESTDIR
	ROOTDIR = $(DESTDIR:%/=%)
endif

DEBUGFLAGS = -g
WARNFLAGS = -Wall -W
CFLAGS = $(DEBUGFLAGS) $(WARNFLAGS) -DHAVE_CONFIG_H -I$(COMMON)/include
