#!/usr/bin/env python -u
import moc_health_check
import os
import time
health_check = moc_health_check.Health_Checker() # instantiating health checker object 

success_pfioh_push = 0                               # Success rate of pfioh_push
success_pman_run = 0                               # Success rate of pman_run
success_pman_status = 0                               # Success rate of pman_status
success_pfioh_pull = 0                               # Success rate of pfioh_pull
RANGE = int(health_check.get_range())
THRESHOLD = int(health_check.get_threshold())

for x in range(1, RANGE + 1):
    print("Iteration " + str(x))
    print("_________________")

    if health_check.verify(health_check.run_pfioh_push()): # verify that Pfioh Push works
        success_pfioh_push += 1
        if health_check.verify(health_check.pman_run()): # Verify that Pman run works

            success_pman_run += 1
            for y in range(1,5):
                if health_check.verify(health_check.run_pman_status()): # verify that job runs properly
                    success_pman_status += 1
                    break
                time.sleep(health_check.backoff(y,100))
                
            if health_check.verify(health_check.run_pman_status()) : # verify that pfio pull works
                if health_check.verify(health_check.run_pfioh_pull()) :
                    success_pfioh_pull += 1
                    health_check.job_delete()
                else :
                    health_check.log_error("moc-health-check/error.log", health_check.run_pfioh_pull())
                    health_check.job_delete()
            else :
                health_check.log_error("moc-health-check/error.log", health_check.run_pman_status())
                health_check.job_delete()
        else :
            health_check.log_error("moc-health-check/error.log", health_check.pman_run())
            health_check.job_delete()
    else:
        health_check.log_error("moc-health-check/error.log", health_check.run_pfioh_push())


<<<<<<< HEAD

=======
    
>>>>>>> c0df3c6... made changes
=======
>>>>>>> cc44746... Update automate.py
# Calculating success rate
success_pfioh_push = int((success_pfioh_push/RANGE)*100)
success_pman_run = int((success_pman_run/RANGE)*100)
success_pman_status = int((success_pman_status/RANGE)*100)
success_pfioh_pull = int((success_pfioh_pull/RANGE)*100)
threshold = int(THRESHOLD) 

# compiling errors in framework to an environment variable
status,msg = health_check.conditionals(threshold,success_pfioh_push,success_pfioh_pull,success_pman_status,success_pman_run)
health_check.finale(status, msg)
