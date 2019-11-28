#!/usr/bin/python2
#-----------------------------------------------------------------------
import logging
import logging.handlers
import os
import sys
import threading
import time
#---------------------------------------
sys.path.insert(1, os.environ['PM_DIR'])
import tm
import util
#---------------------------------------
user = os.environ['USER']
#---------------------------------------
# Initialize paths.
log_dir = os.environ['LOG_DIR']
hist_dir = os.environ['PM_HIST_DIR']
data_dir = os.environ['PM_DATA_DIR']
tmp_dir = os.environ['TMP_DIR']
#---------------------------------------
# LOGGING CONFIG
#---------------------------------------
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
sess = os.environ['PM_SESS']
threads = []
cmd = "new-window -t " + sess + " -d -n top"
t = threading.Thread(target=tm.tmx, args=([cmd]), name='top')
threads.append(t)
t.start()
hosts = ['pi1', 'pi2', 'pi3']
for i in hosts:
    dbg.info("host:" + i)
    dbg.info('t = threading.Thread(target=tm.console, args=(i, "pi"))')
    t = threading.Thread(target=tm.console, args=(i, "pi"), name=i)
    dbg.info("t:" + str(t))
    dbg.info("threads.append(t)")
    threads.append(t)
    dbg.info("t.start()")
    t.start()
    time.sleep(0.05)
    tm.sendk(sess + ":" + i + ".0", "clear")

tm.tmx("select-window -t " + sess + ":top")

for thread in threading.enumerate():
    dbg.debug("thread started:" + thread.name)

