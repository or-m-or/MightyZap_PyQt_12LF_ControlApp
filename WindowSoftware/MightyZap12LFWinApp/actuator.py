import time

class Actuator:
    def __init__(self, servo_id, serial_obj, baudrate, port):
        self.servo_id = servo_id
        self.serial_obj = serial_obj
        self.baudrate = baudrate
        self.port = port
        self.is_serial_open = serial_obj.is_open if serial_obj else False
        self.complete_count = 0 
        
    def send_command(self, command, expect_response=False):
        """보드에 시리얼 통신 명령어 전송"""
        if self.serial_obj and self.serial_obj.is_open:
            print(f'[send_command] ({self.port}) 명령어 전송: {command}')
            self.serial_obj.write(f"{command}\n".encode())
            time.sleep(0.1)
            if expect_response:
                response = self.serial_obj.readline()
                return response[:len(response) - 1].decode().strip()
        return None
