#!/bin/bash
# Multiple ways to count up to 10.

echo

# for loop over packet sizes
for size in 50 250 500 750 1000 1250 1500
do
	# account for 8 bytes ICMP header and 20 bytes IPv4 header
	let "realsize = size - 8 - 20"
	echo "ping -s $realsize -c 50 -i 1 $1 > $1-p$size"
	# call ping (100 packets) and write to file
	ping -s $realsize -c 50 -i 1 $1 > $1-p$size
done  

echo; echo
