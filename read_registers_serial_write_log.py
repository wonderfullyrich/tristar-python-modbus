#!/usr/bin/env python

# Based on Morningstar documentation here
# http://www.morningstarcorp.com/wp-content/uploads/2014/02/TSMPPT.APP_.Modbus.EN_.10.2.pdf
# and heavily modified version of the script here
# http://www.fieldlines.com/index.php?topic=147639.0

# This is modified for the non-MPPT tri-stars without built-in network monitoring. It has different indices and different available data.

import sys
import re
import time
import io
from datetime import datetime, date, timedelta
counter = 0

script = sys.argv[0]
host = re.sub(r".*tristar_monitoring_",'',script)

if len(sys.argv) == 2:
    if sys.argv[1] == "config":
#        print "host_name %s" % host
        print "graph_category power"
       	print "graph_title Solar Charge Controller Info"
	print "graph_vlabel A bit of all (V, A, C)"
	print "vPanel.label panel potential (V)"
	print "vPanel.max   80"
	print "vBattTerm.label battery potential at terminals (V)"
        print "vBattTerm.max 32"
        print "vBattTerm.warning 25:32"
        print "vBattTerm.critical 24:33"
#	print "vBattSense.label battery potential sensing (V)"
#	print "vBattSense.max 32"
	print "hsTemp.label heat sink temperature (C)"
	print "hsTemp.max 120"
        print "hsTemp.warning :60"
        print "hsTemp.critical :80"
	# print "battTemp.label battery temperature (C)"
	# print "battTemp.max 120"
        # print "battTemp.warning :80"
        # print "battTemp.critical :100"
	print "aPanel.label charge current (A)"
	print "aPanel.max 20"
#        print "aPanel.warning :15"
#        print "aPanel.critical :19"
#	print "aBatt.label battery current (A)"
#	print "aBatt.max 20"
#        print "aBatt.warning :15"
#        print "aBatt.critical :19"
        exit(0)
# import the server implementation
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger('./modbus.error')
log.setLevel(logging.ERROR)

client = ModbusClient(method='rtu',port='/dev/ttyUSB0', baudrate=9600, timeout=1)
client.connect()
log.debug(client)

# Define the State list
state = ['Start', 'Night Check', 'Disconnected', 'Night', 'Fault!', 'MPPT', 'Absorption', 'FloatCharge', 'Equalizing', 'Slave']

# Define the Alarm list
alarm = ['RTS open', 'RTS shorted', 'RTS disconnected']

# read registers. Start at 0 for convenience
rr = client.read_holding_registers(0,80,unit=1)
if rr == None:
    client.close()
    log.error("couldn't connect")
    exit(1)
client.connect()
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
rtsTempF = (rtsTemp*9/5)+ 32
timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


logfilename = time.strftime("%Y-%m-%d")
file = open('/home/pi/Desktop/powersystem-logfiles/' + logfilename + '.log', 'a+')
file.write( "%s\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (datetime.now(), host, battsV, battsSensedV, battsI, battsV*battsI, arrayV, arrayI, arrayV*arrayI, hsTemp, rtsTemp, rr.registers[50], state[statenum], outPower, inPower, minVb_daily, maxVb_daily, whc_daily, minTb_daily, maxTb_daily, ahc_daily, whc_daily, Pout_max_daily, minTb_daily, maxTb_daily, time_ab_daily, time_eq_daily, time_fl_daily, faults_daily, alarm_daily_HI, alarm_daily_LO, hourmeterHI, hourmeterLO, adc_ib_f_1m))
file.close()

# Oneliner output tab deliniated"
file = open('/home/pi/Desktop/powersystem-logfiles/plotdailylog' + logfilename + '.log', 'a+')
# file.write( "%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (time.strftime("%H:%M:%S"), battsV, arrayV, adc_ib_f_1m, hsTemp, rtsTemp, outPower, ahc_daily)
#file.write( "%f\t%f\t%f\n" % (datetime.now(), adc_ib_f_1m, rtsTemp))
file.write( "%s\t%f\t%f\t%f\t%f\t%f\n" % (datetime.now(), rtsTempF, outPower, maxVb_daily, minVb_daily, battsSensedV))
file.close()

html_str_part1 = """
<table border=1>
         <tr>
           <th>Power</th>
           <th>Description</th>
         </tr>
         <indent>
           <tr>
"""
html_str_part2 = """
          </tr>
         </indent>
</table>
"""


Html_file= open("/var/www/html/index.html","w")
Html_file.write("         <b>Time</b>: %s " % timestamp)
Html_file.write(html_str_part1)
#Html_file.write("         <td>Time</td> \n\r          <td>%f W</td>" % (time.strftime("%H:%M:%S"))
Html_file.write("         <td>%.1f W</td> \n\r          <td>Current Panel Watts to battery</td>\n\r          </tr>" % outPower)
Html_file.write("         <td>%s</td> \n\r          <td>Charge Controller status</td>\n\r          </tr>" % state[statenum])
Html_file.write("         <td>%.1f W/H</td> \n\r          <td>Daily Watts so far</td>\n\r          </tr>" % ahc_daily)
Html_file.write("         <td>%.1f V</td> \n\r          <td>Battery sense voltage</td>\n\r          </tr>" % battsSensedV)
Html_file.write("         <td>%.1f V</td> \n\r          <td>Minimum battery voltage today</td>\n\r          </tr>" % minVb_daily)
Html_file.write("         <td>%.1f V</td> \n\r          <td>Maximum battery voltage today</td>\n\r          </tr>" % maxVb_daily)
Html_file.write("         <td>%.1f F</td> \n\r          <td>Battery Temperature</td>\n\r          </tr>" % rtsTempF)
#Html_file.write("         <td colspan=2><img src=/var/www/html/daily.png /></td>\n\r          </tr>")
Html_file.write(html_str_part2)
Html_file.close()

client.close()
