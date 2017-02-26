# -*- coding: utf-8 -*-
# Load fabfile and other necessary modules
import time
from fabric.api import env, run
from fabric.context_managers import cd
from fabric.operations import get

# Declare remote host
env.hosts = ['login.osgconnect.net']

# Declare remote username and key info (optional)
with open('/gh/data2/username.txt','r') as myfile:
    env.user = myfile.read()
with open('/gh/data2/pw.txt','r') as myfile:
    env.password = myfile.read()
    
# Commands to execute on the remote server
def run_demo():
    run("git clone https://github.com/srcole/demo_OSG_python")
    with cd('demo_OSG_python'):
        get("./out*")