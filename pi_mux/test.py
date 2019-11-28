#!/usr/bin/python2
#-----------------------------------------------------------------------
import logging
import logging.handlers
import os
import sys
#---------------------------------------
sys.path.insert(1, os.environ['PM_DIR'])
import tm
import util
#---------------------------------------
#calling_script = os.path.splitext(os.path.basename(__main__.__file__))[0]
user = os.environ['USER']
#---------------------------------------
# Initialize paths.
top_dir = os.environ['PM_DIR']
log_dir = os.environ['LOG_DIR]'
hist_dir = os.environ['PM_HIST_DIR']
data_dir = os.environ['PM_DATA_DIR']
tmp_dir = os.environ['TMP_DIR']
#---------------------------------------
# LOGGING CONFIG
#---------------------------------------
# application log file
test_log_format = logging.Formatter('[%(asctime)s]-[%(levelname)-8s]-[%(filename)s]-[line %(lineno)s] %(message)s')
test = logging.getLogger('test')
test.setLevel(logging.INFO)
f_test_log = log_dir + '/test.log'
fh_test_log = logging.handlers.RotatingFileHandler(f_test_log)
fh_test_log.setLevel('INFO')
fh_test_log.setFormatter(test_log_format)
test.addHandler(fh_test_log)
#---------------------------------------
# Application console logging
test_con_format = logging.Formatter('%(filename)s:%(levelname)-8s:%(message)s')
test_ch = logging.StreamHandler()
#ch.setLevel('WARN')
test_ch.setFormatter(test_con_format)
test.addHandler(test_ch)
#---------------------------------------
# debug log file
dbg_format = logging.Formatter('[%(asctime)s]-[%(filename)s]-[line %(lineno)4s] %(message)s')
dbg = logging.getLogger('dbg')
dbg.setLevel(logging.DEBUG)
f_dbg_log = log_dir + '/test_dbg.log'
fh_dbg = logging.handlers.RotatingFileHandler(f_dbg_log)
fh_dbg.setLevel('DEBUG')
fh_dbg.setFormatter(dbg_format)
dbg.addHandler(fh_dbg)
