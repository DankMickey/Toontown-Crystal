#!/bin/sh
cd ..

export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Get the user input:
read -p "Username: " ttcyUsername

# Export the environment variables:
export ttcyUsername=$ttcyUsername
export ttcyPassword="password"
export TTCY_PLAYCOOKIE=$ttcyUsername
export TTCY_GAMESERVER="127.0.0.1"

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "Starting Toontown Crystal Alpha..."
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

ppython -m toontown.toonbase.ClientStart
