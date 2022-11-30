#!/bin/bash

systemctl start \
	revolution@database \
	revolution@replica \
	revolution@hardware \
	revolution@display
