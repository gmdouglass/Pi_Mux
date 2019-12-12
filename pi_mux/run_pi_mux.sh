#!/bin/bash
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# START THE TMUX SESSION AND CONFIGURE TMUX OPTIONS
# Set up the environment for the Tmux session.
#source env_pi_mux
now=$(date +%Y%m%d%H%M%S)
sess_id=${USER}_${now}
pm_dir="${HOME}/src/git/Pi_Mux"
pm_wdir="${HOME}/src/git/Pi_Mux/pi_mux"
log_dir="${pm_dir}/log"
if [[ ! -d $log_dir ]];then
    mkdir $log_dir
fi
pm_data_dir="${pm_wdir}/appdata"
if [[ ! -d $pm_data_dir ]];then
    mkdir $pm_data_dir
fi
pm_db_dir="${pm_data_dir}/db"
if [[ ! -d $pm_db_dir ]];then
    mkdir $pm_db_dir
fi
pm_db_file="${pm_db_dir}/pm.db"
tmp_dir="${HOME}/tmp"
if [[ ! -d $tmp_dir ]];then
    mkdir $tmp_dir
fi
export PM_SESS=$sess_id
export PM_DEBUG=1
export PM_DIR=$pm_dir
export PM_WDIR=$pm_wdir
export PM_LOG_DIR=$log_dir
export PM_DATA_DIR=$pm_data_dir
export PM_DB_DIR=$pm_db_dir
export PM_DB_FILE=$pm_db_file
export PM_TMP_DIR=$tmp_dir
#------------------------------------------------------------------------
# The control window is not intended for end users to use or see.
win_name="control"
tmux new-session -d -s "$sess_id" -n "$win_name"
tmux setenv -u -t $sess_id PM_SESS
tmux setenv -t $sess_id PM_SESS $sess_id

tmux setenv -u -t $sess_id PM_DEBUG
tmux setenv -t $sess_id PM_DEBUG 1

tmux setenv -u -t $sess_id PM_DIR
tmux setenv -t $sess_id PM_DIR $pm_dir

tmux setenv -u -t $sess_id PM_WDIR
tmux setenv -t $sess_id PM_WDIR $pm_wdir

tmux setenv -u -t $sess_id PM_LOG_DIR
tmux setenv -t $sess_id PM_LOG_DIR $log_dir

tmux setenv -u -t $sess_id PM_DATA_DIR
tmux setenv -t $sess_id PM_DATA_DIR $pm_data_dir

tmux setenv -u -t $sess_id PM_DB_DIR
tmux setenv -t $sess_id PM_DB_DIR $pm_db_dir

tmux setenv -u -t $sess_id PM_DB_FILE
tmux setenv -t $sess_id PM_DB_FILE $pm_db_file

tmux setenv -u -t $sess_id PM_TMP_DIR
tmux setenv -t $sess_id PM_TMP_DIR $tmp_dir

#tmux show-environment -t $sess_id
#---------------------------------------
# SESSION OPTIONS
tmux set -t "$sess_id" allow-rename off
tmux set -t "$sess_id" escape-time 0
tmux set -t "$sess_id" mode-keys vi
tmux set -t "$sess_id" history-limit 9999999
tmux set -t "$sess_id" aggressive-resize on
#---------------------------------------
# WINDOW OPTIONS
tmux setw -g xterm-keys on
tmux setw -g status-position top
tmux setw -g status-style fg=black
tmux setw -g status-justify centre
lstatus_max=53
tmux setw -g status-left-length $lstatus_max
tmux setw -g status-left-style bg=blue,fg=white,bold
tmux bind-key -n F1 new-window HELP help.sh
tmux bind-key -n F2 kill-session -t $sess_id
if [[ "$PM_DEBUG" -eq 1 ]];then
    tmux setw -g status-left "#(echo F1-Help F2-Exit F3-View Logs)"
    tmux bind-key -n F3 new-window LOGS view_logs.sh
else
    tmux setw -g status-left "#(echo F1-Help F2-Exit)"
fi

rstatus_max=25
tmux setw -g status-right-style "bg=black,fg=white"
tmux setw -g status-right-length $rstatus_max
tmux setw -g status-right "#{window_name}"
#tmux show-options
#------------------------------------------------------------------------
# Start the application.
win_id="${sess_id}:${win_name}"
tmux send-keys -t "${win_id}.0" "./pi_mux.py" "C-m"
tmux send-keys -t "${win_id}.0" "reset" "C-m"
tmux select-window -t "$win_id"
tmux attach-session -t "$sess_id"
# Make user the session is not left running after the application exits.
tmux kill-session -t "$sess_id"
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#EOF
