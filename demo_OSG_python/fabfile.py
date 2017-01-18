# -*- coding: utf-8 -*-
# Load fabfile and other necessary modules
import time
from fabric.api import env, run
from fabric.context_managers import cd
from fabric.operations import get

# Declare remote host
env.hosts = ['login.osgconnect.net']

# Declare remote username and key info (optional)
with open('C:/gh/data2/username.txt','r') as myfile:
    env.user = myfile.read()
with open('C:/gh/data2/pw.txt','r') as myfile:
    env.password = myfile.read()
    
# Commands to execute on the remote server
def run_demo():
    run("git clone https://github.com/srcole/demo_OSG_python")
    with cd('demo_OSG_python'):
        run("chmod +x create_virtenv.sh")
        run("./create_virtenv.sh")
        run("rm -R python_virtenv_demo")
        run("mv lfp_set/ /stash/user/"+env.user+"/lfp_set/")
        run("tar -cvzf misshapen.tar.gz misshapen")
        run("rm -R misshapen")
        run("mkdir Log")
        run("condor_submit sub_PsTs.submit")
        # Need to wait until done running; should be less than 5 minutes
        time.sleep(300)
        get("./out*")