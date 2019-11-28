#!/bin/bash
source ./env_pi_mux

tmux new-session -d -s "${PM_SESS}" -n control
tmux set -g -t "${PM_SESS}" allow-rename off
tmux set -g -t "${PM_SESS}" escape-time 0
tmux set -g -t "${PM_SESS}" mode-keys vi
tmux set -g -t "${PM_SESS}" history-limit 9999999
tmux set -g -t "${PM_SESS}" aggressive-resize on

tmux set -g -t "${PM_SESS}" status-position top
tmux set -g -t "${PM_SESS}" status-style fg=black
tmux set -g -t "${PM_SESS}" status-justify centre
tmux set -g -t "${PM_SESS}" status-left-length 50
tmux set -g -t "${PM_SESS}" status-right-style "bg=black,fg=white"
tmux set -g -t "${PM_SESS}" status-right-length 10

tmux bind-key -n F1 new-window -t "${PM_SESS}" -n HELP help.sh
tmux bind-key -n F2 new-window -t "${PM_SESS}" -n TEST test.py
tmux bind-key -n F3 kill-session -t "${PM_SESS}"
tmux bind-key -n F4 choose-window
tmux set -g -t "${PM_SESS}" status-left-style bg=blue,fg=white,bold
tmux set -g -t "${PM_SESS}" status-left "#(echo F1-Help F2-Test F3-Exit F4-Choose Window)"
tmux set -g -t "${PM_SESS}" status-right "#{window_name}"

tmux set -ag update-environment "${PM_ENV_STR}"

tmux send-keys -t "${PM_SESS}":control.0 "./pi_mux.py" "C-m"
#tmux send-keys -t "${PM_SESS}":control.0 "clear" "C-m"

#tmux send-keys -t "${PM_SESS}":control.0 "echo TMUX SERVER OPTIONS:" "C-m"
#tmux send-keys -t "${PM_SESS}":control.0 "tmux show-options -s" "C-m"
#tmux send-keys -t "${PM_SESS}":control.0 "echo" "C-m"

#tmux send-keys -t "${PM_SESS}":control.0 "echo TMUX SESSION OPTIONS:" "C-m"
#tmux send-keys -t "${PM_SESS}":control.0 "tmux show-options -g" "C-m"
#tmux send-keys -t "${PM_SESS}":control.0 "echo" "C-m"

#tmux send-keys -t "${PM_SESS}":control.0 "echo TMUX ENV:" "C-m"
#tmux send-keys -t "${PM_SESS}":control.0 "tmux show-environment" "C-m"

#tmux select-window -t "${PM_SESS}":control
tmux attach-session -t "${PM_SESS}"
tmux kill-session -t "${PM_SESS}"
#tmux kill-server
#tmux ls