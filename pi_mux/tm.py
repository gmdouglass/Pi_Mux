#!/usr/bin/python3
#=======================================================================
import os
import sys
import collections
import re
import shlex
import subprocess
import tempfile
import threading
import time
import logging
log = logging.getLogger(__name__)
dbg = logging.getLogger('dbg.' + __name__)
#-----------------------------------------------------------------------
sys.path.insert(1, os.environ['PM_DIR'])
import util
#=======================================================================
def sendk(targ, cmd=None):
    # This block allows targ to be missing without having to refactor
    # a bunch of previously written code to swap parameter positions.
    if cmd is None:
        run = 'tmux send-keys "' + targ + '" C-m'
    else:
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
def capture_pane(pane_id):
    tmx('select-pane -t ' + pane_id)
    tmx('capture-pane -S - -E -')
    f_pane = os.path.join(os.environ['PM_HIST_DIR'], pane_id + '.hist')
    f_in = ''
    prompt = "Enter filename for pane capture (default:" + f_pane + "): "
    f_in = input(prompt)
    if f_in != '':
        f_pane = f_in

    if os.path.exists(f_pane):
        dbg.debug("tmx('save-buffer -a ' + " + f_pane + ")")
        tmx('save-buffer -a ' + f_pane)
    else:
        dbg.debug("tmx('save-buffer ' + " + f_pane + ")")
        tmx('save-buffer ' + f_pane)

# END def capture_pane(pane_id)
#-----------------------------------------------------------------------
def choose_pane(d_panes):
    '''
    d_panes[pane_id] = {}
    d_panes[pane_id]['sess'] = sess
    d_panes[pane_id]['win'] = win_id
    d_panes[pane_id]['pane_num'] = pane_num
    d_panes[pane_id]['name'] = host
    '''
    d_names = collections.OrderedDict()
    for pane in d_panes:
        d_names[pane] = d_panes[pane]['name']


