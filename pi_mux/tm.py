#!/usr/bin/python2
#=======================================================================
import collections
import logging
import os
import re
import shlex
import subprocess
import sys
import tempfile
log = logging.getLogger(__name__)
dbg = logging.getLogger('dbg.' + __name__)
#=======================================================================
def sendk(targ, cmd):
    run = 'tmux send-keys -t ' + targ + ' "' + cmd + '" C-m'
    dbg.info('run:' + run)
    try:
        os.system(run)
        return(1)
    except OSError as e:
        #log.warn("{0}".format(e.strerror))
        dbg.warn("{0}".format(e.strerror))
        dbg.error("{1}ec:{0}".format(e.errno, e.strerror))
        return(0)
# END def sendk
#-----------------------------------------------------------------------
def get_windows():
    cmd = 'tmux list-windows'
    # This regex can be modified later to obtain window size, etc.
    r_win_line = re.compile(r'(\d+):\s+(\w+).*\s+.*(\d+)\s+panes.*')
    l_cmd = shlex.split(cmd)
    p = subprocess.Popen(l_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    p_out = p.communicate()[0]
    dbg.info('p_out:' + p_out)
    p_rc = p.returncode
    d_win = {}
    for line in p_out.split('\n'):
        dbg.info('line:' + line)
        m = r_win_line.match(line)
        if m:
            id = m.group(1)
            d_win[id] = {}
            d_win[id]['id'] = id
            d_win[id]['name'] = m.group(2)
            d_win[id]['num_panes'] = m.group(3)
            d_win[id]['line'] = line
            if re.match( r'.*\(active\)', line):
                d_win[id]['active'] = True
            else:
                d_win[id]['active'] = False

    return(d_win)
# END get_windows
#-----------------------------------------------------------------------
def tmx(cmd):
    sess = os.environ['PM_SESS']
    run = 'tmux ' + cmd
    dbg.info('run:' + run)
    try:
        os.system(run)
        return(1)
    except OSError as e:
        #log.warn("{0}".format(e.strerror))
        dbg.warn("{0}".format(e.strerror))
        dbg.error("{1}ec:{0}".format(e.errno, e.strerror))
        return(0)
    except:
        #log.critical('UNEXPECTED ERROR\n', sys.exc()[0])
        dbg.critical('UNEXPECTED ERROR\n', sys.exc()[0])
        my_exit(101)
# END def tmx
#-----------------------------------------------------------------------
def get_win_list():
    d_win = collections.OrderedDict()
    !!! change the output with -F option
    re_name_panes_size = re.compile(r'^.*\((\d+)a(.+) panes\) \[(\d{2,3})x(\d+)]')
    raw_win_list = tmx("list-windows -a -t " + sess)
    for entry in raw_win_list:
        sess_id, win_num, win_name_panes_size = entry.split(':')
        for elem in win_attr_list:

#-----------------------------------------------------------------------
def console(targ=None, user=None):
    curr_user = os.environ['USER']
    # !!! Check targ validity
    if targ is None or targ == '':
        targ = raw_input('Enter hostname(default:localhost): ')
        if targ is None or targ == '':
            targ = os.environ['HOSTNAME']

        login_cmd = ''
    if user is None or user == '':
        user = raw_input('Enter username (default:' + curr_user + '): ')
        if user is None or user == '':
            user = curr_user

    login_cmd = '/usr/bin/ssh -tCX -o StrictHostKeyChecking=no '
    login_cmd += '-l ' + user + ' ' + targ

    dbg.debug("login_cmd:" + login_cmd)
    sess = os.environ['PM_SESS']
    dbg.debug("sess:" + sess)
    win = targ.split('.')[0]
    dbg.debug("win:" + win)
    pane = win + '.0'
    dbg.debug("pane:" + pane)
#    tmx('set-hook -t ' + sess + ' pane-died "select-window -t ' + sess + ':top"')
    tmx('new-window -t ' + sess + ' -d -n ' + win)
#    tmx('setw -t ' + win + ' remain-on-exit')
    tmx('select-window -t ' + win)
    sendk(pane, login_cmd + ' ; tmux wait-for -S ' + targ + '_done')
    tmx('wait-for ' + targ + '_done ; tmux capture-pane -S - -E -')
#    tmx('wait-for cmd_done')
    f_hist = os.environ['PM_HIST_FILE']
    if os.path.exists(f_hist):
        dbg.debug("tmx('save-buffer -a ' + " + f_hist + ")")
        tmx('save-buffer -a ' + f_hist)
    else:
        dbg.debug("tmx('save-buffer ' + " + f_hist + ")")
        tmx('save-buffer ' + f_hist)

#    tmx('clear-history')
    sendk(pane,'exit')
    tmx("select-window -t " + sess + ":top")
#    tmx('set -gu remain-on-exit')
# END def console
#-----------------------------------------------------------------------
def disp(msg):
    dbg.info('msg:' + msg)
    f_tmp = tempfile.NamedTemporaryFile(mode='w+t')
    f_tmp.write(msg)
    f_tmp.seek(0)
    f_name = f_tmp.name
    tmx('new-window -d -n disp')
    tmx('select-window -t disp')
    disp_pane = 'disp.0'
    sendk(disp_pane, 'less ' + f_name + ' ; tmux wait-for -S cmd_done')
    tmx('wait-for cmd_done')
    f_tmp.close()
    tmx('kill-window -t disp')
# END def disp
