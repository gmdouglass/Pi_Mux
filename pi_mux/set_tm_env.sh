#-----------------------------------------------------------------------
tmux setenv -g PM_DEBUG 1
tmux setenv -g PM_SESS "${USER}_$(date +%Y%m%d%H%M%S)"
pm_dir="${HOME}/src/git/Pi_Muxx"
tmux setenv -g PM_DIR "${HOME}/src/git/Pi_Mux"
pm_wdir="${HOME}/src/git/Pi_Mux/pi_mux"
tmux setenv PM_WDIR="$pm_wdir"
log_dir="${pm_dir}/log"
if [[ ! -d $log_dir ]];then
    mkdir $log_dir
fi
tmux setenv -g PM_LOG_DIR="$log_dir"
pm_data_dir="${pm_wdir}/appdata"
if [[ ! -d $pm_data_dir ]];then
    mkdir $pm_data_dir
fi
tmux setenv -g PM_DATA_DIR="$pm_data_dir"
pm_db_dir="${pm_data_dir}/db"
if [[ ! -d $pm_db_dir ]];then
    mkdir $pm_db_dir
fi
tmux setenv -g PM_DB_DIR="$pm_db_dir"
pm_db_file="${pm_db_dir}/pm.db"
tmux setenv -g PM_DB_FILE="$pm_db_file"
tmp_dir="${HOME}/tmp"
if [[ ! -d $tmp_dir ]];then
    mkdir $tmp_dir
fi
tmux setenv -g  PM_TMP_DIR="$tmp_dir"
#------------------------------------------------------------------------

