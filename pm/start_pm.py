#!/bin/bash
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
app_name="PM"
app_env_name="$(echo $app_name | tr '[:lower:]' '[:upper:]')"
app_name_lc="$(echo $app_name | tr '[:upper:]' '[:lower:]')"

if [[ ! -e app_env ]];then
    if [[ -L $0 ]];then
        wdir=$(dirname $(ls -l $(dirname $0) | grep $(basename $0) \
            | awk '{print $NF}'))
        cd "$wdir"
    else
        cd $(dirname $0)
    fi
fi
app_wdir=$(pwd)
echo
echo "Current working directory: $(pwd)"
echo

if [[ ! -e app_env ]];then
    echo
    echo "The $app_name environment could not be initialized."
    echo
    exit 1
fi

debug=0
if [[ $# = 1 ]];then
    if [[ $1 == '-d' ]];then
        debug=1
    fi
fi
unset "${app_env_name}_DEBUG"
export "${app_env_name}_DEBUG"="$debug"

source app_env
sess_id="$PM_SESS"
echo "sess_id:$sess_id"
app_dir="$PM_DIR"
echo "app_dir:$app_dir"

#------------------------------------------------------------------------
# The control window is not intended for end users to use or see.
win_name="control"
tmux new-session -d -s "$sess_id" -n "$win_name"

tmux setenv -u -t $sess_id "${app_env_name}_SESS"
tmux setenv -t $sess_id "${app_env_name}_SESS" "$sess_id"

tmux setenv -u -t $sess_id "${app_env_name}_DIR"
tmux setenv -t $sess_id "${app_env_name}_DIR" "$app_dir"

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
tmux bind-key -n F1 new-window -n HELP ./help.sh
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
tmux setw -g status-right "%c  #{window_name}"
#tmux show-options
#------------------------------------------------------------------------
# Start the application.
win_id="${sess_id}:${win_name}"
tmux send-keys -t "${win_id}.0" "./${app_name_lc}.py" "C-m"
tmux send-keys -t "${win_id}.0" "reset" "C-m"
tmux select-window -t "$win_id"
tmux attach-session -t "$sess_id"
# Make user the session is not left running after the application exits.
tmux kill-session -t "$sess_id"
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#EOF
