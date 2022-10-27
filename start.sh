#!/bin/bash

systemctl start \
	revolution@syncer \
	revolution@display_driver \
	revolution@miscellaneous_controller \
	revolution@motor_controller \
	revolution@power_sensor \
	revolution@replica \
	revolution@telemeter \
	revolution@voltage_controller
