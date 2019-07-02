import os, sys
import configparser
from subprocess import Popen, PIPE
import test_setup
import subprocess
import time
import atexit
import threading, json, pickle


"""
Performs scalability and performance tests by making increasingly more concurrent requests to pman and capturing resource utilization
"""


success_pfioh_push = 0                               # Success rate of pfioh_push

success_pman_run = 0                               # Success rate of pman_run

success_pman_status = 0                               # Success rate of pman_status

success_pfioh_pull = 0                               # Success rate of pfioh_pull



config = configparser.ConfigParser()
config.read('config.cfg')

RANGE = int(config.get('ConfigInfo', 'RANGE'))
SIZE = config.get('ConfigInfo', 'SIZE')
TIMEOUT = config.get('ConfigInfo', 'TIMEOUT')
THRESHOLD = config.get('ConfigInfo', 'THRESHOLD')
PATH = os.path.dirname(os.getcwd())
WAIT = config.get('ConfigInfo', 'WAIT')
PMAN_URL = config.get('ConfigInfo', 'PMAN_URL')
PFIOH_URL = config.get('ConfigInfo', 'PFIOH_URL')
JID = "healthcheckfinal"

test_setup.check()

with open("export.sh", "w+") as file:
    file.write('export error=error')

def open_subprocess(cmd):
    command = subprocess.Popen("timeout " + TIMEOUT + " " + cmd,shell=True, stdout=subprocess.PIPE)
    return command

def job_delete():
    print("\n" + "Program Ended")
    cmd = 'bash %s/scripts/run_pman_delete %s %s ' % (PATH, PFIOH_URL,JID )
    command = open_subprocess(cmd)
    output = command.stdout.read()                                                     
    output = str(output, "utf-8")
    print(output)



atexit.register(job_delete) # Makes code reentrant, deleting all progress when program ends

for x in range(1, RANGE + 1):
    
    print("Iteration " + str(x))
    print("_________________")

    cmd = 'bash %s/scripts/run_pfioh_push %s %s %s' % (PATH, PFIOH_URL, JID, SIZE)
    command = open_subprocess(cmd)
    print(cmd)  	
    output = command.stdout.read()                                                     
    output = str(output, "utf-8")
    if '"status": true' in output:
        success_pfioh_push = success_pfioh_push + 1
        cmd = 'bash %s/scripts/run_pman %s %s' % (PATH, PMAN_URL,str(JID))
        print(cmd)
        command = open_subprocess(cmd)
        output = command.stdout.read()                                                     
        output = str(output, "utf-8")
        if 'status": true' in output:
            success_pman_run = success_pman_run + 1
            num = 0
            while num<20:
                cmd = 'bash %s/scripts/run_pman_status %s %s' % (PATH, PMAN_URL,JID)
                print(cmd)
                command = open_subprocess(cmd)
                output = command.stdout.read()                                                     
                output = str(output, "utf-8")
                print(output)
                if '"status": finished' in output:
                    break
                else:
                    time.sleep(int(WAIT))
                    num = num + 1
            if '"status": finished' in output:
                success_pman_status = success_pman_status + 1   
                cmd = 'bash %s/scripts/run_pfioh_pull %s %s %s' % (PATH, PFIOH_URL ,JID, SIZE)
                command = open_subprocess(cmd)
                print(cmd)  	
                output = command.stdout.read()                                                     
                output = str(output, "utf-8")
                print(output)
                if 'status": true' in output:
                    success_pfioh_pull = success_pfioh_pull + 1
                    job_delete()
                else:
                    print("Error in Pfioh pull")
                    print(output)
        
            else: 
                print("Error in obtaining a complete status of Pman's job")
                job_delete()
                print(output)
        else:
            print("Error in running job in Pman")
            print(output)
    else:
        print("Error in Pfioh push")
        print(output)

success_pfioh_push = int((success_pfioh_push/RANGE)*100)
success_pman_run = int((success_pman_run/RANGE)*100)
success_pman_status = int((success_pman_status/RANGE)*100)
success_pfioh_pull = int((success_pfioh_pull/RANGE)*100)
threshold = int(THRESHOLD) 

state = True
msg = ""


if threshold > success_pfioh_push:
    msg = ", Pfioh Push"
    state = False
if threshold > success_pman_run:
    msg += ", Pman Run"
    state = False
if threshold > success_pman_status:
    msg += ", Pman Status"
    state = False
if threshold > success_pfioh_pull:
    msg += ", Pfioh Pull"

if state==False:
    msg = msg[2:]
    with open("export.sh", "w+") as file:
        file.write('export error="' + msg + '"')

