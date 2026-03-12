#!/usr/bin/env bash
set -euo pipefail

LARS_PLOTS_DIR="$HOME/SlowControl/plots"
REMOTE_USER="atp"
REMOTE_SERVER="farm-ui2.physik.uzh.ch"
REMOTE_PLOTS_DIR="/home/atp/marmotx/public_html/sc/data_include/LArs/"

LOGFILE="$HOME/local/var/log/lars_plot_sync.log"
mkdir -p "$(dirname "$LOGFILE")"

echo "[$(date)] Starting rsync" >> "$LOGFILE"
rsync -auvP "$LARS_PLOTS_DIR/"*.png "$REMOTE_USER@$REMOTE_SERVER:$REMOTE_PLOTS_DIR" >> "$LOGFILE" 2>&1
echo "[$(date)] Finished rsync" >> "$LOGFILE"
