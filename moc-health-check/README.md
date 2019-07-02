# MOC Health Reporter - v1.0

********
***Overview***
********

This repository provides a real-world application for pfurl project. It sends a generic command from pfurl to send local files to Pfioh, run a sample job on pman, and fetch the files back from pfioh. Overall, it tests all of the core elements of Chris Platform with the requirement of only one job id, making the process reentrant. 


- ``MOC Status Reporter``: a program to test the functionality of MOC 

MOC Health Reporter
=====

``MOC Health Reporter`` is a plugin for pfurl utility, since it successfully utilizes pfurl as a testing service for ChRIS Research Integration System.

In simple terms, ``MOC Health Reporter`` is a status fetcher used to send http-based messages to remote services such as ``pman`` and ``pfioh``, in order to test their reliability and response time. 

It also posseses the capability to run in a containerized atmosphere, requiring no external communication with other modules. 

************
Installation
************

Installation is easy on Linux environments with python 

Python Environments
==========================

On any Linux OS, clone this repository and change arguments of config.cfg

      vim config.cfg

Edit the recipients.txt as per your requirements

      vim recipients.txt

Install requirements of Python

     ./install.sh
     
Run the program 
     
     python3 automate.py


Buddy CI (https://buddy.works/)
===============================

First, fork this repository and edit the .yml file as per your requirements. Additionaly, sign up for Buddy with your email or github. Then click on ``Create new Project`` and ``Attach Existing Github project``. Click on ChRIS-E2E and import option in project. Browse to directory with moc-health-file and select the .yml file. Then, click on build and go to variables tab. Click on ``Add a new variable`` option, and input error for key and error for value. Lastly, change the type to Settable. The program would now run continuously with its given time frame. 


