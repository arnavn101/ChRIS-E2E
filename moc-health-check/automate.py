#!/usr/bin/env python3
import moc_health_check
import os
import time




health_check = moc_health_check.Health_Checker() # Instantiating health checker object 

# Retrieving key variables form moc-health-check object
RANGE = int(health_check.get_range())
THRESHOLD = int(health_check.get_threshold())
# Finding success rate of each aspect of ChRIS Framework
success_pfioh_push, success_pman_run, success_pman_status, success_pfioh_pull = health_check.prog_flow(RANGE, 2, "moc-health-check/error.log",1,0,0,0,0)

print("-----------------------------------------------")
print("------------ Calculating success rate ---------")
print("-----------------------------------------------")
# Calculating success rate
success_pfioh_push = int((success_pfioh_push/RANGE)*100)
success_pman_run = int((success_pman_run/RANGE)*100)
success_pman_status = int((success_pman_status/RANGE)*100)
success_pfioh_pull = int((success_pfioh_pull/RANGE)*100)
threshold = int(THRESHOLD) 

# Compares success rate with threshold
status, msg = health_check.conditionals(threshold, success_pfioh_push, success_pfioh_pull, success_pman_status, success_pman_run)
print("-----------------------------------------------")
print("------------- STATUS --------------------------")
print(status)
print("-----------------------------------------------")
print("------------- MESSAGE --------------------------")
# Compiling errors to an environment variable
health_check.env_write(status, msg)
print(msg)
if status == False:
    print("Healthcheck failed. Exceeding backoff limits.")
    raise Exception



