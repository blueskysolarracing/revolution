#!/bin/bash

systemctl stop \
	revolution@database \
	revolution@replica \
	revolution@hardware \
	revolution@display
