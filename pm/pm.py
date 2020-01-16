#!/usr/bin/python3
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import os
import sys
import logging
import logging.handlers
#---------------------------------------
# Application specific
try:
    top_dir = os.environ['PM_DIR']
except KeyError:
    err_msg = "The 'PM_DIR' environment variable is not set!"
    print(err_msg)
    exit(101)

sys.path.insert(1, top_dir)
import gvar
import db
import tm
#_______________________________________________________________________
# LOGGING CONFIG
#_______________________________________________________________________
user = os.environ['USER']
# application log file
if gvar.debug:
    app_log_format = logging.Formatter('%(asctime)s [%(levelname)-8s] %(threadName)s:%(filename)s:line %(lineno)4s\n%(message)s\n')
else:
    app_log_format = logging.Formatter('%(asctime)s [%(levelname)-8s] %(threadName)s:%(filename)s\n%(message)s\n')

log = logging.getLogger()
if gvar.debug:
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.WARN)

f_app_log = os.path.join(gvar.log_dir, user + '.log')
fh_app_log = logging.handlers.RotatingFileHandler(f_app_log)
if gvar.debug:
    fh_app_log.setLevel('DEBUG')
else:
    fh_app_log.setLevel('WARN')

fh_app_log.setFormatter(app_log_format)
log.addHandler(fh_app_log)
#---------------------------------------
# Application console logging
app_con_format = logging.Formatter('%(filename)s:%(levelname)-8s:%(message)s')
app_ch = logging.StreamHandler()
app_ch.setLevel('WARN')
app_ch.setFormatter(app_con_format)
log.addHandler(app_ch)
#_______________________________________________________________________
# PROGRAM CONTROL
#_______________________________________________________________________
log.debug("gvar.sess:" + gvar.sess)
curr_env, err, rc = tm.tmx('show-environment')
#tm.sendk(gvar.sess + ':0.0', 'tmux show-environment')
#---------------------------------------
#db.create_pm_db()
d_hosts = {'pi1':'pi', 'pi2':'pi', 'pi3':'pi'}
#d_hosts = {'pi2':'pi', 'pi3':'pi'}
tm.multi_rlogin(d_hosts)
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# EOF
