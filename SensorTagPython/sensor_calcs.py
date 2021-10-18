from os import name, system

tosigned = lambda n: float(n-0x10000) if n>0x7fff else float(n)
tosignedbyte = lambda n: float(n-0x100) if n>0x7f else float(n)

def calcTmpTarget(objT, ambT):
        
    objT = tosigned(objT)
    ambT = tosigned(ambT)

    m_tmpAmb = ambT/128.0
    Vobj2 = objT * 0.00000015625
    Tdie2 = m_tmpAmb + 273.15
    S0 = 6.4E-14            # Calibration factor
    a1 = 1.75E-3
    a2 = -1.678E-5
    b0 = -2.94E-5
    b1 = -5.7E-7
    b2 = 4.63E-9
    c2 = 13.4
    Tref = 298.15
    S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
    Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
    fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
    tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
    tObj = (tObj - 273.15)
    return tObj

def temp_calc(data):  
    objT = (data[1]<<8)+data[0]
    ambT = (data[3]<<8)+data[2]
    return calcTmpTarget(objT, ambT)   

def accel_calc(data):
    acc = lambda v: tosignedbyte(v) / 64.0
    return [acc(data[0]), acc(data[1]), acc(data[2]) * -1]     

def humid_calc(data): 
    rawH = (data[3]<<8)+data[2]   
    rawH = float(int(rawH) & ~0x0003)
    return -6.0 + 125.0/65536.0 * rawH  

def magn_calc(data):
    x = (data[1] & 0xFF <<8)+data[0] & 0xFF
    y = (data[3] & 0xFF <<8)+data[2] & 0xFF
    z = (data[5] & 0xFF <<8)+data[4] & 0xFF
    magforce = lambda v: (tosigned(v) * 1.0) / (65536.0/2000.0)
    return [magforce(x),magforce(y),magforce(z)]

def bar_calc(data):
    m_raw_temp = tosigned((data[1]<<8)+data[0])
    m_raw_pres = (data[3]<<8)+data[2]
    return 1000.0 

def gyro_calc(data):
    x = (data[1]<<8)+data[0]
    y = (data[3]<<8)+data[2]
    z = (data[5]<<8)+data[4]
    result = lambda v: (tosigned(v) * 1.0) / (65536.0/500.0)
    return [result(x),result(y) ,result(z)]

def key_calc(data):
    i = int.from_bytes(data, "big")
    result =''
    if i == 1:
        result = 'Right'
    elif i == 2:
        result = 'Left'
    elif i == 3:
        result = 'Left and Right'
    else:
        result = 'None'
    return result