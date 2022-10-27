#!/bin/bash

sed "s?{{ project_path }}?`pwd`?g" revolution@.service > /etc/systemd/system/revolution@.service
