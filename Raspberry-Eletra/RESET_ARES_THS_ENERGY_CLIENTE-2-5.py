from RESET_ARES_THS import RS485_OPTICAL_abnt14522,find_open_port,exc_info,App
import configparser
import tkinter as tk
from time import sleep
try:

    config = configparser.ConfigParser()
    config.read_file(open(r'./include/config/config.ini'))
    lobj_config = {}

    lobj_config['uart_port']      = find_open_port()
    if  lobj_config['uart_port']  == None:
        while True:
            if find_open_port() == None:
                tk_root = tk.Tk()
                tk_app = App(tk_root)
                tk_app.update_label(str('PORTA NÂO ESTÀ CONECTADA'))
                sleep(1000)
                break


    lobj_config['baudrate']                = int(config.get('UART-Config', 'baudrate'))
    lobj_config['bytesize']                = int(config.get('UART-Config', 'bytesize'))
    lobj_config['parity']                  = str(config.get('UART-Config', 'parity'))
    lobj_config['stopbits']                = int(config.get('UART-Config', 'stopbits'))
    lobj_config['timeout']                 = int(config.get('UART-Config', 'timeout'))
    lobj_config['write_timeout']           = None   if config.get('UART-Config', 'write_timeout')            == 'None'      else int(config.get('UART-Config', 'write_timeout') )
    lobj_config['inter_byte_timeout']      = None   if config.get('UART-Config', 'inter_byte_timeout')       == 'None'      else int(config.get('UART-Config', 'inter_byte_timeout') )
    lobj_config['xonxoff']                 = False  if config.get('UART-Config', 'xonxoff')                  == 'False'     else True
    lobj_config['rtscts']                  = False  if config.get('UART-Config', 'rtscts')                   == 'False'     else True
    lobj_config['dsrdtr']                  = False  if config.get('UART-Config', 'dsrdtr')                   == 'False'     else True
    lobj_config['Log']                     = False  if config.get('UART-Config', 'Log')                      == 'False'     else True
    lobj_config['Print']                   = False  if config.get('UART-Config', 'Print')                    == 'False'     else True
    lobj_config['Raise']                   = False  if config.get('UART-Config', 'Raise')                    == 'False'     else True
    lobj_config['check_crc16']             = False  if config.get('UART-Config', 'check_crc16')              == 'False'     else True   
    lobj_config['check_length']            = False  if config.get('UART-Config', 'check_length')             == 'False'     else True   

    obj_UART = RS485_OPTICAL_abnt14522(
                                            lobj_config['uart_port'],
                                            lobj_config['baudrate'],
                                            lobj_config['bytesize'],
                                            lobj_config['parity'],
                                            lobj_config['stopbits'],
                                            lobj_config['timeout'],
                                            lobj_config['write_timeout'],
                                            lobj_config['inter_byte_timeout'],
                                            lobj_config['xonxoff'],
                                            lobj_config['rtscts'],
                                            lobj_config['dsrdtr'],
                                            lobj_config['Log'],
                                            lobj_config['Print'],
                                            lobj_config['Raise'],
                                            lobj_config['check_crc16'],
                                            lobj_config['check_length'])

    obj_UART.set01file_ares8023(2,True,True)

    # print(obj_UART.UART_abtn14522_read_register("00091227",14))
    # obj_UART.UART_abtn14522_fake_read_register()
    # print(obj_UART.optical_reading_code(code=21))
    # obj_UART.reset_ares8023()
except Exception as err:
    _, _, exception_traceback = exc_info()
    line_number = exception_traceback.tb_lineno
    print(f'LINE : {line_number}  -  {str(err)} ')