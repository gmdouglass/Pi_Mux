#!/usr/bin/expect
# -d
#---------------------------------------------------------------------------
# Created: 20130613
# Author: Greg Douglass
#---------------------------------------------------------------------------
# PURPOSE
#
# This script is intended to allow users to build an SSH tunnel through the
# customer's firewall and, then connect to that tunnel.
#
#############################################################################
trap Sig {INT QUIT PIPE TERM}
#============================================================================
# PROCEDURES (SUBROUTINES)
#============================================================================
#---------------------------------------------------------------------------
# Sig
proc Sig {} {
    upvar ::g_script l_script
    puts stderr "\n${l_script}\[WARN]trapped signal [trap -number] SIG_[trap -name]\n"
    exit 1
}
# END Sig
#----------------------------------------------------------------------------
proc Log {l_msg} {
    global gb_log_touched_tf argc argv
    upvar ::g_script l_script
    upvar ::gf_log lf_log
    upvar ::g_proc_name_width l_proc_name_width
    #--------------------------------------
    set l_level [info level]
    set l_caller_level [expr ($l_level -1)]
    if { $l_caller_level == 0 } {
        set l_caller_name "[format %-${l_proc_name_width}s MAIN]"
    } else {
        set l_caller_name "[format %-${l_proc_name_width}s [lindex [info level -1] 0]]"
    }
    set l_HMs [clock format [clock seconds] -format "%H%M%S"]
    set lfh_log [open "$lf_log" a]
    if {$gb_log_touched_tf == 0} {
        puts $lfh_log ""
        puts $lfh_log "##############################################################################"
        puts $lfh_log "START:${l_HMs}:$l_script"
        puts $lfh_log "ARGC:$argc"
        puts $lfh_log "ARGV:$argv"
        puts $lfh_log ""
        set gb_log_touched_tf 1
    }
    puts $lfh_log "${l_HMs}:${l_caller_name}:[pid]:${l_msg}"
    close $lfh_log
    return
}
# END Log
#----------------------------------------------------------------------------
# Ping
proc Ping {} {
    upvar ::g_script l_script
    global g_target
    set l_cmd "ping.pl -t $g_target -q"
    set l_rc [catch {exec ping.pl -t $g_target -q} l_output]
    if { $l_rc } {
        puts "\n${l_script}\[WARN]$l_cmd failed"
        puts "${l_script}\[WARN]RC = $l_rc"
        puts "${l_script}\[WARN]$l_output\n"
#        return 0
    }
    return 1
}
# END Ping
#---------------------------------------------------------------------------
proc Usage {} {
    upvar ::g_script l_script
    puts ""
    puts "USAGE: $l_script \[-t] \[-p]"
    puts ""
    puts "  '-t' \"target ID\""
    puts ""
    puts "  '-p' \"numerical target port\""
    puts ""
    return 1
}
# END Usage
#---------------------------------------------------------------------------
proc Setup {} {
    upvar ::g_script l_script
    upvar ::gb_dbg_tf lb_dbg_tf
    puts "Launching the TBARS WMConnect Utility Setup in a new window..."
    sleep 5
    # -ls starts the shell as a login shell, may or may not want this
    set l_pid [fork]
    switch $l_pid {
        -1 {
            puts stderr "${l_script}\[WARN]Spawning setup_wmconnect.tcl failed!"
            puts "Press any key to continue."
            gets stdin l_junk
            return 0
        }
        0 {
            exec xterm -e setup_wmconnect.tcl
            exit
        }
        default {
            if { $lb_dbg_tf } {
                puts stderr "${l_script}\[WARN]Spawning setup_wmconnect.tcl failed!"
                puts "Press any key to continue."
                gets stdin l_junk
            }
            exit 1
        }
    }
}
# Setup END
#---------------------------------------------------------------------------
#============================================================================
# MAIN
#============================================================================
set g_script [string trim [file tail $argv0]]
if { $argc < 1 } {
    puts "\n${g_script}\[WARN]missing argument\n"
    exit 1
}
#--------------------------------------
set gd_home [string trim $::env(HOME)]
set lb_found_username 0
foreach env_var [lsort [array names ::env]] {
    if {$env_var eq "USERNAME"} {
        set g_user [string trim $::env(USERNAME)]
        set lb_found_username 1
    } elseif {$env_var eq "USER"} {
        set g_user [string trim $::env(USER)]
        set lb_found_username 1
    }
}
if {! $lb_found_username} {
    puts stderr "\[WARN] Unable to determine username from the environment!"
    exit 1
}
set gd_log "${gd_home}/log"
file mkdir "$gd_log"
set gd_tmp "${gd_home}/tmp"
file mkdir "$gd_tmp"
#--------------------------------------
#set gd_wmc .
#--------------------------------------
set g_Ymd [clock format [clock seconds] -format "%Y%m%d"]
set gf_log "${gd_log}/${g_script}.${g_Ymd}.log"
set gb_log_touched_tf 0
set g_proc_name_width 0
foreach l_name [info procs] {
    if {[regexp {auto_} "$l_name"]} {continue}
    set l_length [string length $l_name]
    if { $l_length > $g_proc_name_width } {
        set g_proc_name_width $l_length
    }
}
if {[lindex $argv 0] ne "-dorealprocessing"} {
    #--------------------------------------
    set gb_dbg_tf 1
    set g_my_arg_list $argv
    set l_dbg_index [lsearch -exact $argv -debug]
    if { $l_dbg_index >= 0 } {
        Log "Debugging is enabled!"
        set g_my_arg_list [lsearch -exact -all -inline -not $argv -debug]
    } else {
        set gb_dbg_tf 0
    }
    if { ! $gb_dbg_tf } {
        log_user 0
    }
    #---------------------------------------------------------------------------
    # This hardcoded IP is for HPREBARS from the HPE side of the firewall.
    !!! NEED TO CONVERT HERE
    set g_ssh_server_ip 161.170.140.72
    #---------------------------------------------------------------------------
    # required arg flags
    # !!! probably not needed
    #set gb_opt_p_tf 0
    set gb_opt_t_tf 0
    # optional argument for user
    set gb_opt_u_tf 0
    # Check commandline
    set l_prev_arg ""
    Log "g_my_arg_list:'${g_my_arg_list}'"
    foreach l_curr_arg $g_my_arg_list {
        if {"$l_prev_arg" eq ""} {
            set l_prev_arg $l_curr_arg
            continue
        }
        #------------------------------------------------------------------------
        # The previous argument started with a dash and,
        # the current argument does not have a leading dash.
        if { [regexp {^-} "$l_prev_arg"] && [regexp {^[^-]} "$l_curr_arg"] } {
            #--------------------------------------------------------------------
            # Match Prev (the leading dash arg) against expected args and,
            # assign CurrArg appropriately.
            if {[regexp {\-t} "$l_prev_arg"]} {
                set gb_opt_t_tf 1
                set g_target $l_curr_arg
                Log "g_target: $g_target"
            } elseif {[regexp {\-p} "$l_prev_arg"]} {
    # !!! probably not needed
                #set gb_opt_p_tf 1
                set g_target_port $l_curr_arg
                Log "g_target_port: $g_target_port"
# !!! DISALLOW USER OTHER THAN LOGIN ID OR SET UP ACL
#            } elseif {[regexp {\-u} "$l_prev_arg"]} {
#                set gb_opt_u_tf 1
#                set g_user $l_curr_arg
#                Log "g_user: $g_user"
            } else {
                Log "invalid argument  : '${l_curr_arg}'"
                Log "received arguments: '${g_my_arg_list}'"
                Usage
                exit 1
            }
        } elseif {[regexp {^[^-]} "$l_prev_arg"] && [regexp {^-} "$l_curr_arg"]} {
            #------------------------------------------------------------------------
            # The previous argument did not start with a dash and, the current
            # argument does.
            set l_prev_arg $l_curr_arg
            continue
        } elseif { [regexp {^-} "$l_prev_arg"] && [regexp {^-} "$l_curr_arg"]} {
            #--------------------------------------------------------------------
            # Prev is a Boolean. Match against expected Booleans
            if {[regexp {\-h} "$l_prev_arg"] || [regexp {\-help} "$l_prev_arg"]} {
                Usage
                exit 0
            } else {
                # NOOP
                puts -nonewline ""
            }
        } elseif {[regexp {^[^-]} "$l_prev_arg"] && [regexp {^[^-]} "$l_curr_arg"]} {
            #------------------------------------------------------------------------
            # The previous argument has no leading dash and,
            # the current argument does not have a leading dash.
            # UNEXPECTED
            puts stderr "${g_script}\[WARN]unexpected argument:'$l_curr_arg'"
            exit 1
        } else {
            set l_prev_arg $l_curr_arg
            continue
        }
        set l_prev_arg $l_curr_arg
        continue
    }
    # REQUIRED ARGS
    # !!! probably not needed
    #if { ! $gb_opt_t_tf || ! $gb_opt_p_tf } {
    if { ! $gb_opt_t_tf } {
        Log "A required argument is missing."
        Log "received arguments:'${g_my_arg_list}'"
        puts "\nA required argument is missing."
        puts "received arguments:'${g_my_arg_list}'\n"
        Usage
        puts "${g_script} \[FATAL]"
        exit 1
    }
    #---------------------------------------------------------------------------
#    Log "Pinging ${g_target}..."
#    if { ! [Ping] } {
#        Log "$g_target could not be pinged."
#        puts "\n${g_script}\[WARN] $g_target could not be pinged.\n"
#        exit 1
#    }
    #---------------------------------------------------------------------------
    # g_tun_port is always the port at the local end of the tunnel through
    # hprebars. That tunnel may end on bvar or on the local host.
    # Either way, that's the port to which we will connect.
    # Find a local, unused port to use for the SSH tunnel.
# !!! NO TUNNELS
#    Log "get_tcp_port.pl"
#    set l_rc [catch {exec get_tcp_port.pl} g_tun_port]
#    if { $l_rc != 0 } {
#        Log "get_tcp_port.pl failed"
#        Log "$g_tun_port"
#        puts "\n${g_script}\[WARN] get_tcp_port.pl failed\n"
#        exit 1
#    }
#    set g_tun_port [string trim $g_tun_port]
#    Log "g_tun_port:$g_tun_port"
    #-----------------------------------------------------------------------
    # Build the local tunnel.
#    puts "$g_tun_port"
    set l_command [list [info nameofexecutable]]
#    if {![info exists ::starkit::mode] || $starkit::mode ne "starpack"} {
#        lappend l_command [info script]
#    }
    !!! NEED TO CONVERT HERE
    set l_tun_cmd [list /usr/bin/ssh -C -p 5584 -g -N -L $g_tun_port:$g_target:$g_target_port ${g_user}@$g_ssh_server_ip]
    Log "CMD: $l_tun_cmd"
    eval exec $l_command -dorealprocessing $l_tun_cmd >/dev/null &
    sleep 1
    exit 0
} else {
    set l_tun_cmd [lrange $argv 1 end]
#    set l_tun_cmd [list /usr/bin/ssh -C -c arcfour128,blowfish-cbc -p 5584 -g -N -L $g_tun_port:$g_target:$g_target_port ${g_user}@$g_ssh_server_ip]
    Log "spawn -noecho $l_tun_cmd"
    eval spawn -noecho $l_tun_cmd
    expect -- "pooky"
    wait
    exit 0
}
