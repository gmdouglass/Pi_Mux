#!/bin/bash

source ./env_pi_mux

sess_id="$CURR_TM_SESS"
win_name="control"
win_id="${sess_id}:${win_name}"

tmux new-session -d -s "$sess_id" -n "$win_name"
tmux set -t "$sess_id" allow-rename off
tmux set -t "$sess_id" escape-time 0
tmux set -t "$sess_id" mode-keys vi
tmux set -t "$sess_id" history-limit 9999999
tmux set -t "$sess_id" aggressive-resize on

tmux set -w -t "$win_id" window-status-position top
tmux set -w -t "$win_id" window-status-style fg=black
tmux set -w -t "$win_id" window-status-justify centre
tmux set -w -t "$win_id" window-status-left-length 50
tmux set -w -t "$win_id" window-status-right-style "bg=black,fg=white"
tmux set -w -t "$win_id" window-status-right-length 10

tmux set -w -t "$win_id" window-status-left-style bg=blue,fg=white,bold
#tmux set -g -t "$sess_id" status-left "#(echo F1-Help F2-Test F3-Exit F4-Choose Window)"
tmux set -w -t "$win_id" window-status-left "#(echo F1-Help F2-Exit)"
#tmux set -w -t "$win_id" window-status-right "#{window_name}"
#tmux set -w -t "$win_id" xterm-keys on
tmux bind-key -n F1 new-window -t "$sess_id" -n HELP help.sh
#tmux bind-key -n F2 new-window -t "$sess_id" -n TEST test.py
tmux bind-key -n F2 kill-session -t "$sess_id"
#tmux bind-key -n F4 choose-window


tmux send-keys -t "${win_id}.0 ./pi_mux.py" "C-m"
tmux set -ag update-environment "$PM_ENV_STR"
#tmux send-keys -t "${win_id}.0 "clear" "C-m"

#tmux send-keys -t "${win_id}.0 "echo TMUX SERVER OPTIONS:" "C-m"
#tmux send-keys -t "$win_id}.0 "tmux show-options -s" "C-m"
#tmux send-keys -t "$win_id}.0 "echo" "C-m"

#tmux send-keys -t "${win_id}.0 "echo TMUX SESSION OPTIONS:" "C-m"
#tmux send-keys -t "${win_id}.0 "tmux show-options -g" "C-m"
#tmux send-keys -t "${win_id}.0 "echo" "C-m"

#tmux send-keys -t "${win_id}.0 "echo TMUX ENV:" "C-m"
#tmux send-keys -t "${win_id}.0 "tmux show-environment" "C-m"

#tmux select-window -t "$win_id"
tmux attach-session -t "$sess_id"
tmux kill-session -t "$sess_id"
#tmux kill-server
#tmux ls
