import serial
PROTOCOL_TX_BUF_SIZE =  50
PROTOCOL_RX_BUF_SIZE = 50
MIGHTYZAP_PING = 0xf1
MIGHTYZAP_READ_DATA = 0xf2
MIGHTYZAP_WRITE_DATA = 0xf3
MIGHTYZAP_REG_WRITE = 0xf4
MIGHTYZAP_ACTION = 0xf5
MIGHTYZAP_RESET = 0xf6
MIGHTYZAP_RESTART = 0xf8
MIGHTYZAP_FACTORY_RESET = 0xf9
MIGHTYZAP_SYNC_WRITE = 0x73 

TxBuffer=[0]*PROTOCOL_TX_BUF_SIZE
TxBuffer_index = 0
RxBuffer=[0]*PROTOCOL_RX_BUF_SIZE
RxBuffer_size =0

ErollService = 0
ErollService_Instruction = 0
ErollService_ID = 0x00
ErollService_Addr = 0x00
ErollService_Size = 0x00
ErollService_ModelNum = 0x0000
ActuatorID = 0
checksum=0
MZap = serial.Serial()

def SetProtocalHeader():
    global TxBuffer_index
    global TxBuffer
    TxBuffer_index = 0    
    TxBuffer[TxBuffer_index] = 0xff
    TxBuffer_index+=1
    TxBuffer[TxBuffer_index] = 0xff
    TxBuffer_index+=1
    TxBuffer[TxBuffer_index] = 0xff
    TxBuffer_index+=1
    TxBuffer[TxBuffer_index] = ActuatorID
    TxBuffer_index+=1

def SetProtocolInstruction(ins):
    global TxBuffer_index
    global TxBuffer
    global ErollService_Instruction

    TxBuffer_index = 5
    ErollService_Instruction = ins    
    TxBuffer[TxBuffer_index] = ins
    TxBuffer_index+=1

def AddProtocolFactor(para):
    global TxBuffer_index
    global TxBuffer    
    TxBuffer[TxBuffer_index] = para
    TxBuffer_index+=1

def SetProtocollength_checksum():
    global TxBuffer_index
    global TxBuffer
    global checksum
    checksum = 0
    start_i = 0

    TxBuffer[4] = TxBuffer_index - 4
    start_i = 3
        
    for i in range(start_i,TxBuffer_index):	
        checksum += TxBuffer[i]    
    TxBuffer[TxBuffer_index] = (checksum & 0x000000ff)^ 0x000000ff
    TxBuffer_index+=1

def getID():
    global ActuatorID
    return ActuatorID

def setID(ID):
    global ActuatorID
    ActuatorID = ID

def MightyZap(ID) :
    global ErollService
    global ErollService_Instruction
    global ErollService_ID
    global ErollService_Addr
    global ErollService_Size
    global ErollService_Size
    
    ErollService = 0
    ErollService_Instruction = 0
    ErollService_ID = 0x00
    ErollService_Addr = 0x00
    ErollService_Size = 0x00
    ErollService_ModelNum = 0x0000

    setID(ID)

def OpenMightyZap(portname, BaudRate):
    """
    시작 COM Port 연결 : 서보 액츄에이터를 제어하기 위한 포트연결 
    
    Args:
        portname (str): 연결할 COM 포트 번호를 문자열로 입력 (예: "COM6").
        BaudRate (int): 통신 속도. 9600, 19200, 57600, 115200bps 제공.
    """
    MZap.port = portname
    MZap.baudrate = BaudRate
    MZap.timeout = 0.1
    
    MZap.open()

def serialtimeout(time):
    MZap.timeout = time
    
def CloseMightyZap():
    """ 서보 액츄에이터를 제어한 포트연결 종료 """
    MZap.close()

def SendPacket():
    global TxBuffer_index
    global TxBuffer
    for i in range(0,TxBuffer_index):	
        MZap.write([TxBuffer[i]])

def ReceivePacket(ID, size):
    global TxBuffer_index
    global TxBuffer    
    global RxBuffer
    timeout = 0
    temp =0
    i =0
    head_count = 0
    
    while head_count < 3:
        timeout =timeout+1
        if timeout>5:
            RxBuffer[6] = 0
            RxBuffer[7] = 0
            return -1;
        
        temp = MZap.read(1);
   
        if temp == b'\xff':
            RxBuffer[head_count] = 0xff
            head_count+=1
        else:
            RxBuffer[0] = 0            
            head_count=0

    for i in range(3,size):
        temp = ord(MZap.read(1))
        RxBuffer[i] = temp
        
    return 1

