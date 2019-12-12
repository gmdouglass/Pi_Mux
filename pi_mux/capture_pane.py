#!/usr/bin/python3
import ast
import os
import re
import sys
#-----------------------------------------------------------------------
try:
    sess = os.environ['PM_SESS']
except KeyError:
    err_msg = "'PM_SESS' env var not set!"
    print(err_msg)

top_dir = os.environ['PM_DIR']
sys.path.insert(1, top_dir)
import tm
#---------------------------------------
log_dir = os.environ['PM_LOG_DIR']
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
f_app_log = os.path.join(log_dir, user + '_capture_pane.log')
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
f_dbg_log = os.path.join(log_dir,user + '_capture_pane_dbg.log')
fh_dbg = logging.handlers.RotatingFileHandler(f_dbg_log)
fh_dbg.setLevel('DEBUG')
fh_dbg.setFormatter(dbg_format)
dbg.addHandler(fh_dbg)
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
    dbg.info("d_panes = ast.literal_eval(sys.argv[1])")
    d_panes = ast.literal_eval(sys.argv[1])
else:
    dbg.info("d_panes = ast.literal_eval(sys.argv[1])")
    d_panes = ast.literal_eval(sys.argv[1])

#a_pane_id = d_panes.keys()[0]
for pane_id in d_panes:
    a_pane_id = pane_id
    break

dbg.info("a_pane_id:" + a_pane_id)
win_id, pnum = a_pane_id.split('.')
panes, err, rc = tm.tmx('list-panes -t ' + win_id)
dbg.info("panes:" + panes)
pane_lines = panes.split('\n')
dbg.info("pane_lines:" + str(pane_lines))
re_active = re.compile(r'(\d{1,2}).*active')
for line in pane_lines:
    dbg.info("line:" + line)
    m = re_active.search(line)
    if m:
        active_pane_num = m.group(1)
        dbg.info("active_pane_num:" + active_pane_num)
        break

for pane_id in d_panes:
    dbg.info("pane_id:" + pane_id)
    win_id, pane_num = pane_id.split('.')
    if pane_num == active_pane_num:
        active_pane_id = pane_id
        dbg.info("active_pane_id:" + active_pane_id)
        break

dbg.info("f_pane_capture = tm.capture_pane(pane_id)")
f_pane_capture = tm.capture_pane(active_pane_id)
dbg.info("f_pane_capture:" + f_pane_capture)
dbg.info("tm.edit_pane_cap(f_pane_capture)")
tm.edit_pane_cap(f_pane_capture)

