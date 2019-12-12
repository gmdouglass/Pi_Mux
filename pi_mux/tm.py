#!/usr/bin/python3
#_______________________________________________________________________
import os
import sys
import collections
import re
import shlex
import stat
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
#_______________________________________________________________________
# DEFS
#_______________________________________________________________________
def sendk(targ, cmd=None):
    dbg.info("START def sendk(targ, cmd=None):")
    # This block allows targ to be missing without having to refactor
    # a bunch of previously written code to swap parameter positions.
    if cmd is None:
        run = 'tmux send-keys "' + targ + '" C-m'
    else:
        run = 'tmux send-keys -t ' + targ + ' "' + cmd + '" C-m'

    dbg.info('run:' + run)
    try:
        os.system(run)
        dbg.info("END def sendk(targ, cmd=None):return(1)")
        return(1)
    except OSError as e:
        #log.warn("{0}".format(e.strerror))
        dbg.warn("{0}".format(e.strerror))
        dbg.error("{1}ec:{0}".format(e.errno, e.strerror))
        dbg.info("END def sendk(targ, cmd=None):return(0)")
        return(0)
#-----------------------------------------------------------------------
def choose_pane(d_panes):
    dbg.info("START def choose_pane(d_panes):")
    dbg.info("d_panes:" + str(d_panes))
    '''
    d_panes[pane_id] = {}
    d_panes[pane_id]['title'] = pane_title
    '''
    idx = 1
    od_menu_entries = collections.OrderedDict()
    for pane_id in d_panes:
        od_menu_entries[str(idx)] = d_panes[pane_id]['title']
        idx += 1

    d_menu = {}
    d_menu['title'] = 'Choose Pane'
    d_menu['entries'] = od_menu_entries
    d_menu['prompt'] = "Choose a pane: "
    done = False
    while not done:
        l_choices = util.menu(d_menu)
        if len(l_choices) > 1:
            print("Only one choice is allowed.")
            raw_input("Choose again.")
            continue
        else:
            done = True

    menu_choice = l_choices[0]
    title = od_menu_entries[menu_choice]
    for pane_id in d_panes.keys():
        if title == d_panes[pane_id]['title']:
            dbg.info("END def choose_pane(d_panes):return(pane_id)")
            return(pane_id)
#-----------------------------------------------------------------------
def capture_pane(pane_id, f_pane_capture=None):
    dbg.info("START def capture_pane(pane_id, f_pane_capture=None)")
    dbg.info("pane_id:" + pane_id)
    f_in = ''
    if f_pane_capture is None:
        f_pane_capture = os.path.join(os.environ['HOME'], pane_id
                                      + '.out')
        dbg.info("f_pane_capture:" + f_pane_capture)
        prompt = "Enter filename for pane capture (default:"
        prompt += f_pane_capture + "): "
        f_in = input(prompt)
        if f_in != '':
            f_pane_capture = f_in

    win_id, pane_num = pane_id.split('.')
    tmx('select-window -t ' + win_id)
    tmx('select-pane -t ' + pane_id + '\; capture-pane -S - -E -')
    dbg.info("tmx('last-window')")
    tmx('last-window')
    if f_pane_capture is None:
        f_pane_capture = os.path.join(os.environ['HOME'], pane_id
                                      + '.out')

    if os.path.exists(f_pane_capture):
        dbg.debug("tmx('save-buffer -a ' + " + f_pane_capture + ")")
        tmx('save-buffer -a ' + f_pane_capture)
    else:
        dbg.debug("tmx('save-buffer ' + " + f_pane_capture + ")")
        tmx('save-buffer ' + f_pane_capture)

        msg = "END def capture_pane(pane_id, f_pane_capture=None):"
        msg += "return(f_pane_capture)"
        dbg.info(msg)
    return(f_pane_capture)
#-----------------------------------------------------------------------
def edit_pane_cap(f_cap):
    dbg.info("START def edit_pane_cap(f_cap):")
    dbg.info("f_cap:" + f_cap)
    try:
        dbg.info("editor = os.environ['EDITOR']")
        editor = os.environ['EDITOR']
        dbg.info("editor:" + editor)
    except KeyError:
        dbg.info("editor = '/usr/local/bin/vim'")
        editor = '/usr/local/bin/vim'
        dbg.info("editor:" + editor)

    win_name = get_win_name('EDIT_CAPTURE')
    win_id = sess + ':' + win_name
    edit_pane = sess + ':' + win_name + '.0'
    tmx('new-window -d -t ' + sess + ' -n ' + win_name)