def read_data(ID, addr, size): 
    global MIGHTYZAP_READ_DATA
    
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_READ_DATA)
    AddProtocolFactor(addr)
    AddProtocolFactor(size)
    SetProtocollength_checksum()
    SendPacket()	

def ead_data_model_num(ID):
    global MIGHTYZAP_READ_DATA
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_READ_DATA)
    AddProtocolFactor(0); ErollService_Addr = 0
    AddProtocolFactor(2); ErollService_Size = 2
    SetProtocollength_checksum()
    SendPacket()

def write_data(ID, addr, data, size):
    global MIGHTYZAP_WRITE_DATA
    i = 0
    setID(ID)        
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_WRITE_DATA)
    AddProtocolFactor(addr)
    for i in range(0,size):
        AddProtocolFactor(data[i])
    SetProtocollength_checksum()
    SendPacket()
		
def Sync_write_data(addr,data, size):
    """
    다수 서보의 동일한 Address에 Data 저장
    
    Args:
        Addr :Data를 입력할 파라메터 주소, 아래 표의 Factor#1
        data :입력 Data 행렬, 아래 표의 Factor#2 이후의 Factor 값을 행렬로 입력 
            Length + ID1 + Datat#1, +Data#2 +ID2 + Data#1 + data#2 …..
        Size :입력한 Data Size
    """
    global MIGHTYZAP_SYNC_WRITE
    i = 0
    setID(0xfe)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_SYNC_WRITE)
    AddProtocolFactor(addr)
    for i in range(0,size):
        AddProtocolFactor(data[i])
    SetProtocollength_checksum()
    SendPacket()
        
def WritePacket(buff, size):
    """
    하나의 완성된 Packet을 서보 액츄에이터에 사용자가 직접 Packet을 구성하여 보낼 때 사용 
    
    Args:
        buffer : 서보 액츄에이터에 전송할 Packet buffer
        size: 서보 액츄에이터에 전송할 Packet buffer의 사이즈
            ( Packet 전송의 대한 자세한 설명은 사용자 매뉴얼에의 Packet Description 또는 Packet 예제를 참조하시기 바랍니다.) 
    """
    for i in range(0,size):	
        MZap.write([buff[i]])				
		
def reg_write(ID,  addr, data,size): # 파라미터 datz -> data 오타 의심되어 수정함
    global MIGHTYZAP_WRITE_DATA
    i = 0
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_REG_WRITE)
    AddProtocolFactor(addr)
    for i in range(0,size):
        AddProtocolFactor(data[i])
    SetProtocollength_checksum()
    SendPacket()

def action(ID):
    global MIGHTYZAP_WRITE_DATA
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_ACTION)
    SetProtocollength_checksum()
    SendPacket()

        
def reset_write(ID, option):
    global MIGHTYZAP_RESET
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_RESET)
    AddProtocolFactor(option)
    SetProtocollength_checksum()
    SendPacket()

    
def Restart(ID):
    """ 
    서보 액츄에이터의 시스템을 재 시작
    Overload, input Voltage Error 등으로 인한 Shutdown(모터 정지)을 재 시작 시킬 수 있음    
    
    Arge:
         bID :서보ID (1~253), Broad CAST ID(254), Stand-alone ID (0)
    """
    global MIGHTYZAP_RESTART
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_RESTART)
    SetProtocollength_checksum()
    SendPacket()

        
def factory_reset_write(ID,  option):
    global MIGHTYZAP_FACTORY_RESET
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_FACTORY_RESET)
    AddProtocolFactor(option)
    SetProtocollength_checksum()
    SendPacket()


def ping(ID):
    global MIGHTYZAP_PING
    setID(ID)
    SetProtocalHeader()
    SetProtocolInstruction(MIGHTYZAP_PING)
    SetProtocollength_checksum()
    SendPacket()

def changeID(bID,data):
    pByte=[0]*1
    pByte[0] = (data & 0x00ff)
    setID(pByte[0])
    write_data(bID, 0x03, pByte, 1)

