import subprocess, os, sys, runpy

username = raw_input("> ")
password = raw_input("> ") 

os.environ["TTCY_GAMESERVER"] = "server.toontowncrystal.com"
os.environ["ttcyUsername"] = username
os.environ["ttcyPassword"] = password

runpy.run_module('src.toontown.toonbase.ToontownStart', run_name='__main__', alter_sys=True)
