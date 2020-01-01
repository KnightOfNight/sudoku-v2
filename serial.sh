#!/bin/bash

secs=$(date +%s)
printf "%.9f" $(echo "$secs/1000000000" | bc -l)
