#!/usr/bin/python3
#_______________________________________________________________________
import os
import sys
import collections
import re
import shlex
import sqlite3
from sqlite3 import Error
import stat
import subprocess
import logging
log = logging.getLogger(__name__)
dbg = logging.getLogger('dbg.' + __name__)
#-----------------------------------------------------------------------
# Application specific
import util
#_______________________________________________________________________
# DEFS
#_______________________________________________________________________
#------------------------------------------------------------------------
def get_conn(db_file):
    '''
    '''
    #---------------------------------------
    dbg.info("START def get_conn(db_file):")
    #---------------------------------------
    dbg.info("db_file:" + db_file)
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        dbg.critical(e)
        exit(101)
    finally:
        if conn:
            return(conn)

    #---------------------------------------

    dbg.info("END def get_conn(db_file):")
#------------------------------------------------------------------------
def add_act(d_act):
    '''
    '''
    #---------------------------------------
    dbg.info("START def add_act(text):")
    #---------------------------------------
    tbl_cols = get_cols('actions')
    val_str = '('
#    for col, val in od_action:

    if action_type is None:
        action_type = 'NUL'

    out_lines = out.split('\n')
#    for line in out_lines:

    conn = get_conn(pm_db_file)
    cur = conn.cursor()
    cur.execute("""INSERT INTO actions
                   (user,
                   date,
                   host,
                   act,
                   rc,
                   out,
                   type,
                   cat)

                   VALUES('user'
                   date,
                   host,
                   cmd,
                   rc,
                   out
                   )""")
    conn.commit()
    conn.close()
    dbg.info("END def add_act(text):")
#------------------------------------------------------------------------
def create_pm_db():
    '''
    '''
    #---------------------------------------
    dbg.info("START def create_pm_db:")
    #---------------------------------------
    dbg.info("conn = get_conn(pm_db_file)")
    conn = get_conn(pm_db_file)
    dbg.info("cur = conn.cursor()")
    cur = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS actions ( '
    sql += 'user TEXT NOT NULL, '
    sql += 'date DATE NOT NULL, '
    sql += 'act TEXT NOT NULL, '
    sql += 'host TEXT NOT NULL, '
    sql += 'out TEXT NOT NULL, '
    sql += 'rc TEXT, '
    sql += 'type TEXT, '
    sql += 'cat TEXT, '
    sql += 'PRIMARY KEY (user, date, act), '
    sql += 'FOREIGN KEY (type) REFERENCES act_type (type), '
    sql += 'FOREIGN KEY (cat) REFERENCES act_cat (cat) '
    sql += ');'
    try:
        dbg.info("cur.execute(CREATE TABLE IF NOT EXISTS actions")
        cur.execute(sql)
    except Error as e:
        dbg.critical(e)
        exit(101)

    dbg.info("cur.execute(CREATE TABLE IF NOT EXISTS cmd")
    sql = 'CREATE TABLE IF NOT EXISTS cmd '
    sql += '(cmd TEXT NOT NULL, '
    sql += 'options TEXT NOT NULL, '
    sql += 'type TEXT, '
    sql += 'cat TEXT, '
    sql += 'help TEXT,'
    sql += 'PRIMARY KEY(cmd, options), '
    sql += 'FOREIGN KEY (type) REFERENCES cmd_type (type), '
    sql += 'FOREIGN KEY (cat) REFERENCES cmd_cat (cat) '
    sql += ');'
    try:
        cur.execute(sql)
    except Error as e:
        dbg.critical(e)
        exit(101)

    dbg.info("cur.execute(CREATE TABLE IF NOT EXISTS act_type")
    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS act_type
                 (type TEXT NOT NULL UNIQUE,
                 PRIMARY KEY (type)
                 );''')
    except Error as e:
        dbg.critical(e)
        exit(101)

    dbg.info("cur.execute(CREATE TABLE IF NOT EXISTS act_cat")
    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS act_cat
                 (cat TEXT NOT NULL UNIQUE,
                 PRIMARY KEY (cat)
                 );''')
    except Error as e:
        dbg.critical(e)
        exit(101)

    dbg.info("cur.execute(CREATE TABLE IF NOT EXISTS cmd_type")
    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS cmd_type
                 (type TEXT NOT NULL UNIQUE,
                 PRIMARY KEY (type)
                 );''')
    except Error as e:
        dbg.critical(e)
        exit(101)

    dbg.info("cur.execute(CREATE TABLE IF NOT EXISTS cmd_cat")
    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS cmd_cat
                 (cat TEXT NOT NULL UNIQUE,
                 PRIMARY KEY (cat)
                 );''')
    except Error as e:
        dbg.critical(e)
        exit(101)

    dbg.info("conn.commit()")
    conn.commit()
    dbg.info("conn.close()")
    conn.close()
    #---------------------------------------
    dbg.info("END def create_pm_db:")
#------------------------------------------------------------------------
#_______________________________________________________________________
# END DEFS
#_______________________________________________________________________
try:
    sess = os.environ['PM_SESS']
except KeyError:
    err_msg = "'PM_SESS' env var not set!"
    print(err_msg)

sys.path.insert(1, os.environ['PM_DIR'])
top_dir = os.environ['PM_DIR']
log_dir = os.environ['PM_LOG_DIR']
db_dir = os.environ['PM_DB_DIR']
pm_db_file = os.environ['PM_DB_FILE']
pm_db_name = 'pm'
data_dir = os.environ['PM_DATA_DIR']
tmp_dir = os.environ['PM_TMP_DIR']
user = os.environ['USER']