#    tmx('setw -t ' + win_id + ' status off')
    dbg.info("tmx('setw -t + ' win_id + ' remain-on-exit off')")
    tmx('setw -t ' + win_id + ' remain-on-exit off')
    sendk(edit_pane, 'reset')
    tmx('select-window -t ' + win_id)
    sendk(edit_pane, editor + ' ' + f_cap + '; tmux wait-for -S edit_done')
    tmx('wait-for edit_done')
    sendk(edit_pane, 'exit')
    #---------------------------------------
    dbg.info("END def edit_pane_cap(f_cap):")
#-----------------------------------------------------------------------
def get_windows():
    dbg.info("START def get_windows():")
    cmd = 'tmux list-windows'
    # This regex could be modified later to obtain window size, etc.
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

    dbg.info("END def get_windows():return(d_win)")
    return(d_win)
#-----------------------------------------------------------------------
def tmx(cmd):
    dbg.info("START def tmx(cmd):")
    run = 'tmux ' + cmd
    dbg.info('run:' + run)
    try:
        out, err, rc = util.cmd(run)
        dbg.info("END def tmx(cmd):return(out, err ,rc)")
        return(out, err ,rc)
    except OSError as e:
        #log.warn("{0}".format(e.strerror))
        dbg.warn("{0}".format(e.strerror))
        dbg.error("{1}ec:{0}".format(e.errno, e.strerror))
        dbg.info("END def tmx(cmd):exit(101)")
        exit(101)
    except:
        #log.critical('UNEXPECTED ERROR\n', sys.exc()[0])
        dbg.critical('UNEXPECTED ERROR\n', sys.exc()[0])
        dbg.info("END def tmx(cmd):exit(101)")
        exit(101)
#-----------------------------------------------------------------------
def get_win_name(new_name):
    dbg.info("START def get_win_name(new_name):")
    dbg.info("new_name:" + new_name)
    re_win_names = re.compile('r' + new_name + '_(\d+)')
    d_win = collections.OrderedDict()
    l_win_names, err, rc = tmx("list-windows -a -F '#{window_name}'")
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

    dbg.info("END def get_win_name(new_name):return(new_name)")
    return(new_name)
#-----------------------------------------------------------------------
def single_rlogin(host, user):
    dbg.info("START def single_rlogin(host, user):")
    win_name = get_win_name(host)
    win_id = sess + ':' + win_name
    tmx('new-window -t ' + sess + ' -d -n ' + win_name)
    pane_num = 0
    pane_id = win_id + '.' + str(pane_num)
    tmx('select-pane -t ' + pane_id)
    set_status(win_id,'single')
    rlogin(host, user, pane_id)
    time.sleep(0.05)
    sendk(pane_id, 'clear')
    dbg.info("END def single_rlogin(host, user):")
#-----------------------------------------------------------------------
def multi_rlogin(d_hosts):
    dbg.info("START def multi_rlogin(d_hosts):")
    win_name = get_win_name('multi_rlogin')
    win_id = sess + ':' + win_name
    tmx('new-window -t ' + sess + ' -d -n ' + win_name)
    num_splits = len(d_hosts)
    dbg.info("num_splits:" + str(num_splits))
    for pane in range(1, num_splits):
        tmx('split-window -t ' + sess + ':' + win_name)

    pane_num = 0
    pane_id = win_id + '.' + str(pane_num)
    d_panes = {}
    threads = []
    for host, user in d_hosts.items():
        tmx('select-pane -t ' + pane_id)
        d_panes[pane_id] = {}
        d_panes[pane_id]['title'] = host
        t = threading.Thread(target=rlogin, args=(host, user, pane_id))
        threads.append(t)
        t.start()
        time.sleep(0.05)
        sendk(pane_id, 'clear')
        pane_num += 1
        pane_id = win_id + '.' + str(pane_num)
        tmx('select-pane -t ' + win_id + '.0')

    '''
    FROM THE MAN PAGE
    tmux also supports user options which are prefixed with a ‘@’.
    User options may have any name, so long as they are prefixed
    with ‘@’, and be set to any string.
    For example:
       $ tmux setw -q @foo "abc123"
                  $ tmux showw -v @foo
                             abc12
    '''
    set_status(win_id, d_panes, 'multi')
    dbg.info("END def multi_rlogin(d_hosts):")
#-----------------------------------------------------------------------
def set_status(win_id, d_panes=None, spec=None):
    dbg.info("START def set_status(win_id, spec=None):")
    dbg.info("spec:" + spec)
