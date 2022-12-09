#!/bin/bash

systemctl start \
	revolution@database \
	revolution@replica \
	revolution@controller \
	revolution@display
