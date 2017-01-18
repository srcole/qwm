# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 20:34:25 2017

@author: Scott
"""

import time    
from fabric.api import env, run
from fabric.context_managers import cd
from fabric.operations import get
env.hosts = ['login.osgconnect.net']
with open('C:/gh/data2/username.txt','r') as myfile:
    env.user = myfile.read()
with open('C:/gh/data2/pw.txt','r') as myfile:
    env.password = myfile.read()
    
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
        # Need to wait til done running
        # Could do this by repeatedly sleeping and checking how many files
        # there are, and only continue after time limit ot all files done
        time.sleep(300)
        get("./out*")
    
def run_demo3():
    with cd('demo_OSG_python'):
        run("condor_submit sub_PsTs.submit")
        time.sleep(300)
        get("./out*")
    
def run_demo2():
    with cd('demo_OSG_python'):
        get("./out*")

def uptime():
    run("pwd")
    with cd('demo_OSG_python'):
        run("pwd")
        run("uptime")

def test_get():
    get("./temp*")