# END def choose_pane(d_panes)
#-----------------------------------------------------------------------
def get_windows():
    cmd = 'tmux list-windows'
    # This regex can be modified later to obtain window size, etc.
    r_win_line = re.compile(r'(\d+):\s+(\w+).*\s+.*(\d+)\s+panes.*')
    l_cmd = shlex.split(cmd)
    p = subprocess.Popen(l_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    p_out = p.communicate()[0]
    p_out = p_out.decode('utf-8')
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
    run = 'tmux ' + cmd
    dbg.info('run:' + run)
    try:
        out, err, rc = util.cmd(run)
        return(out, err ,rc)
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
def get_win_name(new_name):
    dbg.info("new_name:" + new_name)
    re_win_names = re.compile('r' + new_name + '_(\d+)')
    d_win = collections.OrderedDict()
    #l_win_names = tmx("list-windows -t " + sess + " -F '#{window_name}' -a")
    l_win_names, err, rc = tmx("list-windows -a -F '#{window_name}'")
#    dbg.info("l_win_names:" + str(l_win_names))
#    disp(str(l_win_names))
    l_win_nums = []
    name_match = False
    for name in l_win_names:
        m = re_win_names.search(name)
        if m:
            name_match = True
            l_win_nums.append(int(m.group(1)))

    if name_match:
        last_num = max(l_win_nums)
        new_name = new_name + '_' + str(last_num + 1)

    return(new_name)
# def get_win_name(new_name)
#-----------------------------------------------------------------------
def single_rlogin(host, user):
    win_name = get_win_name(host)
    win_id = sess + ':' + win_name
    tmx('new-window -t ' + sess + ' -d -n ' + win_name)
    pane_num = 0
    pane_id = win_id + '.' + str(pane_num)
    tmx('select-pane -t ' + pane_id)
    rlogin(host, user, pane_id)
    time.sleep(0.05)
    sendk(pane_id, 'clear')
# END def single_rlogin()
#-----------------------------------------------------------------------
def multi_rlogin(d_hosts):
    win_name = get_win_name('multi_rlogin')
    win_id = sess + ':' + win_name
    tmx('new-window -t ' + sess + ' -d -n ' + win_name)
    num_splits = len(d_hosts)
    dbg.info("num_splits:" + str(num_splits))
    for pane in range(1, num_splits):
        tmx('split-window -t ' + sess + ':' + win_name)

    pane_num = 0
    pane_id = win_id + '.' + str(pane_num)
    threads = []
    for host, user in d_hosts.items():
        tmx('select-pane -t ' + pane_id)
        d_panes[pane_id] = {}
        d_panes[pane_id]['sess'] = sess
        d_panes[pane_id]['win'] = win_id
        d_panes[pane_id]['pane_num'] = pane_num
        d_panes[pane_id]['name'] = host
        t = threading.Thread(target=rlogin, args=(host, user, pane_id))
        threads.append(t)
        t.start()
        time.sleep(0.05)
        sendk(pane_id, 'clear')
        pane_num += 1
        pane_id = win_id + '.' + str(pane_num)
        tmx('select-pane -t ' + win_id + '.0')

    tmx('resize-pane -Z')
# END def multi_rlogin()
#-----------------------------------------------------------------------
def rlogin(host, user, pane_id):
    dbg.debug("host:" + host)
    dbg.debug("user:" + user)
    dbg.debug("pane_id:" + pane_id)
    login_cmd = '/usr/bin/ssh -tCX -o StrictHostKeyChecking=no '
    login_cmd += '-l ' + user + ' ' + host
    dbg.debug("login_cmd:" + login_cmd)
    tmx('select-pane -t ' + pane_id)
    sendk(pane_id, login_cmd + '; tmux wait-for -S ' + host + '_done')
    tmx('wait-for ' + host + '_done \; capture-pane -S - -E -')
    f_buff = os.path.join(os.environ['PM_HIST_DIR'], host + '_' + sess + '.hist')
    if os.path.exists(f_buff):
        dbg.debug("tmx('save-buffer -a ' + " + f_buff + ")")
        tmx('save-buffer -a ' + f_buff)
    else:
        dbg.debug("tmx('save-buffer ' + " + f_buff + ")")
        tmx('save-buffer ' + f_buff)

    sendk('exit')
    win_id, pane_num = pane_id.split('.')
    tmx('select-pane -t ' + win_id + '.0')
    tmx('resize-pane -Z')
# END def rlogin(host, user, pane_id)
#-----------------------------------------------------------------------
def console():
    targ = os.environ['HOSTNAME']
    win = targ.split('.')[0]
    dbg.debug("win:" + win)
    pane = win + '.0'
    dbg.debug("pane:" + pane)
    tmx('new-window -t ' + sess + ' -d -n ' + win)
#    tmx('setw -t ' + win + ' remain-on-exit')
    tmx('select-window -t ' + win)
    sendk(pane, login_cmd + ' ; tmux wait-for -S ' + targ + '_done')
    tmx('wait-for ' + targ + '_done ; tmux capture-pane -S - -E -')
    f_buff = os.path.join(os.environ['PM_HIST_DIR'], host + '_' + sess + '.hist')
    if os.path.exists(f_buff):
        dbg.debug("tmx('save-buffer -a ' + " + f_buff + ")")
        tmx('save-buffer -a ' + f_buff)
    else:
        dbg.debug("tmx('save-buffer ' + " + f_buff + ")")
        tmx('save-buffer ' + f_buff)

    sendk(pane,'exit')
# END def console
#-----------------------------------------------------------------------
def disp(msg):
    msg = str(msg)
    dbg.info('msg:' + msg)
    f_tmp = tempfile.NamedTemporaryFile(mode='w+t')
    f_tmp.write(msg)
    f_tmp.seek(0)
    f_name = f_tmp.name
    win_name = get_win_name('disp')
    tmx('new-window -d -n ' + win_name)
    tmx('select-window -t ' + win_name)
    disp_pane = 'disp.0'
    sendk(disp_pane, 'less ' + f_name + ' ; tmux wait-for -S cmd_done')
    tmx('wait-for cmd_done')
    f_tmp.close()
    tmx('kill-window -t ' + win_name)
# END def disp
#-----------------------------------------------------------------------
sess = os.environ['CURR_TM_SESS']
user = os.environ['USER']
# This dict is used to hold names for panes.
d_panes = {}
'''
EXAMPLE
d_panes[pane_id]['sess'] = sess
d_panes[pane_id]['win'] = win_id
d_panes[pane_id]['pane_num'] = pane_num
d_panes[pane_id]['name'] = pane_name
'''
