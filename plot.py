import pylab
import time
import os
from matplotlib import dates
import datetime


os.environ["DISPLAY"] = ":0.0"

plotdailylogfilename = '/home/pi/Desktop/powersystem-logfiles/' + time.strftime("%Y-%m-%d") + '.log'
#dt=pylab.dtype([('f0','datetime64[ms]'),('f1',str,(2)),('f2',float,(5))])
dt=pylab.dtype([('f0','datetime64[ms]'),('s1',str,(15)),('f2',float,(1)),('f3',float,(1)),('f4',float,(1)),('f5',float,(1)),('f6',float,(1)),('f7',float,(1)),('f8',float,(1)),('f9',float,(1)),('f10',float,(1)),('f11',float,(1)),('s12',str,(15)),('f13',float,(1)),('f14',float,(1)),('f15',float,(1)),('f16',float,(1)),('f17',float,(1)),('f19',float,(1)),('f20',float,(1)),('f21',float,(1)),('f22',float,(1)),('f23',float,(1)),('f24',float,(1)),('f25',float,(1)),('f26',float,(1)),('f27',float,(1)),('f28',float,(1)),('f29',float,(1)),('f30',float,(1)),('f31',float,(1)),('f32',float,(1)),('f33',float,(1)),('f34',float,(1))])
data = pylab.genfromtxt(plotdailylogfilename,dtype=dt,delimiter='\t')

pylab.plot( data['f0'], data['f2'], label="Output")
pylab.plot( data['f0'], data['f3'], label="Battery")
pylab.legend()
pylab.title("Charge Data for " + time.strftime("%Y-%m-%d"))
pylab.xlabel("Time")
pylab.ylabel("Voltage: \n")
pylab.savefig("/var/www/html/voltagegraph.png")
pylab.clf()

pylab.plot( data['f0'], data['f21'], label="Amp")
pylab.plot( data['f0'], data['f22'], label="Watts")
pylab.legend()
pylab.title("Charge Data for " + time.strftime("%Y-%m-%d"))
pylab.xlabel("Time")
pylab.ylabel("Charge")
pylab.legend(loc='lower left')
pylab.savefig("/var/www/html/whcgraph.png")
pylab.clf()

pylab.plot( data['f0'], data['f9'], label="Heat Sink")
pylab.plot( data['f0'], data['f10'], label="Battery")
pylab.legend()
pylab.title("Charge Data for " + time.strftime("%Y-%m-%d"))
pylab.xlabel("Time")
pylab.ylabel("Temperature")
pylab.legend(loc='best')
pylab.savefig("/var/www/html/tempgraph.png")
pylab.clf()

pylab.plot( data['f0'], data['f15'], label="Min")
pylab.plot( data['f0'], data['f16'], label="Max")
pylab.legend()
pylab.title("Charge Data for " + time.strftime("%Y-%m-%d"))
pylab.xlabel("Time")
pylab.ylabel("Voltage")
pylab.legend(loc='best')
pylab.savefig("/var/www/html/voltminmaxgraph.png")
pylab.clf()

pylab.plot( data['f0'], data['f13'], label="Watts")
pylab.legend()
pylab.title("Charge Data for " + time.strftime("%Y-%m-%d"))
pylab.xlabel("Time")
pylab.ylabel("Output")
pylab.legend(loc='best')
pylab.savefig("/var/www/html/inputoutputgraph.png")
pylab.clf()

pylab.plot( data['f0'], data['f26'], label="Absorb")
pylab.legend()
pylab.title("Charge Data for " + time.strftime("%Y-%m-%d"))
pylab.xlabel("Time")
pylab.ylabel("Level")
#hfmt = dates.DateFormatter('%m/%d %H:%M')
#ax.xaxis.set_major_locator(dates.MinuteLocator())
#ax.xaxis.set_major_formatter(hfmt)
pylab.gcf().autofmt_xdate()
pylab.legend(loc='best')
pylab.savefig("/var/www/html/absorbgraph.png")
pylab.clf()