def GoalPosition(bID, position):
    """
    스트로크 위치를 원하는 위치로 이동
    
    Args:
        bID :서보ID
        position :이동하고자 하는 위치 (0~4095)
    """
    pByte=[0]*2
    pByte[0] = (position & 0x00ff)
    pByte[1] = (position >> 8)
    write_data(bID, 0x86, pByte, 2)

def PresentPosition(bID):
    """
    현재위치 읽기 :현재의 스트로크 위치를 파악하여 회신
    
    Args:
        bID :서보ID
    Return:
        현재의 스트로크 위치값을 회신합니다. (Timeout 발생시 ‘-1’ 값을 return 합니다.)
    """
    global RxBuffer
    read_data(bID,0x8C,2)		
    timeout = ReceivePacket(bID,9)
    if timeout == 1:
        return (RxBuffer[7] *256)+(RxBuffer[6])
    else :
        return -1
	

def GoalSpeed(bID, speed):
    """
    이동속도 조정 [F/C Version Only]
    서보 액츄에이터의 이동 속도 제어
    
    Args:
        bID :서보ID
        speed :이동하고자 하는 속도 감소치 (0~1023), 
            (0일 때 속도 감소 모드 해제(최대 속도), 1~1023 속도 감소 모드(1:저속, 1023:고속))
    """
    pByte=[0]*2

    pByte[0] = (speed & 0x00ff)
    pByte[1] = (speed >> 8)
    write_data(bID, 0x15, pByte, 2)

def GoalCurrent(bID, curr):
    """
    최대 전류 조정 [F/C Version Only]
    최대 사용 전류의 상한선을 제어
    
    Args:
        bID :서보ID
        current :목표하는 최대 전류 값 (0~1600)
            (0일 때 최대 전류 1600mA를 나타낸다., 범위 : 1~1600 으로 전류값 제어, default : 800)
            ※ 전류를 줄이면 속도도 함께 줄어들게 됩니다.
            ※ 해당 값은 실제 전류 값을 mA로 표현한 것이며 +/-15% 오차를 포함 하고 있습니다.
            ※ 높은 골커런트 설정은 액츄에이터의 수명에 영향을 줄 수 있으므로, 적절한 사용을 위해 data sheet를 참고하시기 바랍니다.
    """
    pByte=[0]*2

    pByte[0] = (curr & 0x00ff)
    pByte[1] = (curr >> 8)
    write_data(bID, 0x34, pByte, 2)

def Acceleration(bID, acc):
    """
    가속률 제어 [F/C Version Only]
    서보 액츄에이터의 가속률을 제어
    
    Args:
        bID :서보ID
        accel:서보 액츄에이터의 가속률 값 (1~255) / 값이 클수록 가속도가 빨라집니다
    """
    pByte=[0]*1
    pByte[0] = acc
    write_data(bID, 0x21, pByte, 1)
    
def Deceleration(bID, acc):
    """
    감속률 제어 [F/C Version Only]
    서보 액츄에이터의 감속률을 제어
    
    Args:
        bID :서보ID
        decel: 액츄에이터의 감속률 값 (1~255) / 값이 클수록 감속률이 커지고 감속 타임이 늦어집니다.
            ※너무 큰 값으로 설정하면 최종 위치 도달 시 Overshoot 및 진동이 발생할 수 있습니다.
            ※Speed 및 GoalCurrent 등 액츄에이터의 기본 설정을 변경 중 Overshoot이 발생하면 감속률을 줄여주면 됩니다. 
    """
    pByte=[0]*1
    pByte[0] = acc
    write_data(bID, 0x22, pByte, 1)
		
def ShortStrokeLimit(bID, SStroke):
    pByte=[0]*2

    pByte[0] = (SStroke & 0x00ff)
    pByte[1] = (SStroke >> 8)
    write_data(bID, 0x06, pByte, 2)
	
def LongStrokeLimit(bID, LStroke):
    pByte=[0]*2

    pByte[0] = (LStroke & 0x00ff)
    pByte[1] = (LStroke >> 8)
    write_data(bID, 0x08, pByte, 2)	
	
