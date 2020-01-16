#!/usr/bin/python3
import ast
import os
import sys
import logging
import logging.handlers
#---------------------------------------
try:
    top_dir = os.environ['PM_DIR']
    sys.path.insert(1, top_dir)
except KeyError:
    err_msg = "'PM_DIR' env var not set!"
    print(err_msg)
    exit(101)

import gvar
import tm
#---------------------------------------
# LOGGING CONFIG
#---------------------------------------
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

f_app_log = os.path.join(gvar.log_dir, user + 'choose_pane.log')
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
#========================================================================
d_panes = {}
num_args = len(sys.argv)
if num_args < 2:
    err_msg = "missing argument"
    log.critical(err_msg)
    exit(101)
elif num_args > 2:
    err_msg = "too many arguments, extra arguments ignored"
    log.error(err_msg)
    log.info("d_panes = ast.literal_eval(sys.argv[1])")
    d_panes = ast.literal_eval(sys.argv[1])
else:
    log.info("d_panes = ast.literal_eval(sys.argv[1])")
    d_panes = ast.literal_eval(sys.argv[1])

for pane_id in d_panes:
    log.info("pane_id:" + pane_id)
    host = d_panes[pane_id]['title']
    log.info("host:" + host)

log.info("pane_id = tm.choose_pane(d_panes)")
pane_id = tm.choose_pane(d_panes)
log.info("pane_id:" + pane_id)
log.info("tm.tmx('select-pane -t ' + pane_id)")
tm.tmx('select-pane -t ' + pane_id)
