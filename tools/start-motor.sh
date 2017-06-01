#!/bin/bash

echo 0 > /sys/class/pwm/pwm3/duty_ns
echo 0 > /sys/class/pwm/pwm4/duty_ns
echo 0 > /sys/class/pwm/pwm5/duty_ns
echo 0 > /sys/class/pwm/pwm6/duty_ns

echo 0 > /sys/class/pwm/pwm3/run
echo 0 > /sys/class/pwm/pwm4/run
echo 0 > /sys/class/pwm/pwm5/run
echo 0 > /sys/class/pwm/pwm6/run

echo 20000000 > /sys/class/pwm/pwm3/period_ns
echo 20000000 > /sys/class/pwm/pwm4/period_ns
echo 20000000 > /sys/class/pwm/pwm5/period_ns
echo 20000000 > /sys/class/pwm/pwm6/period_ns

echo 1 > /sys/class/pwm/pwm3/run
echo 1 > /sys/class/pwm/pwm4/run
echo 1 > /sys/class/pwm/pwm5/run
echo 1 > /sys/class/pwm/pwm6/run
