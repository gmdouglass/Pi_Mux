#!/usr/bin/python3
#-----------------------------------------------------------------------
import threading
import time
#---------------------------------------
import os
import sys
sess = os.environ['CURR_TM_SESS']
sys.path.insert(1, os.environ['PM_DIR'])
import tm
import util
#---------------------------------------
# Initialize paths.
log_dir = os.environ['LOG_DIR']
hist_dir = os.environ['PM_HIST_DIR']
data_dir = os.environ['PM_DATA_DIR']
tmp_dir = os.environ['TMP_DIR']
#---------------------------------------
# LOGGING CONFIG
#---------------------------------------
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
#---------------------------------------
# hist file
'''
hist_format = logging.Formatter('%(message)s')
hist = logging.getLogger('hist')
hist.setLevel(logging.INFO)
f_hist = os.path.join(hist_dir, user + '.hist')
fh_hist = logging.handlers.RotatingFileHandler(f_hist)
fh_hist.setLevel('INFO')
fh_hist.setFormatter(hist_format)
hist.addHandler(fh_hist)
'''
#=======================================================================
d_hosts = {'pi1':'pi', 'pi2':'pi', 'pi3':'pi'}
tm.multi_rlogin(d_hosts)
# EOF
