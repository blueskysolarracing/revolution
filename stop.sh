#!/bin/bash

PROJECT_PATH=$(realpath $(dirname ${BASH_SOURCE[0]}))

systemctl stop \
	revolution@marshal \
	revolution@display_driver \
	revolution@miscellaneous_controller \
	revolution@motor_controller \
	revolution@power_sensor \
	revolution@replica \
	revolution@telemeter \
	revolution@voltage_controller

$PROJECT_PATH/src/unlinker
