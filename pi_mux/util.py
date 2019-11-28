#!/usr/bin/python2
#=======================================================================
import logging
import os
import re
import shlex
import subprocess
import sys
import textwrap
import time
log = logging.getLogger(__name__)
dbg = logging.getLogger('dbg.' + __name__)
#=======================================================================
# This causes the 'man' command to display the first man page found
# rather than presenting a list of man pages from all sections from
# which to choose.
os.environ['MAN_POSIXLY_CORRECT'] = '1'
#=======================================================================
def rem_lin_cmd(cmd, targ, user=None):
    if user is None:
        user = os.environ['USER']

    # !!! Check targ validity
    ssh_cmd = '/usr/bin/ssh -tCX -o StrictHostKeyChecking=no ' + user + '@' + targ + ' '
    pre_cmd = 'echo -n \\\"DATE: \\\";date \\\"+\%x \%X \%z\\\";'
    pre_cmd += 'echo -n \\\"HOST: \\\";hostname;'
    pre_cmd += 'echo -n \\\"CMD : \\\"' + cmd + ';echo;echo;'
    cmd = ssh_cmd + pre_cmd + cmd
    dbg.debug('cmd:' + cmd)
    l_cmd = shlex.split(cmd)
    dbg.debug('l_cmd:' + str(l_cmd))
    p = subprocess.Popen(l_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    out = p.communicate()[0]
    dbg.debug('out from p:' + str(out))
    rc = p.returncode
    dbg.debug('rc from p:' + str(rc))
    return(out, rc)
# END def rem_lin_cmd
#-----------------------------------------------------------------------
def loc_lin_cmd(cmd):
    dbg.debug('cmd:' + cmd)
    loc_out = ''
    loc_out = 'LOC DATE: '
    loc_cmd = 'date "+%x %X %z"'
    loc_cmd = shlex.split(loc_cmd)
    loc = subprocess.Popen(loc_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    loc_out += loc.communicate()[0]
    loc_rc = loc.returncode
    #---------------------------------------
    loc_out += 'LOC HOST: ' + os.environ['HOSTNAME']
    #---------------------------------------
    loc_out += '\nCMD     : ' + cmd + '\n'
    loc_out += 'RC      : '
    dbg.debug('cmd:' + cmd)
    if '|' in cmd:
        cmds = cmd.split('|')
        dbg.debug('cmds:' + str(cmds))
        last_idx = len(cmds) - 1
        cmd0 = cmds[0]
        l_cmd0 = shlex.split(cmd0)
        dbg.debug('l_cmd0:' + str(l_cmd0))
        curr_p = subprocess.Popen(l_cmd0, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        prev_p = curr_p
        idx = 0
        for piped_cmd in cmds[1:]:
            dbg.debug('piped_cmd:' + piped_cmd)
            curr_piped_cmd = shlex.split(piped_cmd)
            dbg.debug('curr_piped_cmd:' + str(curr_piped_cmd))
            curr_p = subprocess.Popen(curr_piped_cmd, stdin=prev_p.stdout,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            prev_p.stdout.close()
            prev_p = curr_p

        out = curr_p.communicate()[0]
        rc = curr_p.returncode
    else:
        # Command has no pipe characters
        l_cmd = shlex.split(cmd)
        dbg.debug('l_cmd:' + str(l_cmd))
        p = subprocess.Popen(l_cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        out = p.communicate()[0]
        dbg.debug('out from p:' + str(out))
        rc = p.returncode
        dbg.debug('rc from p:' + str(rc))

    out = loc_out + str(rc) + '\nOUTPUT  :\n' + out
    dbg.debug('out:\n' + out)
    return(out)
# END def loc_lin_cmd
#-----------------------------------------------------------------------
def my_exit(ec=None):
    if ec is None:
        ec = 0
        log.utilinfo('exit code:' + str(ec))
    else:
        log.warn('exit code:' + str(ec))

    clean()
    exit(ec)
# END def my_exit
#-----------------------------------------------------------------------
def clean():
    # !!! Not yet implemented.
    # possibly implement compression of rotated files here.
    pass
# END def clean
#-----------------------------------------------------------------------
def get_time(spec=None):
    if spec is None:
        return(time.localtime())
    elif spec == 'stamp_time':
        return(time.strftime('%H%M%S'))
    elif spec == 'stamp_date':
        return(time.strftime('%Y%m%d'))
    elif spec == 'stamp10':
        return(time.strftime('%y%m%d%H%M'))
    elif spec == 'stamp12':
        return(time.strftime('%y%m%d%H%M%S'))
    elif spec == 'datetime':
        return(time.strftime('%Y.%m.%d %H:%M:%S'))
    elif spec == 'date':
        return(time.strftime('%Y.%m.%d'))
    elif spec == 'time':
        return(time.strftime('%H:%M:%S'))
    else:
        log.critical('bad time specification:' + spec)
        my_exit(101)
# END def get_time
#-----------------------------------------------------------------------
def get_rows_cols():
    return(os.popen('stty size', 'r').read().split())
# END def get_rows_cols
#-----------------------------------------------------------------------
def menu(d_menu):
    '''This function provides a basic console menu framework.

    A single input argument of type 'dict' (d_menu) is expected.
    A list of choices(possibly containg one element) is returned.

    REQUIRED:
    d_menu['title']   - This is the title string.
    d_menu['entries'] - This is an ordered dict containing the menu
                        choices.  The dict keys must be strings.
    d_menu['prompt']  - This is the string displayed for the menu prompt.

    OPTIONAL:
    d_menu['info']    - This is an informational string of text that will
                        be displayed below the title.  It can be multiple
                        lines.
    '''
    #---------------------------------------
    max_width = 120
    done = False
    menu_keys = d_menu.keys()
    while not done:
        print('\n')
        os.system('clear')
        # Format the menu.
        rows, cols = get_rows_cols()
        if int(cols) > max_width:
            cols = max_width

        menu_width = int(cols) - 4
        indent = ' ' * 2
        wrapper = textwrap.TextWrapper(width=menu_width)
        wrapper.initial_indent = indent
        #wrapper.subsequent_indent = indent
        #---------------------------------------
        # Build the menu
        menu_text = ''
        eq_line = indent + ('=' * menu_width) + '\n'
        minus_line = indent + ('-' * menu_width) + '\n'
        menu_text += eq_line
        spec =  '{0:^' + str(menu_width) + '}'
        title = spec.format(d_menu['title'])
        menu_text += title + '\n'
        indent = ' ' * 4
        wrapper.subsequent_indent = indent
        if 'info' in menu_keys and not d_menu['info'] is None:
            menu_text += minus_line
            info_lines = d_menu['info'].splitlines()
            info = ''
            for line in info_lines:
                wrapped_lines = wrapper.wrap(line)
                for line in wrapped_lines:
                    if line is None:
                        info += '\n'
                    else:
                        info += line + '\n'

            menu_text += info

        menu_text += eq_line
        menu_entries = d_menu['entries']
        entry_keys = d_menu['entries'].keys()
        key_width = str(len(max(entry_keys, key=len)) + 2)
        spec = '{0:>' + key_width + '}'
        for entry in entry_keys:
            entry_line = spec.format(entry) + '. ' + menu_entries[entry] + '\n'
            entry_line = wrapper.wrap(entry_line)[0] + '\n'
            menu_text += entry_line

        menu_text += eq_line
        #---------------------------------------
        # Display the menu.
        print(menu_text)
        prompt = wrapper.wrap(d_menu['prompt'])[0]
        resp = raw_input(prompt)
        #---------------------------------------
        # Check the response.
        l_choices = []
        if ',' in resp:
            l_choices = resp.split(',')
        else:
            l_choices.append(resp)

        done = True
        for choice in l_choices:
            if not choice in entry_keys:
                done = False
                print('  invalid choice:' + choice + '\n')
                raw_input('Press "Enter" to continue.')
                break
        #---------------------------------------
        return(resp)
# END def menu
#-----------------------------------------------------------------------