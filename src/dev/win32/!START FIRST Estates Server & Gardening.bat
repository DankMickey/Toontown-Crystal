@echo off
title Toontown crystal Development MongoDB

cd ../../

:main
"dependencies/MongoDB\Server\3.0\bin\mongod.exe" --dbpath dependencies/MongoDB/GardeningDatabase


pause
