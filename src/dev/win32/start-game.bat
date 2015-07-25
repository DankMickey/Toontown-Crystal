@echo off

title Toontown Crystal Alpha Launcher

echo Choose your connection method!
echo.
echo #1 - Localhost
echo #2 - Custom
echo #3 - Dan's Server
echo.

:selection

set INPUT=-1
set /P INPUT=Selection: 

if %INPUT%==1 (
    set TTS_GAMESERVER=127.0.0.1
) else if %INPUT%==3 (
    set TTS_GAMESERVER=25.195.196.22
) else if %INPUT%==2 (
    echo.
    set /P TTS_GAMESERVER=Gameserver: 
) else (
	goto selection
)

echo.

) else (
    set /P TTS_PLAYCOOKIE=Username: 
)

echo.

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Starting Toontown Crystal Alpha...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

cd ../../

) else (
    "dependencies/panda/python/ppython.exe" -m toontown.toonbase.ClientStart
)

pause
