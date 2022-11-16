#!/bin/bash

PROJECT_PATH=$(realpath $(dirname ${BASH_SOURCE[0]}))

sed "s/{{ username }}/`who am i | awk '{print $1}'`/g; s?{{ project_path }}?$PROJECT_PATH?g" $PROJECT_PATH/revolution@.service > /etc/systemd/system/revolution@.service
