
import subprocess, os, sys

username = raw_input("> ")
password = raw_input("> ") 

os.environ["TTCY_GAMESERVER"] = "server.toontowncrystal.com"
os.environ["ttcyUsername"] = username
os.environ["ttcyPassword"] = password

subprocess.call(['dependencies\panda\python\ppython.exe', '-m', 'toontown.toonbase.ToontownStart'])