def ForceEnable(bID, enable):
    """
    Force On / Off
    서보 액츄에이터의 Force를 강제적으로 활성/비활성
    
    Args:
        bID :서보ID
        enable : 0일 때 비활성, 1일 때 활성
    ※ Force Off된 상태라도 통신은 여전히 동작합니다.
    ※ Force Off된 상태에서 다음 위치 명령을 내리면 자동으로 Force On되며 위치이동.
    당사 서보 서보 액츄에이터 중 35N이상의 제품의 경우 모터의 전원이 해제되어도 기구적인 설계특성상 위치를 고수하려는 특성이 있습니다.
    따라서, 설비에서 서보 서보 액츄에이터가 특정위치를 지속적으로 고수하고 있어야 하는 경우 Force Off 명령으로 모터전원을 차단하여 
    모터의 수명을 연장시킬 수 있습니다. 이 경우 통신은 여전히 유지되며, 모터의 전원만 차단됩니다. 
    다시 위치이동명령을 내리게 되면 자동으로 Force ON 되어 다음 명령을 수행하게 됩니다. 
    """
    pByte=[0]*2
    
    if enable ==1:
        pByte[0]=1
    else :
        pByte[0] = 0
        
    write_data(bID,0x80,pByte,1)
    SendPacket()

	
def SetShutDownEnable(bID, flag):
    """
    Shutdown On / Off
    에러 발생시 서보 액츄에이터의 전원 연결 가능/불가능을 에러 별로 각각 설정
    
    Args:
        bID :서보ID
        flag :설정하고자 하는 값 (사용자 매뉴얼 Alarm Shutdown 참조) 
    """
    pByte=[0]*1
    pByte[0] = flag
    write_data(bID, 0x12, pByte, 1)

def GetShutDownEnable( bID):							
    read_data(bID,0x12, 1)
    timeout = ReceivePacket(bID,8)
    if timeout == 1:    
        return RxBuffer[6]
    else:
        return -1

def SetErrorIndicatorEnable(bID, flag):
    pByte=[0]*1
    pByte[0]=flag	
    write_data(bID,0x11,pByte,1)					

def GetErrorIndicatorEnable(bID):
    read_data(bID,0x11, 1)
    timeout = ReceivePacket(bID,8)
    if timeout == 1:
        return RxBuffer[6]
    else :
        return -1
		
def ReadError( bID):
    """
    현재 에러 발생 상태를 회신
    
    Args:
        bID :서보 ID
    Return:
        에러 발생 상태를 회신 (Timeout 발생시 ‘-1’ 값을 return 합니다.)
    """
    ping(bID)
    timeout = ReceivePacket(bID,7)
    if timeout == 1:
        return RxBuffer[5]
    else :
        return -1

def Write_Addr( bID,  addr,  size,  data):
    """
    주소에 Data직접쓰기
    Data Map의 Memory/Parameter에 직접 Data를 쓰기 위해 해당 주소에 직접 입력
    
    Args:
        bID :서보 ID
        Addr :Data를 입력할 파라메터 주소
        Size :입력할 Data Size
        Data :입력 Data
        ( mightyZAP사용자매뉴얼 Data Map 참고)
    """
    if size == 2:
        pByte=[0]*2 
        pByte[0]=(data&0x00ff)
        pByte[1]=(data//256)
        write_data(bID,addr,pByte,2)				
    else:
        pByte=[0]*1
        pByte[0] = data
        write_data(bID,addr,pByte,1)					

def Read_Addr(bID, addr, size):
    """
    주소 직접읽기
    Data Map의 Memory/Parameter로부터 직접 Data를 읽기 위해 해당 주소로부터 직접 읽어오기
    
    Args:
        bID :서보 ID
        Addr :Data를 읽어올 파라메터 주소
        Size :읽어올 Data Size
    Return:
        읽어 온 Data회신 (Timeout 발생시 ‘-1’ 값을 return 합니다.)
        ( mightyZAP 사용자매뉴얼–Data Map-참고) 
    """
    if size==2 :
        read_data(bID,addr,2)		
        timeout = ReceivePacket(bID,9)
        if timeout == 1:
            return (RxBuffer[7] *256) + RxBuffer[6]
        else :
            return -1
    else :
        read_data(bID,addr,1)        
        timeout = ReceivePacket(bID,8)
        if timeout == 1:
            return RxBuffer[6]
        else :
            return -1