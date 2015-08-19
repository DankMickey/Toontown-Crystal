@echo off
cd "../../src/dependencies/astron/"

title TTCY Astron
astrond --loglevel info config/cluster.yml
pause
