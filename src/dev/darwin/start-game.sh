#!/bin/sh
cd ../../../

export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Get the user input:
read -p "Username: " ttcyUsername
read -p "Gameserver (DEFAULT:  167.114.28.238): " ttcy_GAMESERVER
ttcy_GAMESERVER=${ttcy_GAMESERVER:-"167.114.28.238"}

# Export the environment variables:
export ttcyUsername=$ttcyUsername
export ttcyPassword="password"
export ttcy_PLAYCOOKIE=$ttcyUsername
export ttcy_GAMESERVER=$ttcy_GAMESERVER

echo "==============================="
echo "Starting Toontown crystal..."
echo "Username: $ttcyUsername"
echo "Gameserver: $ttcy_GAMESERVER"
echo "==============================="

ppython -m src.toontown.toonbase.ToontownStart