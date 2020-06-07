#!/bin/bash

source ~/.anaconda3/etc/profile.d/conda.sh 
conda activate sapevo;
docker-compose up -d;
./manage.py runserver

