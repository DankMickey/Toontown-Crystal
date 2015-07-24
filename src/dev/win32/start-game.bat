@echo off

title Toontown Crystal Launcher [Beta]

echo Choose your connection method!
echo.
echo #1 - Localhost
echo #2 - Toontown Stride Dev Server
echo #3 - Custom
echo #4 - Local RemoteDB
echo #5 - Dan's Server
echo.

:selection

set INPUT=-1
set /P INPUT=Selection: 

if %INPUT%==1 (
    set TTS_GAMESERVER=127.0.0.1
) else if %INPUT%==2 (
    set TTS_GAMESERVER=167.114.220.172
) else if %INPUT%==4 (
    set TTS_GAMESERVER=127.0.0.1
) else if %INPUT%==5 (
    set TTS_GAMESERVER=25.195.196.22
) else if %INPUT%==3 (
    echo.
    set /P TTS_GAMESERVER=Gameserver: 
) else (
	goto selection
)

echo.

if %INPUT%==2 (
    set /P ttsUsername="Username: "
    set /P ttsPassword="Password: "
) else if %INPUT%==4 (
    set /P ttsUsername="Username: "
    set /P ttsPassword="Password: "
) else (
    set /P TTS_PLAYCOOKIE=Username: 
)

echo.

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Starting Toontown Crystal Alpha...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

cd ../../

if %INPUT%==2 (
    "dependencies/panda/python/ppython.exe" -m toontown.toonbase.ClientStartRemoteDB
) else if %INPUT%==4 (
    "dependencies/panda/python/ppython.exe" -m toontown.toonbase.ClientStartRemoteDB
) else (
    "dependencies/panda/python/ppython.exe" -m toontown.toonbase.ClientStart
)

pause
