# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver

#����ȡ port:����P�˿ڣ�  �������أ��Ҷ�����; ��ȡ����-1  
def get_value(port:bytes) -> Optional[bytes]:
    light_str=[0xA0, 0x02, 0x00, 0xBE]
    light_str[0]=0XA0+port
    light_str[2]=1
    response = base_driver.single_operate_sensor(light_str)       
    if response == None:
        return None
    else:
        light_data=response[4:-1]
        light_num=int.from_bytes(light_data, byteorder='big', signed=True)
        return light_num
        