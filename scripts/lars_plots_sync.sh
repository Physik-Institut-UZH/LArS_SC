#!/usr/bin/env bash

LARS_PLOTS_DIR="$HOME/SlowControl/plots"

REMOTE_USER="atp"
REMOTE_SERVER="farm-ui2.physik.uzh.ch"
REMOTE_PLOTS_DIR="/home/atp/marmotx/public_html/sc/data_include/LArs"

SLEEP_SECS=120

while [ 1 ]
do
	rsync -avP "$LARS_PLOTS_DIR/*.png" "$REMOTE_USER@$REMOTE_SERVER:$REMOTE_PLOTS_DIR"
	sleep $SLEEP_SECS
done
