import pyvisa as visa
import time
import TeledyneLeCroyPy
import functions

if __name__ == "__main__":
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

    functions.Ini()
    base_cmd = """Enter the command you want to execute:
tsl     - Manage TSL parameters
scope   - Manage oscilloscope parameters
sweep   - Run a sweep of the TSL
exit    - Exit this program
"""
    tsl_cmd = """Enter the command you want to execute:
idn     - Get the identification of the TSL
def     - Resets to default parameters
onoff   - Turn the laser on or off
            - 0: Off
            - 1: On
pow     - Set or get the laser power in dBm
            - ?: Get the power
            - <value>: Set the power
wav     - Set or get the laser wavelength in nm
            - ?: Get the wavelength
            - <value>: Set the wavelength
trigIn  - Disable or enable the external trigger input
            - 0: Disable
            - 1: Enable
trigOut - Set the trigger output mode of the TSL
            - 0: None
            - 1: Stop
            - 2: Start
            - 3: Step
"""
    scope_cmd = """Enter the command you want to execute:
idn     - Get the identification of the oscilloscope
def     - Resets to default parameters NOTE: not working yet
tSrc    - Set the trigger source of the oscilloscope
            - C1, C2, C3, C4, EXT
tSlope  - Set the trigger slope of a channel (<channel>:<slope>)
            - <channel>: EXT, C1, C2, C3, C4
            - <slope>: Positive, Negative, Either
tMode   - Set the trigger mode of the oscilloscope. 
            - AUTO, NORM, SINGLE, STOP
tdiv    - Sets time division (horizontal scale) of the oscilloscope
            - 1, 2, 5, 10, 20, 50, 100, 200, 500 for NS, US, MS
            - 1, 2, 5, 10, 20, 50, 100 for S
vdiv    - Sets voltage division (vertical scale) of the oscilloscope (<channel>:<scale>)
            - <channel>: C1, C2, C3, C4
            - <scale>: 500 uV to 10 V per division (Default unit is V)
wave    - Write the waveform of a channel to a file (<channel>:<filename>)
            - <channel>: 1, 2, 3, 4
            - <filename>: Name of the file to write the waveform to.
chd     - Change the directory to save the waveform files
            - <dir>: The directory to save the waveform files to.
"""
    
    while True:
        cmd1 = input(base_cmd)

        if cmd1 == "tsl":
            cmd2 = input(tsl_cmd)
            if cmd2 == "idn":
                print(TSL.query("*IDN?"))
            elif cmd2.find("onoff") != -1:
                state = cmd2.split(" ")[1]
                TSL.write('POW:STAT ', state)
            elif cmd2.find("pow") != -1:
                power = cmd2.split(" ")[1]
                TSL.write('POW ', power)
            elif cmd2.find("wav") != -1:
                wavelength = cmd2.split(" ")[1]
                functions.SetWL(wavelength)
            elif cmd2 == "trigIn":
                state = cmd2.split(" ")[1]
                TSL.write('TRIG:INP:EXT ', state)
            elif cmd2.find("trigOut") != -1:
                mode = cmd2.split(" ")[1]
                TSL.write('TRIG:OUTP ', mode)
            else:
                print("Invalid command")
                time.sleep(0.5)

        elif cmd1 == "scope":
            cmd2 = input(scope_cmd)
            if cmd2 == "idn":
                functions.sidn()
            elif cmd2.find("tSrc") != -1:
                source = cmd2.split(" ")[1]
                functions.setTrigSource(source)
            elif cmd2.find("tSlope") != -1:
                tmp = cmd2.split(" ")[1]
                source = tmp.split(":")[0]
                slope = tmp.split(":")[1]
                functions.setTrigSlope(source, slope)
            elif cmd2.find("tMode") != -1:
                mode = cmd2.split(" ")[1]
                functions.setTrigMode(mode)
            elif cmd2.find("tDiv") != -1:
                scale = cmd2.split(" ")[1]
                functions.setTdiv(scale)
            elif cmd2.find("vDiv") != -1:
                tmp = cmd2.split(" ")[1]
                channel = tmp.split(":")[0]
                scale = tmp.split(":")[1]
                functions.setVdiv(channel, scale)
            elif cmd2.find("wave") != -1:
                tmp = int(cmd2.split(" ")[1])
                channel = tmp.split(":")[0]
                filename = tmp.split(":")[1]
                functions.storeData(channel, cmd2.split(" ")[2])
            else:
                print("Invalid command")
                time.sleep(0.5)

        elif cmd1 == "sweep":
            fpath = input("output file path: ")
            fname = input("output file name: ")
            channel = input("channel number: ")
            sWL = input("start wavelength: ")
            eWL = input("end wavelength: ")
            rSwe = input("sweep rate (nm/s): ")
            swpMode = input(
"""sweep modes:
0: One-way step
1: One-way continuous
2: Two-way step
3: Two-way continuous
sweep mode: """
)
            if swpMode == "0" or swpMode == "2":
                step = input("dwell time (s): ")
            elif TSL.query("TRIG:OUTP?") == "3":
                step = input("trigger step (m)")
            else:
                step = 0
            functions.Auto_Start(int(swpMode), int(sWL), int(eWL), int(rSwe), int(step), '')
            functions.storeData(int(channel), fpath + fname)

        
        elif cmd1 == "exit":
            break
        else:
            print("Invalid command")
            time.sleep(0.5)