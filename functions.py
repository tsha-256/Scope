# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 18:11:06 2018

@author: chentir
"""
import pyvisa as visa
import time
import TeledyneLeCroyPy
global TSL
global scope
scope = TeledyneLeCroyPy.LeCroyWaveRunner('USB0::0x05ff::0x1023::4609N02990::INSTR')
rm=visa.ResourceManager()
listing=rm.list_resources()
tools=[i for i in listing if 'GPIB' in i]
for i in tools:
    buffer=rm.open_resource(i, read_termination='\r\n')
    if 'TSL' in buffer.query('*IDN?'):
        TSL= buffer
Ini_Cond={
        'POW:STAT ':'0','POW:SHUT ':'0','POW:ATT:AUT ':'1','POW:UNIT ':'0','WAV:UNIT ':'0',
        'TRIG:INP:EXT ':'0','TRIG:OUTP ':'2','WAV:SWE:MOD ':'1',
        'SYST:COMM:GPIB:DEL ':'2','COHC ':'0','AM:STAT ':'0'
        }
Use_Cond={
        'POW:STAT ':'','POW:SHUT ':'','POW:ATT:AUT ':'','POW:UNIT ':'','WAV:UNIT ':'',
        'TRIG:INP:EXT ':'','TRIG:OUTP ':'','WAV:SWE:MOD ':'',
        'SYST:COMM:GPIB:DEL ':'','COHC ':'','AM:STAT ':''
        }



def Ini():
    TSL.write('*CLS')
    TSL.write('*RST')
    for i,j in zip(Ini_Cond.keys(),Ini_Cond.values()):
        TSL.write(i+j)
    if '550' in TSL.query('*IDN?') or '710' in TSL.query('*IDN?'):
        TSL.write('GC 1')
    else:
        TSL.write('SYST:COMM:COD 0')
    try:
        scope.set_trig_source("Ext")
        scope.set_trig_slope("Ext", "Either")
    except:
        pass

def setTrigSource(source):
    scope.set_trig_source(source)

def setTrigSlope(source, slope):
    scope.set_trig_slope(source, slope)

def setTrigMode(mode):
    scope.set_trig_mode(mode)

def setTdiv(tdiv):
    scope.set_tdiv(tdiv)

def setTrigDelay(delay):
    scope.set_trig_delay(delay)

def setVdiv(channel, vdiv):
    scope.set_vdiv(channel, vdiv)

def sidn():
    print(scope.idn())

def storeData(channel, fname):
    rawData = scope.get_waveform(n_channel=channel)
    data = rawData['waveforms'][0]
    te = data['Time (s)']
    ve = data[f'Amplitude (V)']
    with open(fname, "w") as file:
        for i,j in zip(te, ve):
            file.write(f"{i}, {j}\n") #TODO End of modifications

def calcTime(stopTime):
    time_to_tdiv = {0.00000001:'1NS',0.00000002:'2NS',0.00000005:'5NS',0.0000001:'10NS',0.0000002:'20NS',0.0000005:'50NS',0.000001:'100NS',0.000002:'200NS',0.000005:'500NS',0.00001:'1US',0.00002:'2US',0.00005:'5US',0.0001:'10US',0.0002:'20US',0.0005:'50US',0.001:'100US',0.002:'200US',0.005:'500US',0.01:'1MS',0.02:'2MS',0.05:'5MS',0.1:'10MS',0.2:'20MS',0.5:'50MS',1:'100MS',2:'200MS',5:'500MS',10:'1S',20:'2S',50:'5S',100:'10S',200:'20S',500:'50S',1000:'100S'}
    tdiv = '100S'
    oTime = 1000
    for i in time_to_tdiv:
        if stopTime <= i:
            tdiv = time_to_tdiv[i]
            oTime = i
            break
    return tdiv, oTime

def SetWL(WL):
    TSL.write('WAV ', str(WL))
    while True:
        check=TSL.query("*opc?")
        if check=='0':
            time.sleep (0.1)
        else:
            GetWL()
            break        

def GetWL():
    return TSL.query('WAV?')
    
def SetPwr(Pwr): 
    if Pwr>13:
        Pwr=13
    elif Pwr<-14:
        Pwr=-14
    TSL.write('POW ', str(Pwr))

    while True:
        check=TSL.query("*opc?")
        if check=='0':
            time.sleep (0.1)
        else:
            GetPwr()                          
            break
  
def GetPwr():
    return TSL.query('POW:ACT?')

def SetAtt(Att):
    if Att>30:
        Att=30
    elif Att<0:
        Att=0
    TSL.write('POW:ATT ', str(Att))
    while True:
        check=TSL.query("*opc?")
        if check=='0':
            time.sleep (0.1)
        else:
            GetAtt()
            GetPwr()
            break
  
def GetAtt():
    return TSL.query('POW:ATT?')

def Auto_Start(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle,File,channel):
    stopTime = (int(WLend)-int(WLstart))/int(Arg1)
    tdiv, oTime = calcTime(stopTime)
    scope.set_tdiv(tdiv)
    scope.set_trig_delay(oTime/2)
    try:
        open(File, 'a')
    except:
        print("Path error")
        return
    TSL.write('POW:STAT 1')
    TSL.write('TRIG:INP:STAN 0')
    scope.set_trig_mode("NORM") #TODO Normal or Single?
    Scan(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle)
    print("Scan function called") #TODO Remove after testing
    time.sleep(stopTime) #TODO might need to be put into Scan
    TSL.write('POW:STAT 0')
    scope.set_trig_mode("STOP")
    storeData(channel, File)

def Trig_Start(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle):
    TSL.write('TRIG:INP:STAN 1')
    Scan(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle)

def Scan(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle):
    TSL.write('WAV:SWE:MOD '+str(Swp_mod))
    TSL.write('WAV:SWE:STAR '+str(WLstart))
    TSL.write('WAV:SWE:STOP '+str(WLend))
    if str(Cycle)!='':
        TSL.write('WAV:SWE:REP')
        TSL.write('WAV:SWE:CYCL '+str(Cycle))
        
    if Swp_mod==1 or Swp_mod==3:                                                #if Continuous scan modes (one way or two ways) areselected, Arg1 and Arg2 = Scan speed, trigger output step
        TSL.write('WAV:SWE:SPE '+str(Arg1))
        TSL.write('TRIG:OUTP:STEP '+str(Arg2))
        TSL.write('WAV:SWE:STAT 1')
        check=TSL.query('WAV:SWE?')
        while True:
            if check!='3':
                check=TSL.query('WAV:SWE?')
                time.sleep(0.1)
            else:
                TSL.write('WAV:SWE:SOFT')
                break
            break
    elif Swp_mod==0 or Swp_mod==2:
        TSL.write('WAV:SWE:STEP '+str(Arg1))
        TSL.write('WAV:SWE:DWEL '+str(Arg2))
        TSL.write('WAV:SWE:STAT 1')
        if Swp_mod == 0:
          check=TSL.query('WAV:SWE?')
        while True:
            if check!='3':
                check=TSL.query('WAV:SWE?')
                time.sleep(0.1)
            else:
                TSL.write('WAV:SWE:SOFT')
                break
            break

def Del_change(delimiter):
    TSL.write('SYST:COMM:GPIB:DEL '+str(delimiter)) 

def TrigSrc(Trigg):
    TSL.write('TRIG:INP:EXT '+str(Trigg))    

def TrigMode(Mode):
    TSL.write('TRIG:OUTP '+str(Mode))
