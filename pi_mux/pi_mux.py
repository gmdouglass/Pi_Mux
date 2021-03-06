#!/usr/bin/python3
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import threading
import time
import os
import sys
#---------------------------------------
# Application specific
try:
    sess = os.environ['PM_SESS']
except KeyError:
    err_msg = "'PM_SESS' env var not set!"
    print(err_msg)

top_dir = os.environ['PM_DIR']
log_dir = os.environ['PM_LOG_DIR']
db_dir = os.environ['PM_DB_DIR']
pm_db = os.environ['PM_DB_FILE']
data_dir = os.environ['PM_DATA_DIR']
tmp_dir = os.environ['PM_TMP_DIR']
sys.path.insert(1, top_dir)
import db
import tm
import util
#_______________________________________________________________________
# LOGGING CONFIG
#_______________________________________________________________________
import logging
import logging.handlers
user = os.environ['USER']
# application log file
app_log_format = logging.Formatter('%(asctime)s [%(levelname)-8s] %(threadName)s:%(filename)s\n%(message)s\n')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
f_app_log = os.path.join(log_dir, user + '.log')
fh_app_log = logging.handlers.RotatingFileHandler(f_app_log)
fh_app_log.setLevel('DEBUG')
fh_app_log.setFormatter(app_log_format)
log.addHandler(fh_app_log)
#---------------------------------------
# Application console logging
app_con_format = logging.Formatter('%(filename)s:%(levelname)-8s:%(message)s')
app_ch = logging.StreamHandler()
#ch.setLevel('WARN')
app_ch.setFormatter(app_con_format)
log.addHandler(app_ch)
#---------------------------------------
# debug log file
dbg_format = logging.Formatter('%(asctime)s [%(levelname)-8s] %(threadName)s:%(filename)s:line %(lineno)4s\n%(message)s\n')
dbg = logging.getLogger('dbg')
dbg.propagate = False
dbg.setLevel(logging.DEBUG)
f_dbg_log = os.path.join(log_dir,user + '_dbg.log')
fh_dbg = logging.handlers.RotatingFileHandler(f_dbg_log)
fh_dbg.setLevel('DEBUG')
fh_dbg.setFormatter(dbg_format)
dbg.addHandler(fh_dbg)
#_______________________________________________________________________
# PROGRAM CONTROL
#_______________________________________________________________________
dbg.info("sess:" + sess)
curr_env, err, rc = tm.tmx('show-environment')
#tm.sendk(sess + ':0.0', 'tmux show-environment')
#---------------------------------------
db.create_pm_db()
#d_hosts = {'pi1':'pi', 'pi2':'pi', 'pi3':'pi'}
#tm.multi_rlogin(d_hosts)
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# EOF
