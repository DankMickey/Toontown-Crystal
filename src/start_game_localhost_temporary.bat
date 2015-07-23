@echo off

set /P ttsUsername="Username (DEFAULT: username): " || ^
set ttsUsername=username
set ttsPassword=password
set TTS_PLAYCOOKIE=%ttrUsername%
set TTS_GAMESERVER=localhost

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH


echo ===============================
echo Starting Toontown Stride...
echo ppython: %PPYTHON_PATH%
echo Username: %ttsUsername%
echo Client Agent IP: %TTS_GAMESERVER%
echo ===============================

%PPYTHON_PATH% -m toontown.toonbase.ClientStart
pause
