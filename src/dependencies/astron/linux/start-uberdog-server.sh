#!/bin/sh
cd ../..

# Define some constants for our AI server:
MAX_CHANNELS=999999
STATESERVER=4002
ASTRON_IP="127.0.0.1:7100"
EVENTLOGGER_IP="127.0.0.1:7198"

# Get the user input:
read -p "Base channel (DEFAULT: 1000000): " BASE_CHANNEL
BASE_CHANNEL=${BASE_CHANNEL:-1000000}

echo "==============================="
echo "Starting Toontown Crystal Ubderdog.."
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

while [ true ]
do
/usr/bin/python2 -m toontown.uberdog.ServiceStart --base-channel $BASE_CHANNEL \
                 --max-channels $MAX_CHANNELS --stateserver $STATESERVER \
                 --astron-ip $ASTRON_IP --eventlogger-ip $EVENTLOGGER_IP
done
