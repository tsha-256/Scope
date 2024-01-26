# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 18:11:06 2018

@author: chentir
"""
import pyvisa as visa
import time
global TSL
global Scope
rm=visa.ResourceManager()
listing=rm.list_resources()
tools=[i for i in listing if 'GPIB' in i]
for i in tools:
    buffer=rm.open_resource(i, read_termination='\r\n')
    if 'TSL' in buffer.query('*IDN?'):
        TSL= buffer
    if 'ANDO' in buffer.query('*IDN?'):
        Scope= buffer
Ini_Cond={
        'POW:STAT ':'1','POW:SHUT ':'0','POW:ATT:AUT ':'1','POW:UNIT ':'0','WAV:UNIT ':'0',
        'TRIG:INP:EXT ':'0','TRIG:OUTP ':'3','WAV:SWE:MOD ':'1',
        'SYST:COMM:GPIB:DEL ':'2','COHC ':'0','AM:STAT ':'0'
        }
Use_Cond={
        'POW:STAT ':'','POW:SHUT ':'','POW:ATT:AUT ':'','POW:UNIT ':'','WAV:UNIT ':'',
        'TRIG:INP:EXT ':'','TRIG:OUTP ':'','WAV:SWE:MOD ':'',
        'SYST:COMM:GPIB:DEL ':'','COHC ':'','AM:STAT ':''
        }

Scope_Cond= [
        'STAWL****.**', 'STPWL****.**', 'RESLN*.**', 'REFL***.*', 'LSCL**.*', 'AVG****', 'SMPL****',
          'WRTA', 'DSPA', 'FIXB', 'BLKB', 'FIXC', 'BLKC'  # TODO HAS TO BE CONFIGURED, SMPL prob 0
]


def Ini():
    TSL.write('*CLS')
    TSL.write('*RST')
    Scope.write('*RST') # TODO Not sure if necessary; will reset all settings
    for i,j in zip(Ini_Cond.keys(),Ini_Cond.values()):
        TSL.write(i+j)
    if '550' in TSL.query('*IDN?') or '710' in TSL.query('*IDN?'):
        TSL.write('GC 1')
    else:
        TSL.write('SYST:COMM:COD 0')
    for i in Scope_Cond:
        Scope.write(i)

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

def Auto_Start(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle):
    TSL.write('TRIG:INP:STAN 0')
    Scan(Swp_mod,WLstart,WLend,Arg1,Arg2,Cycle)
    data = ReadData() # Function modifications start here
    ct = time.ctime(time.time()).split()
    fn = "data_" + WLstart + "_" + WLend + "_" + ct[1] + "_" + ct[2] + "_" + ct[3][0:5] + ".txt"
    with open("data.txt", "w") as file: # TODO CHANGE FILE NAME
        for i in data:
            file.write(i + "\n")

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
        Scope.write('AUTO') # TODO Might be RPT? not sure
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
            Scope.write('SGL') # TODO Modified code to start scan
        elif Swp_mod == 2: #
            Scope.write('RPT') #
        check=TSL.query('WAV:SWE?') #
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

def ReadData():
    Scope.write('SD0')
    Scope.write('BD0')
    data = Scope.query('LDATA') # TODO Might be WDATA
    if data[0] == " ":
        data = data[1:]

    data = data.split(',')
    return data
