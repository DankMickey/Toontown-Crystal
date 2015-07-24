@echo off

rem Define some constants for our UberDOG server:
set MAX_CHANNELS=999999
set STATESERVER=4002
set ASTRON_IP=127.0.0.1:7100
set EVENTLOGGER_IP=127.0.0.1:7198

rem Get the user input:
set /P BASE_CHANNEL="Base channel (DEFAULT: 1000000): " || ^
set BASE_CHANNEL=1000000

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Starting Toontown Crystal Uberdog...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

cd ../../

:main
"dependencies/panda/python/ppython.exe" ^
	-m toontown.uberdog.ServiceStart ^
	--base-channel %BASE_CHANNEL% ^
	--max-channels %MAX_CHANNELS% ^
	--stateserver %STATESERVER% ^
	--astron-ip %ASTRON_IP% ^
	--eventlogger-ip %EVENTLOGGER_IP%
goto main
