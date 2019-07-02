#!/usr/bin/env python -u
import os, sys
import configparser
from subprocess import Popen, PIPE
import test_setup
import subprocess
import time
import logging
import pfurl
import json

class Health_Checker:
    # defining all of required variables
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('moc-health-check/config.cfg')
        self.RANGE = config.get('ConfigInfo', 'RANGE')
        self.SIZE = config.get('ConfigInfo', 'SIZE')
        self.TIMEOUT = config.get('ConfigInfo', 'TIMEOUT')
        self.THRESHOLD = config.get('ConfigInfo', 'THRESHOLD')
        self.PATH = os.getcwd()
        self.WAIT = int(config.get('ConfigInfo', 'WAIT'))
        self.PMAN_URL = config.get('ConfigInfo', 'PMAN_URL')
        self.PFIOH_URL = config.get('ConfigInfo', 'PFIOH_URL')
        self.JID = config.get('ConfigInfo', 'JID')

        # Creating sample files
        test_setup.check() 

        # Reentrancy testing
        self.check_job_status()

        """ Log File Reentrancy
        last_cmd = self.last_line("program.log","root:")

        if(self.reentrancy(last_cmd.strip(), "job_delete")):
            self.job_delete()
        """

        # Erasing contents of error log file & program log file
        self.erase('moc-health-check/error.log', "\n")
        self.job_delete()


    # accessor methods
    def get_range(self):
        return self.RANGE
    
    def get_threshold(self):
        return self.THRESHOLD

    # delete a pman job
    def job_delete(self):
        data = {   "action": "delete",
            "meta":  {
                "key":"jid",
                "value": '"' + self.JID + '"'
            }
        }

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(data),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PMAN_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = "password"
        )

        d_dataComs = dataComs()
        return d_dataComs
    
    # upload data to swift 
    def run_pfioh_push(self):
        data = { "action":"pushPath",
        "meta": {
            "remote": {
                "key":        self.JID 
                },
            "local": {
                "path":        "/tmp/" + self.SIZE
                },
            "transport": {
                "mechanism":   "compress",
                "compress": {
                    "archive": "zip",
                    "unpack":   True,
                    "cleanup":  True
                    }
                }
            }
        }
        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(data),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (str(self.PFIOH_URL), "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = "password"
        )
        print(dataComs())
        return dataComs()
    
    # sets exponential backoff
    def backoff(self, attempt, max_value):
        return min(max_value,self.WAIT * 2 ** attempt)


    # run a job in Pman
    def pman_run(self):
        data = {   "action": "run",
            "meta":  {
                "cmd": "simpledsapp.py --prefix test- --sleepLength 0 /share/incoming /share/outgoing",
                "auid": "rudolphpienaar",
                "jid": '"' + self.JID + '"',
                "threaded": True,
                "container": {
                        "target": {
                            "image": "fnndsc/pl-simpledsapp"
                        }
                }
            }
        }

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(data),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PMAN_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = "password"
        )
        print(dataComs())
        return dataComs()


    # check status of job in Pman
    def run_pman_status(self):
        data = {   "action": "status",
            "meta":  {
                "key":"jid",
                "value": '"' + self.JID + '"'
            }
        }

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(data),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PMAN_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = "password"
        )
        print(dataComs())

        return dataComs()

    # downlad data from swift
    def run_pfioh_pull(self):
        data = {"action": "pullPath",
    "meta": {
        "remote": {
            "key":         '"' + self.JID + '"'
        },
        "local": {
            "path":         "/tmp/" + self.SIZE,
            "createDir":    True
        },
        "transport": {
            "mechanism":    "compress",
            "compress": {
                "archive":  "zip",
                "unpack":   True,
                "cleanup":  True
            }
        }
    }}

        dataComs = pfurl.Pfurl(
                    msg                         = json.dumps(data),
                    verb                        = 'POST',
                    http                        = '%s/%s' % (self.PFIOH_URL, "api/v1/cmd"),
                    b_quiet                     = False,
                    b_raw                       = True,
                    b_httpResponseBodyParse     = True,
                    jsonwrapper                 = '',
                    authToken                   = "password"
        )
        print(dataComs())

        return dataComs()
    
    # check if success rate is above threshold
    def conditionals(self,threshold,success_pfioh_push,success_pfioh_pull,success_pman_status,success_pman_run):
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
        return state, msg
    
    # create reentrancy by maintaining logs of program
    def debugger(self,service):
        logging.basicConfig(filename='program.log',level=logging.DEBUG)
        logging.debug(service)
    
    # check if commands executed properly
    def verify(self,result):
        if '"status": true' in result or '"status": finished' in result:
            return True
        return False

    # open a file and write to it
    def export(self, msg, file_name):
        with open(file_name, "w+") as file:
            file.write("env.DB_URL=" + '"' + msg + '"')

    # if error persists in MOC, write env variables to bash file
    def finale(self,state, msg):
        if state==False:
            msg = msg[2:]
            self.export(msg, 'test.groovy')
            raise Exception
        
    # get last line of log file
    def last_line(self, file_name, key):
        f_read = open(file_name, "r")
        line = f_read.readlines()[-1]
        line = line.split(key,1)[1] 
        return line
    
    # check if program executed properly in previous run
    def reentrancy(self,last_cmd, end_cmd):
        if last_cmd != end_cmd:
            return True
    
    # delete contents of log file and replace it with one line
    def erase(self, file_name,line):
       with open(file_name, "w+") as file:
        file.write(line)

    def log_error(self,file_name, error):
        with open(file_name, "w") as file:
            file.write(error)

    def job_execution(self, output):
        if '"status" : started' in output:
            return True
            
    def check_job_status(self):
        if self.verify(self.run_pman_status()) or self.job_execution(self.run_pman_status()):
            self.job_delete()
