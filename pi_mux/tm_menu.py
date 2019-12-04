#!/usr/bin/python3
########################################################################
import collections
import os
import re
import shlex
import subprocess
import tempfile
#---------------------------------------
import sys
sys.path.insert(1, os.environ['PM_DIR'])
import tm
import util
#---------------------------------------
import logging
log = logging.getLogger(__name__)
dbg = logging.getLogger('dbg.' + __name__)
########################################################################
#=======================================================================
########################################################################
sess = os.environ['CURR_TM_SESS']
cmd = 'tmux list-panes -a'
out, err, rc = util.sh(cmd)
'''
if out is None and err is None:
    tm.disp('OUT:None\n' + 'ERR:None\n' + 'RC:' + str(rc))
elif out is None:
    tm.disp('OUT:None\n' + 'ERR:\n' + err + '\n' + 'RC:' + str(rc))
elif err is None:
    tm.disp('OUT:\n' + out + '\n' + 'ERR:None\n' + 'RC:' + str(rc))
else:
    tm.disp('OUT:\n' + out + '\n' + 'ERR:\n' + err + '\n' + 'RC:' + str(rc))
'''
