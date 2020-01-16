#!/usr/bin/python3
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
import os
import sys
#---------------------------------------
# Application specific
try:
    top_dir = os.environ['PM_DIR']
except KeyError:
    err_msg = "The 'PM_DIR' env variable is not set!"
    print(err_msg)
    exit(101)

sess = os.environ['PM_SESS']
debug = os.environ['PM_DEBUG']
log_dir = os.environ['PM_LOG_DIR']
tmp_dir = os.environ['PM_TMP_DIR']
data_dir = os.environ['PM_DATA_DIR']
db_dir = os.path.join(data_dir, 'db')
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# EOF
