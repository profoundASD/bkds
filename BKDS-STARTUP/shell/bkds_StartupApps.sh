#!/bin/bash
#####################################################################
# Usage:
# Description:
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id="BKDS_STARTUP_${1}"
#shell scripts used - startup
shell_path="$BKDS_STARTUP_SHELL"
#node_id_script="$shell_path/bkds_SetHostName.sh"
keyring_script="$shell_path/bkds_KeyringTrigger.sh"
sound_check_script="$shell_path/bkds_SoundCheck.sh"
syncthing_script="$shell_path/bkds_SyncthingFailSafe.sh"
netdata_script="$shell_path/bkds_StartupNetData.sh"
conky_script="$BKDS_DESKTOP_SHELL/bkds_ConkyLaunch.sh"
set_mouse_config_script="$shell_path/bkds_SetMouse.sh"

#automation scheduler
auto_sched_script="$BKDS_AUTO_SCHED_SHELL/bkds_AutomationLoop.sh"
#util scripts used
log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py" #shell scripts
util_shell_path="$BKDS_UTIL_SHELL"
sound_script="$util_shell_path/bkds_SystemSound.sh" #python scripts
screenshot_script="$util_shell_path/bkds_ScreenShot.sh" #sends back to reporting a screenshot of desktop/conky on each boot
redshift_script="$util_shell_path/bkds_redShift.sh" #checks time and sets blue filter for display

#calendar_widget="$BKDS_DESKTOP_PYTHON/bkds_CalendarWidget.py"
#ui_panel_script="xfce4-panel --quit"
#other files/settings used
gnome_settings="screen-keyboard-enabled false"
initial_volume=70 # 65%
interval_wait=300 #automation scheduler wait between checks
max_intervals=100 #max attempts any scheduled program execute
keyring_trigger_timeout=6 #the process(es) will only live for this amount of time

audio_app="/usr/bin/mpg123"
audio_path="$BKDS_UTIL_MP3"
audio_file="$audio_path/bkdsStartupSound.mp3"

########################################################################
#  Main logic and functions
log_msg() {
    python3 $log_script "$program_name" "$batch_id" "$1" && echo "$1"
}

    #bash reset_env.sh $batch_id "ffplay" "conky" "brave" "chrome" "code" "thunderbird" "gnome-system-monitor" "bashtop"
    log_msg "startup settings..."
    log_msg "start_time: $( date '+%Y-%m-%d %H:%M:%S')"
    log_msg "program_name: $program_name"
    log_msg "base_name: $0"
    log_msg "batch id: $batch_id"
    log_msg "Current Directory: $(pwd)"
# Setup / Resetting env complete
########################################################################



########################################################################
# set node id/hostname begin
# sets hostname to the node id. drives backend reporting
# checks first and only changes if not set to the preferred
#
    log_msg "checking current hostname: $(hostname)"
    #checks the preferred node_id against hostname
    #sets hostname to node_id if needed 
    #bash $node_id_script "$batch_id"
    node_id=$(hostname) #reset node_id to be most recent hostname
    log_msg "using from hostname: $(hostname)"
# set node id/hostname end
########################################################################

########################################################################
# red shift begin
log_msg "redshift starting with $redshift_script"

bash $redshift_script

log_msg "redshift ending with $redshift_script"

# red shift end
########################################################################

########################################################################
# Conky App Launch Begin
# Launches soon to display during workspace transformation
# 
    log_msg "$conky_script begins"
    bash $conky_script $batch_id $node_id &
    log_msg "$conky_script attempted"
# Conky App Launch end
########################################################################

########################################################################
# Configure Sound Begin
    log_msg "$sound_check_script begins"
    sleep 5 # wait for 5 seconds after boot up
    bash $sound_check_script $batch_id $initial_volume &
    log_msg "$sound_check_script attempted"
# Configure Sound end
########################################################################


########################################################################
# startup sound begin
#
log_msg "startup audio"
if pgrep -x "$audio_app" > /dev/null; then
    log_msg "Terminating existing processes"
    pkill -x "$audio_app"
fi
sleep 0.25
log_msg "Starting $audio_app"
$audio_app "$audio_file" &

# startup sound end
########################################################################

########################################################################
#keyrying unlock begin
    log_msg "$keyring_script begins"
    #bash $keyring_script $batch_id $keyring_trigger_timeout &
    sleep 1 
    #bash $keyring_script $batch_id $keyring_trigger_timeout &
    log_msg "$keyring_script ends"
#keyrying unlock end
########################################################################

########################################################################
# Configure Automation Begin
    log_msg "$set_mouse_config_script begins with $batch_id"
    bash $set_mouse_config_script $batch_id 
    log_msg "$set_mouse_config attempted"
# Configure Automation end
#########################################################################


########################################################################
# Configure Sound Begin
    log_msg "$screenshot_script begins with $batch_id"
    sleep 5 #give use chance to get through keyring unlock
    bash $screenshot_script $batch_id
    log_msg "$screenshot_script attempted"
# Configure Sound end
########################################################################



#########################################################################
# Final Settings Begin    
    #give gnome time before changing settings
    log_msg "pausing before applying gnome settings: $gnome_settings"
    sleep 12
    gsettings set org.gnome.desktop.a11y.applications $gnome_settings
    log_msg "$gnome_settings appllied"
# Final Settings End
#########################################################################

########################################################################
# Conky / Syncthing failsafe begin
# Launches soon to display during workspace transformation
# 
    log_msg "$conky_script failsafe begins"
    bash $conky_script $batch_id $node_id &
    log_msg "$conky_script failsafe attempted"
# Conky / Syncthing failsafe begin
########################################################################


#########################################################################
# Cleanup begin
    #kill audio if still playing
    pkill -f "mpg123 $audio_file" &
# Cleanup end
#########################################################################

########################################################################
# Configure Automation Begin
    log_msg "$auto_sched_script begins with $interval_wait and $max_intervals for $batch_id"
    bash $auto_sched_script $interval_wait $max_intervals $batch_id
    log_msg "$auto_sched_script attempted"
# Configure Automation end
########################################################################

# startup end
    log_msg "Boot sequence complete at $(date '+%Y-%m-%d %H:%M:%S')"
# startup end
#########################################################################

