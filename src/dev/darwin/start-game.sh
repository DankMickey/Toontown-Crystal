#!/bin/sh
cd ..

export DYLD_LIBRARY_PATH=`pwd`/Libraries.bundle
export DYLD_FRAMEWORK_PATH="Frameworks"

# Get the user input:
read -p "Username: " ttsUsername
read -p "Gameserver (DEFAULT:  127.0.0.1): " TTS_GAMESERVER
TTS_GAMESERVER=${TTS_GAMESERVER:-"127.0.0.1"}

# Export the environment variables:
export ttsUsername=$ttsUsername
export ttsPassword="password"
export TTS_PLAYCOOKIE=$ttsUsername
export TTS_GAMESERVER=$TTS_GAMESERVER

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "Starting Toontown Crystal Alpha..."
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

ppython -m toontown.toonbase.ClientStart
