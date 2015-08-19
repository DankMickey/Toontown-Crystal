@echo off

title TTCY Alpha Lancher

echo Choose your connection method!
echo.
echo #1 - Localhost
echo #2 - Custom
echo #3 - khdecoder's Server [REQUIRES WORKING HAMACHI]
echo #5 - Craigy's Test Server
echo #6 - GAMESERVER 1
echo #7 - Vince's Server
echo.

:selection

set INPUT=-1
set /P INPUT=Selection: 

if %INPUT%==1 (
    set TTCY_GAMESERVER=127.0.0.1
) else if %INPUT%==7 (
    set TTCY_GAMESERVER=vincettcy.mooo.com
    	echo You don't need Hamachi for this!
) else if %INPUT%==6 (
    set TTCY_GAMESERVER=server.toontowncrystal.com
) else if %INPUT%==3 (
    set TTCY_GAMESERVER=khdecoder.crabdance.com
	echo Hope you have the host in a Hamachi Group!
) else if %INPUT%==5 (
    set TTCY_GAMESERVER=toontowncrystal.ddns.net
	echo Have fun playing if it doesn't work im not currently hosting
) else if %INPUT%==2 (
    echo.
    set /P TTCY_GAMESERVER=Gameserver: 
) else (
	goto selection
)

echo.

if %INPUT%==6 (
    set /P ttcyUsername="Username: "
    set /P ttcyPassword="Password: "
) else (
    set /P ttcy_PLAYCOOKIE=Username: 
)

echo.


echo ===============================
echo Starting Toontown crystal...
echo ppython: "src/dependencies/panda/python/ppython.exe"

if %INPUT%==2 (
    echo Username: %ttcyUsername%
) else if %INPUT%==4 (
    echo Username: %ttcyUsername%
) else (
    echo Username: %ttcy_PLAYCOOKIE%
)

echo Gameserver: %ttcy_GAMESERVER%
echo ===============================

cd ../../../

if %INPUT%==4 (
    "src/dependencies/panda/python/ppython.exe" -m src.toontown.toonbase.ToontownStartRemoteDB
) else (
    "src/dependencies/panda/python/ppython.exe" -m src.toontown.toonbase.ToontownStart
)

pause