#    tmx('unbind-key -n F1')
#    tmx('unbind-key -n F2')
#    tmx('bind-key -n F1 new-window HELP help.sh')
#    tmx('bind-key -n F2 kill-session -t ' + sess)
    tmx('unbind-key -n F3')
    tmx('unbind-key -n F4')
    tmx('unbind-key -n F5')
    if spec == 'multi':
        tmx('setw -t ' + win_id + ' -q @d_panes "' + str(d_panes) + '"')
        tmx('bind-key -n F3 new-window -t ' + sess + ' -n CHOOSE_PANE choose_pane.py \"' + str(d_panes) + '\"')
        tmx('bind-key -n F4 new-window -t ' + sess + ' -n CAPTURE_PANE capture_pane.py \"' + str(d_panes) + '\"')
        tmx('bind-key -n F5 new-window -n LOGS view_logs.sh')
        dbg.info("lstat_str = 'F1-Help F2-Exit F3-Choose Host F4-Save Pane F5-view Logs'")
        lstat_str = 'F1-Help F2-Exit F3-Choose Host F4-Save Pane F5-view Logs'
        width = len(lstat_str)
        tmx('setw -a -t ' + win_id + ' status-left-length ' + str(width))
        tmx('setw -t ' + win_id + ' status-left \"' + lstat_str + '\"')
    elif spec == 'single':
        tmx('bind-key -n F3 new-window -t ' + sess
            + ' -n CAPTURE_PANE capture_pane.py \"' + str(d_panes) + '\"')
        if debug_flag:
            tmx('bind-key -n F5 new-window -n LOGS view_logs.sh')
            lstat_str = 'F1-Help F2-Exit F3-Choose Host F4-Save Pane F5-View Logs'
        else:
            lstat_str = 'F1-Help F2-Exit F3-Choose Host F4-Save Pane'

        llen = len(lstat_str)
        tmx('setw -t ' + win_id + ' status-left-length ' + str(llen))
        # !!! look into force-width
        tmx('setw -t ' + win_id + ' status-left \"' + lstat_str + '\"')
    else:
        lstat_str = 'F1-Help F2-Exit'
        llen = len(lstat_str)
        tmx("setw -t " + win_id + " status-left-length " + llen)
        tmx("setw -t " + win_id + " status-left-style bg=blue,fg=white,bold")
        tmx("setw -t " + win_id + " status-left \" + lstat_str + '\"")
    #---------------------------------------
    dbg.info("END def set_status(win_id, spec=None):")
#-----------------------------------------------------------------------
def rlogin(host, user, pane_id):
    dbg.info("START def rlogin(host, user, pane_id):")
    dbg.debug("host:" + host)
    dbg.debug("user:" + user)
    dbg.debug("pane_id:" + pane_id)
    login_cmd = '/usr/bin/ssh -tCX -o StrictHostKeyChecking=no '
    login_cmd += '-l ' + user + ' ' + host
    dbg.debug("login_cmd:" + login_cmd)
    tmx('select-pane -t ' + pane_id)
    sendk(pane_id, login_cmd + '; tmux wait-for -S ' + host + '_done')
    tmx('wait-for ' + host + '_done \; capture-pane -S - -E -')
    f_buff = os.path.join(os.environ['PM_HIST_DIR'], host + '_'
                          + sess + '.hist')
    if os.path.exists(f_buff):
        dbg.debug("tmx('save-buffer -a ' + " + f_buff + ")")
        tmx('save-buffer -a ' + f_buff)
    else:
        dbg.debug("tmx('save-buffer ' + " + f_buff + ")")
        tmx('save-buffer ' + f_buff)

    sendk('exit')
    win_id, pane_num = pane_id.split('.')
    tmx('select-pane -t ' + win_id + '.0')
    dbg.info("END def rlogin(host, user, pane_id):")
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
    f_buff = os.path.join(os.environ['PM_HIST_DIR'], host + '_'
                          + sess + '.hist')
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
    dbg.info("START def disp(msg):")
    msg = str(msg)
    dbg.info('msg:' + msg)
    f_tmp = tempfile.NamedTemporaryFile(mode='w+t')
    f_tmp.write(msg)
    f_tmp.seek(0)
    f_name = f_tmp.name
    win_name = get_win_name('disp')
    tmx('new-window -d -n ' + win_name)
#    tmx('setw -t ' + sess + ':' + win_name + ' status off')
    tmx('select-window -t ' + win_name)
    disp_pane = 'disp.0'
    sendk(disp_pane, 'less ' + f_name + ' ; tmux wait-for -S cmd_done')
    tmx('wait-for cmd_done')
    f_tmp.close()
    tmx('kill-window -t ' + win_name)
    dbg.info("END def disp(msg):")
#-----------------------------------------------------------------------
#_______________________________________________________________________
# END DEFS
#_______________________________________________________________________
try:
    sess = os.environ['PM_SESS']
except:
    err_msg = "The 'PM_SESS' environment variable has not "
    err_msg += "been initialized."
    log.critical(err_msg)
    dbg.critical(err_msg)
    print(err_msg)
    input('Press any key to continue.')
    exit(101)

debug_flag = os.environ['PM_DEBUG']
user = os.environ['USER']
