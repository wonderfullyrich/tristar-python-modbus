#!/usr/bin/env python

# Based on Morningstar documentation here
# http://www.morningstarcorp.com/wp-content/uploads/2014/02/TSMPPT.APP_.Modbus.EN_.10.2.pdf
# and heavily modified version of the script here
# http://www.fieldlines.com/index.php?topic=147639.0

import time
import io
counter = 0

import sys

if len(sys.argv) <= 1:
    print "Usage: read_registers.py <ip address 1> [ip address 2] ..."
    exit(1)

hosts = sys.argv[1:]

# import the server implementation
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger('./modbus.error')
log.setLevel(logging.ERROR)

for host in hosts:
# print "Host %s" % host
 client = ModbusClient(host,502)
 client.connect()

# Define the State list
 state = ['Start', 'Night Check', 'Disconnected', 'Night', 'Fault!', 'MPPT', 'Absorption', 'FloatCharge', 'Equalizing', 'Slave']

# Define the Alarm list
 alarm = ['RTS open', 'RTS shorted', 'RTS disconnected']

# read registers. Start at 0 for convenience
 rr = client.read_holding_registers(0,80,unit=1)

# for all indexes, subtract 1 from what's in the manual
 V_PU_hi = rr.registers[0]
 V_PU_lo = rr.registers[1]
 I_PU_hi = rr.registers[2]
 I_PU_lo = rr.registers[3]

 V_PU = float(V_PU_hi) + float(V_PU_lo)
 I_PU = float(I_PU_hi) + float(I_PU_lo)

 v_scale = V_PU * 2**(-15)
 i_scale = I_PU * 2**(-15)
 p_scale = V_PU * I_PU * 2**(-17)

# battery sense voltage, filtered
 battsV = rr.registers[24] * v_scale
 battsSensedV = rr.registers[26] * v_scale
 battsI = rr.registers[28] * i_scale
 arrayV = rr.registers[27] * v_scale
 arrayI = rr.registers[29] * i_scale
 statenum = rr.registers[50]
 hsTemp = rr.registers[35] 
 rtsTemp = rr.registers[36]
 adc_ib_f_1m = rr.registers[39] * i_scale
 hourmeterHI = rr.registers[42]
 hourmeterLO = rr.registers[43]
 outPower = rr.registers[58] * p_scale
 inPower = rr.registers[59] * p_scale
 minVb_daily = rr.registers[64] * v_scale
 maxVb_daily = rr.registers[65] * v_scale
 ahc_daily = rr.registers[67]
 whc_daily = rr.registers[68]
 Pout_max_daily = rr.registers[70]
 minTb_daily = rr.registers[71]
 maxTb_daily = rr.registers[72]
 time_ab_daily = rr.registers[77]
 time_eq_daily = rr.registers[77]
 time_fl_daily = rr.registers[78]
 dipswitches = bin(rr.registers[48])[::-1][:-2].zfill(8)
 faults_daily = rr.registers[74]
 alarm_daily_HI = rr.registers[75]
 alarm_daily_LO = rr.registers[76]
# alarm_HI = rr.registers[46]
# alarm_LO = rr.registers[47]
# led_state = rr.registers[49]

 logfilename = time.strftime("%Y-%m-%d")
 file = open('/home/pi/Desktop/powersystem-logfiles/' + logfilename + '.log', 'a+')
 file.write( "%s\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (time.strftime("%Y-%m-%d\t%H:%M:%S\t%Z"), host, battsV, battsSensedV, battsI, battsV*battsI, arrayV, arrayI, arrayV*arrayI, hsTemp, rtsTemp, rr.registers[50], state[statenum], outPower, inPower, minVb_daily, maxVb_daily, whc_daily, minTb_daily, maxTb_daily, ahc_daily, whc_daily, Pout_max_daily, minTb_daily, maxTb_daily, time_ab_daily, time_eq_daily, time_fl_daily, faults_daily, alarm_daily_HI, alarm_daily_LO, hourmeterHI, hourmeterLO, adc_ib_f_1m))
 file.close()

 # Write minimal items to a separated log file with linux date/time for future pylab plotting.
 file = open('/home/pi/Desktop/powersystem-logfiles/plotdailylog' + logfilename + '.log', 'a+')
 file.write( "%f\t%f\t%f\n" % (time.time(), adc_ib_f_1m, rtsTemp))
 file.close()

 client.close()
