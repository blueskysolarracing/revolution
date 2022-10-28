#!/bin/bash

sed "s/{{ username }}/`who am i | awk '{print $1}'`/g; s?{{ project_path }}?`pwd`?g" revolution@.service > /etc/systemd/system/revolution@.service
