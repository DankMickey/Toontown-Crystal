import subprocess, os, sys

#import src.toontown.toonbase.ToontownStart
import src.toontown.toonbase

username = raw_input("> ")
password = raw_input("> ") 

os.environ["TTCY_GAMESERVER"] = "server.toontowncrystal.com"
os.environ["ttcyUsername"] = username
os.environ["ttcyPassword"] = password

subprocess.call(['src\dependencies\panda\python\ppython.exe', 'src/toontown/toonbase/ToontownStart.py'])
