from serial   import Serial, SerialException
from serial   import FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS,PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE
from sys      import exc_info
from os       import path
from time     import sleep
import        datetime
from textwrap import wrap
import logging
from termcolor import colored
import tkinter as tk
from tkinter import ttk
import pygame.midi as midi
import serial.tools.list_ports

def find_open_port():
    for port in serial.tools.list_ports.comports():
        try:
            s = serial.Serial(port.device)
            s.close()
            return port.device
        except serial.SerialException:
            pass
    return None

class App:

    def __init__(self, master):
        self.master = master
        master.title("Loading")
        # Obtém a largura e altura da tela do monitor
        screen_width = master.winfo_screenwidth() 
        screen_height = master.winfo_screenheight()
        
        master.geometry("%dx%d+0+0" % (screen_width, screen_height))
        master.configure(bg="#212121")
        self.label = tk.Label(master, text='RESETANDO MEDIDOR ARES 8023', font=("Arial", 14), fg="white", bg="#212121")
        self.label.pack(pady=10)
        self.progressbar = ttk.Progressbar(master, orient='horizontal', length=250, mode='indeterminate')
        self.progressbar.pack(pady=20)
        self.loading_bar = tk.Label(master, text="", font=("Arial", 14), fg="white", bg="black")
        self.loading_bar.pack(pady=50)

        # self.button1 = tk.Button(master, text="Button 1", command=self.button1_clicked)
        # self.button1.pack(pady=10)

        self.start_loading()
        
    def start_loading(self):
        self.progressbar.start()

    def update_label(self, valor):
            self.loading_bar.config(text=valor)
            self.master.update()
            
    def button1_clicked(self):
        # Define the behavior when Button 1 is clicked
        print("Button 1 clicked")



class RS485_OPTICAL_abnt14522(object):

    def __init__(self,uart_port:str,
                    baudrate:int,
                    bytesize:int,
                    parity:str,
                    stopbits:int,
                    timeout:int,
                    write_timeout=None,
                    inter_byte_timeout=None,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False,
                    Log=False,
                    Print=False,
                    Raise=False,
                    check_crc16=False,
                    check_length=True
                    ):

        # dev/ttyS1'  pin 38 TX | 40 RX     
        # dev/ttyS2'  pin 13 TX | 11 RX            
        # dev/ttyS3'  pin 8 TX  | 10 RX            


        #   CLASS CONFIG
        self.Log                : bool = Log             # Activa logging debug
        self.Print              : bool = Print           # Activa print
        self.Raise              : bool = Raise           # Return raise if True
        self.check_crc16        : bool = check_crc16     # If true Check if crc correct       
        self.check_length       : bool = check_length    # If true Check if length msg correct

        #   UART USB  CONFIG    
        self.port    : str = uart_port

        self.tk_root = tk.Tk()
        self.tk_app = App(self.tk_root)





        if  not path.exists(self.port):
            return self.raise_or_print(line_number=42,err=str(f"Err in port  : {self.port}"))


        if bytesize in [5,6,7,8]:
            if bytesize == 5:
                bytesize = FIVEBITS
            if bytesize == 6:
                bytesize = SIXBITS
            if bytesize == 7:
                bytesize = SEVENBITS
            if bytesize == 8:
                bytesize = EIGHTBITS
        else:
            self.raise_or_print(line_number=55,err=str(f"Err in bytesize: {bytesize}"))

            
        parity = parity.upper()
        if parity in ['NONE','EVEN','ODD','MARK','SPACE']:
            if parity == 'NONE':
                parity = PARITY_NONE
            if parity == 'EVEN':
                parity = PARITY_EVEN
            if parity == 'ODD':
                parity = PARITY_ODD
            if parity == 'MARK':
                parity = PARITY_MARK
            if parity == 'SPACE':
                parity = PARITY_SPACE
        else:
            self.raise_or_print(line_number=78,err=str(f"Err in parity: {parity}"))
            
        try:
            #   SERIAL CONFIG    
            self.obj_serial                    = Serial(self.port)              # Porta serial a ser utilizada
            self.obj_serial.baudrate           :int = baudrate                  # Taxa de transmissão em bits por segundo
            self.obj_serial.bytesize           :int = bytesize                  # Número de bits de dados por byte (8 bits)
            self.obj_serial.parity             :str = parity                    # Tipo de paridade (nenhuma)
            self.obj_serial.stopbits           :int = stopbits                  # Número de bits de parada (1 bit)
            self.obj_serial.timeout            = timeout                        # Tempo limite em segundos para a leitura da porta serial
            self.obj_serial.write_timeout      = write_timeout                  # Representa o tempo de espera em segundos para operações de escrita.
            self.obj_serial.inter_byte_timeout = inter_byte_timeout             # Representa o tempo de espera em segundos entre bytes de dados recebidos
            self.obj_serial.xonxoff            = xonxoff                        # Controle de fluxo XON/XOFF desativado
            self.obj_serial.rtscts             = rtscts                         # Controle de fluxo RTS/CTS desativado
            self.obj_serial.dsrdtr             = dsrdtr                         # Controle de fluxo DSR/DTR desativado
            self.is_open                       : bool = self.obj_serial.is_open # Retorna se a porta serial esta open


        except Exception as err:    
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))


    def raise_or_print(self,line_number:int,err:str):
        self.logging_or_print(f'LINE : {line_number}   -   {err} ')
        if self.Print  == True:
            print(f'LINE : {line_number}   -   {err} ')
        if self.Raise  == True:
            raise Exception(f'LINE : {line_number}   -   {err} ')


    def formate_bytes(self,btarr:bytes,space:bool) -> str:
        if space :
            return ' '.join(['{:02X}'.format(b) for b in btarr])
        else:
            return ''.join(['{:02X}'.format(b) for b in btarr])


    def logging_or_print(self,message:str):
        
        # if str(self.port.split("/")[-1]) == '':
        #     port = 'not_found_port_err'
        # else:
        #     port = str(self.port.split("/")[-1])
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',filename=f'./include/logs/COM.log', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
        if self.Print == True:
            print(str(message))
        if self.Log == True:
            logging.debug(str(message))  


    def calcula_crc16_abnt(self,input_data:bytes) -> bytes:
        try:
            def calcula_crc16_optical_input(string_crc, tamanho_buffer):
                retorno = 0
                crcpolinv = 0x4003
                for i in range(0, tamanho_buffer):
                    retorno ^= (string_crc[i] & 0xff)
                    for _ in range(0, 8):
                        if ((retorno & 0x0001) != 0):
                            retorno ^= crcpolinv
                            retorno >>= 1
                            retorno |= 0x8000
                        else:
                            retorno >>= 1
                return retorno
            crc = calcula_crc16_optical_input(input_data, len(input_data))
            crc = ((crc & 0xff) << 8) | ((crc & 0xff00) >> 8)
            hex_str = hex(crc)[2:].zfill(4)
            byte_obj = bytes.fromhex(hex_str)
            return byte_obj

        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))


    def check_crc16_abnt14522(self,input_data:str) -> bool:
        try:
            data  = input_data[:-4]
            crc_input_data = input_data[-4:]
            crc_expected    =  self.formate_bytes(btarr=self.calcula_crc16_abnt(bytes.fromhex(str(data))),space=False)

            if str(crc_expected).upper() == str(crc_input_data).upper():
                return True
            return False
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))


    def Disconnect(self):
        try:
            self.obj_serial.close()
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))

        
    def UART_send(self, value:bytes) -> bool:
        try: 
            if self.obj_serial.is_open:
                self.logging_or_print(f"    {colored(self.port, 'dark_grey')}  -  {colored('SEND', 'red')} :   {self.formate_bytes(btarr=value,space=True)}")
                self.obj_serial.write(value) 
                self.obj_serial.reset_input_buffer()
                return True
            else:
                return self.raise_or_print(line_number=209,err='Port is not open - UART_send')
            
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))
            return False


    def UART_read(self,leng:int) -> bytes:
        try: 
            if self.obj_serial.is_open:
                response = self.obj_serial.read(leng)
                self.logging_or_print(f"    {colored(self.port, 'dark_grey')}  -  {colored('READ', 'green')} :   {self.formate_bytes(btarr=response,space=True)}")
                self.obj_serial.reset_input_buffer()
                return response
            else:
                return self.raise_or_print(line_number=217,err='Port is not open - UART_read')
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))


    def UART_wait_buffer(self,leng:int,stop:bool) -> str:
        try: 
            while True:
                response = self.UART_read(int(leng))
                if len(response) >= leng:
                    if stop:
                        return self.formate_bytes(btarr=response,space=True)
                        
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))

    def optical_reading_code(self,code:int):
        try:
            if code in [21,14]:

                self.obj_serial.setDTR(True)
                sleep(1)   
                self.UART_read(6)
                code = bytes.fromhex(''.join([f'x{el}' for el in f'{code}']).replace('x', ''))
                message = code + b'\x11\x11\x11' +  b'\x00' * 60 
                message   = message + self.calcula_crc16_abnt(message)
                self.UART_send(message) 
                sleep(0.1)   
                response = self.UART_read(258)
                response_sem_space = self.formate_bytes(btarr=response,space=False)
                response__correct = self.check_crc16_abnt14522(response_sem_space)
                
                if  self.check_crc16 and not response__correct:
                    return False
                self.obj_serial.setDTR(False)   
                self.UART_send(b'\x06')
                self.obj_serial.setDTR(False) 
                
                if len(response) >= 250:
                    return True
                else :
                    return False
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))


    def UART_abtn14522_read_register(self,serial_number:str,code:int) -> str:
        try: 
            if code in [14,20,21,22,51]:
                serial_number_code = bytes.fromhex(''.join([f'x{el}' for el in f'{serial_number}{code}']).replace('x', ''))
                message = b'\x99' + serial_number_code + b'\x11\x11\x11' +  b'\x00' * 60
                message += self.calcula_crc16_abnt(message[5::])
                if self.UART_send(message):
                    response = self.UART_read()
                    if response:
                        return str(self.formate_bytes(response))
                else:
                    return False
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(int(exception_traceback.tb_lineno),str(err))


    def reset_ares8023(self):
        try:
            self.tk_app.update_label(str('Inicia o reset do medidor'))
            self.obj_serial.setDTR(True)   
            self.UART_read(5)
            self.UART_send(b'\x98\x11\x11\x11\x57\xFE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x62\x0A') 
            self.UART_read(257)
            self.obj_serial.setDTR(False)   
            self.UART_send(b'\x06')
            self.obj_serial.setDTR(False) 
            return True
        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(int(exception_traceback.tb_lineno),str(err),Str=True,Raise=False)



    def set01file_ares8023(self,eqm_display_type,bol_inicializa,bol_config_display):
        try:
            # if eqm_display_type == 1:
            #     display_name = "energia ativa"
            #     display_list = [1,2,3,24,32,33]

            # if eqm_display_type == 2:
            #     display_name = "cliente 2,5"
            #     display_list = [1,2,3,4,8,10,14,16,17,21,23,24,25,29,32,33,52,53,54,57,66,68,69,71,73,75,93]
            
            # if eqm_display_type == 3:
            #     display_name = "solar"
            #     display_list = [1,2,3,24,32,33,55]
            
            # if eqm_display_type == 4:
            #     display_name = "solar"
            #     display_list = [1,2,3,24,33,55,65]


            if self.reset_ares8023() :
                data_atual = datetime.datetime.now()
                dia_atual = str(data_atual.day).zfill(2)
                mes_atual = str(data_atual.month).zfill(2)
                ano_atual = str(data_atual.year)[2:]
                dia_atual = str(data_atual.day).zfill(2)
                hora_atual = str(data_atual.hour).zfill(2)
                minuto_atual = str(data_atual.minute).zfill(2)
                segundo_atual = str(data_atual.second).zfill(2)

                
                dia = bytes.fromhex(''.join([f'x{el}' for el in f'{(dia_atual)}']).replace('x', ''))
                mes = bytes.fromhex(''.join([f'x{el}' for el in f'{str(mes_atual)}']).replace('x', ''))
                ano = bytes.fromhex(''.join([f'x{el}' for el in f'{str(ano_atual)}']).replace('x', ''))

                hora = bytes.fromhex(''.join([f'x{el}' for el in f'{str(hora_atual)}']).replace('x', ''))
                minuto = bytes.fromhex(''.join([f'x{el}' for el in f'{str(minuto_atual)}']).replace('x', ''))
                segundo = bytes.fromhex(''.join([f'x{el}' for el in f'{str(segundo_atual)}']).replace('x', ''))

            
            
                msg_hour = b'\x30\x12\x34\x56' + hora + minuto  + segundo + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                msg_hour = msg_hour + self.calcula_crc16_abnt(msg_hour)

                msg_date = b'\x29\x12\x34\x56' + dia + mes  + ano + b'\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                msg_date = msg_date + self.calcula_crc16_abnt(msg_date)


                sleep(8)
                self.tk_app.update_label(str('Seta o arquivo 01'))
                self.obj_serial.setDTR(True)   
                sleep(1.3)
                self.obj_serial.setDTR(False)   
                sleep(0.2)
                self.obj_serial.setDTR(True)   
                sleep(0.3)
                self.UART_send(b'\x09\x03\x03\x03\x03\x03\x03\xF6\xF5\x82\x82\xBE\x39')
                self.UART_read(1)
                self.obj_serial.setDTR(True)   
                sleep(2)
                self.UART_read(19)
                self.UART_send(b'\x09\x03\x81\x03\x03\x03\x03\x03\x87\x03\x03\x03\x03\xF5\x72\xBE\x39')
                self.UART_read(14)
                self.obj_serial.setDTR(True)   
                sleep(0.0350)
                self.UART_send(b'\x09\x81\x03\x03\x03\x03\x03\x03\x03\x03\x81\x03\x87\x03\x03\x03\x81\x03\x03\x82\x0A\x84\xF5\x03\x72\x03\x81\x84\xF6\x06\x05\x03\x81\x81\xF0\x77\x06\x03\x82\x81\x03\x03\x03\x03\x03\x81\x81\x03\x81\x03\x03\x82\x72\x87\x06\x87\x06\x06\x00\x00\x81\x00\x81\x03\x81\x87\x71\xF5\x82\x00\x81\x00\x81\x82\x71\xBE\x39')
                self.UART_read(14) 

                with open('./include/01-files/8023VS98.txt', 'r') as file:
                    data_list =  [el for el in file]
                    for el in range(0,len(data_list)):
                        str(data_list[el]).replace('\n','')
                        self.UART_send(bytes.fromhex(data_list[el]))
                        self.UART_read(14)
                        self.tk_app.update_label(f'Seta o arquivo 01   - {el}  de {len(data_list)}')


                self.obj_serial.write(b'\x09\x03\x03\x03\x03\x03\x03\x03\x82\xF5\xF5\xBE\x39\xBE\x39')
                self.obj_serial.setDTR(True)   
                sleep(0.3)
                self.obj_serial.read(20)
                self.obj_serial.write(b'\x09\x03\x03\x03\x03\x03\x03\x03\x82\xF5\xF5\xBE\x39')
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.obj_serial.read(12)
                    
                if bol_inicializa == False:
                    self.tk_app.update_label(f'MEDIDOR EM MODO CONFIG')
                    sleep(40)
                    return

                if eqm_display_type == 2:
                     # BEGIN 
                    self.obj_serial.setDTR(True) 
                    sleep(1)
                    self.UART_send(b'\x29\x12\x34\x56\x08\x03\x24\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x92\x05')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END 



                self.tk_app.update_label(f'Inicializa o medidor')
                sleep(4)
                # BEGIN DATA
                self.tk_app.update_label(f'configura  a DATA')
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.UART_read(5)
                self.UART_send(msg_date)
                self.obj_serial.setDTR(True) 
                self.UART_read(257)
                sleep(0.3)
                self.obj_serial.setDTR(False)
                # END DATA

                # BEGIN INTERVALO DE DEMANDA
                self.tk_app.update_label(f'configura  o INTERVALO DE DEMANDA')
                sleep(0.8)
                self.obj_serial.setDTR(True) 
                self.UART_read(7)
                self.obj_serial.setDTR(True) 
                sleep(1)
                self.UART_send(b'\x31\x12\x34\x56\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x94\x6A')
                self.UART_read(257)
                self.obj_serial.setDTR(False)   
                # END INTERVALO DE DEMANDA

                # BEGIN FERIADOS NACIONAIS
                self.tk_app.update_label(f'configura  o FERIADOS NACIONAIS')
                sleep(0.5)
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.UART_read(7)
                self.UART_send(b'\x32\x12\x34\x56\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x95\x5B')                
                self.UART_read(257)
                self.obj_serial.setDTR(False)   
                # END FERIADOS NACIONAIS

                # BEGIN CONSTANTES DE MULTIPLICACAO
                self.tk_app.update_label(f'configura  o CONSTANTES DE MULTIPLICACAO')
                sleep(0.5)
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.UART_read(7)
                self.UART_send(b'\x33\x12\x34\x56\x00\x00\x01\x00\x10\x00\x00\x00\x01\x00\x10\x00\x00\x00\x01\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x6F\x1F')
                self.UART_read(257)
                self.obj_serial.setDTR(False)   
                # END CONSTANTES DE MULTIPLICACAO


                # BEGIN SEGMENTOS HORARIOS
                self.tk_app.update_label(f'configura  o segmento de horarios')
                sleep(0.5)
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.UART_read(7)
                self.UART_send(b'\x35\x12\x34\x56\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x99\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x58\x69')                
                self.UART_read(257)
                self.obj_serial.setDTR(False)   
                # END SEGMENTOS HORARIOS

                # BEGIN HORA
                self.tk_app.update_label(f'configura  a hora ')
                sleep(0.5)
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.UART_read(7)
                self.UART_send(msg_hour)  # hora    
                # self.UART_send(b'\x30\x12\x34\x56\x02\x50\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xBE\x5F')                
                self.UART_read(257)
                self.obj_serial.setDTR(False)   
                # END HORA
                
                # Display : energia ativa  [1,2,3,24,32,33]
                if eqm_display_type == 1 and bol_config_display:
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : energia ativa')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x88\x01\x45\x02\x46\x03\x47\x04\x48\x49\x06\x08\x09\x90\x91\x92\x93\x50\x51\x52\x53\x10\x54\x55\x12\x56\x57\x14\x58\x15\x59\x16\xAF\x17\x19\x60\x61\x62\x63\x64\x21\x65\x22\x66\x23\x67\x24\x68\x25\x69\x27\x29\x70\x71\x72\x73\x30\x74\x00\x55\xFA')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : energia ativa')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x31\x75\x32\x76\x33\x77\x34\x78\x35\x79\x36\x37\x38\x39\x80\x81\x82\x83\x40\x84\x41\x85\x86\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x78\xCC')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : energia ativa')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x01\x01\x02\x03\x24\x32\x33\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xB4\x71')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END             

                #  CLIENTE  2,5
                if eqm_display_type == 2 and bol_config_display:
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : cliente 2,5')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x88\x01\x45\x02\x46\x03\x47\x04\x48\x49\x06\x08\x09\x90\x91\x92\x93\x50\x51\x52\x53\x10\x54\x55\x12\x56\x57\x14\x58\x15\x59\x16\xAF\x17\x19\x60\x61\x62\x63\xFC\x64\x21\x65\x22\x66\x23\x67\x24\x68\x25\x69\x27\x29\x70\x71\x72\x73\x30\x00\x60\xC0')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : cliente 2,5')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x74\x31\x75\x32\x76\x33\x77\x34\x78\x35\x79\x36\x37\x38\x39\x80\x81\x82\x83\x40\x84\x41\x85\x86\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xD0')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : cliente 2,5')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x01\x01\x02\x03\x24\x32\x33\x65\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x57')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END

                # SOLAR 
                if eqm_display_type == 3 and bol_config_display:
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x88\x01\x45\x02\x46\x03\x47\x04\x48\x49\x06\x08\x09\x90\x91\x92\x93\x50\x51\x52\x53\x10\x54\x55\x12\x56\x57\x14\x58\x15\x59\x16\xAF\x17\x19\x60\x61\x62\x63\x64\x21\x65\x22\x66\x23\x67\x24\x68\x25\x69\x27\x29\x70\x71\x72\x73\x30\x74\x00\x55\xFA')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x31\x75\x32\x76\x33\x77\x34\x78\x35\x79\x36\x37\x38\x39\x80\x81\x82\x83\x40\x84\x41\x85\x86\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x78\xCC')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x01\x01\x02\x03\x24\x32\x33\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xB1\xBD')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x01\x01\x02\x03\x04\x08\x10\x14\x16\x17\x21\x23\x24\x25\x29\x32\x33\x52\x53\x54\x57\x66\x68\x69\x71\x73\x75\x93\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xCA\x86')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                
                # SOLAR 01_02_03_24_33_55_65
                if eqm_display_type == 4 and bol_config_display:
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar 01_02_03_24_33_55_65 ')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x88\x01\x45\x02\x46\x03\x47\x04\x48\x49\x06\x08\x09\x90\x91\x92\x93\x50\x51\x52\x53\x10\x54\x55\x12\x56\x57\x14\x58\x15\x59\x16\xAF\x17\x19\x60\x61\x62\x63\x64\x21\x65\x22\x66\x23\x67\x24\x68\x25\x69\x27\x29\x70\x71\x72\x73\x30\x74\x00\x55\xFA')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar 01_02_03_24_33_55_65')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x00\x31\x75\x32\x76\x33\x77\x34\x78\x35\x79\x36\x37\x38\x39\x80\x81\x82\x83\x40\x84\x41\x85\x86\x43\x87\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x78\xCC')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END
                    # BEGIN
                    self.tk_app.update_label(f'configura Display : solar 01_02_03_24_33_55_65')
                    sleep(0.5)
                    self.obj_serial.setDTR(True)   
                    sleep(1)
                    self.UART_read(7)
                    self.UART_send(b'\x79\x12\x34\x56\x01\x01\x02\x03\x24\x33\x55\x65\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xBA\xEE')
                    self.UART_read(257)
                    self.obj_serial.setDTR(False)   
                    # END


                # BEGIN INICIALIZACAO
                self.tk_app.update_label(f'INICIALIZA O MEDIDOR')
                sleep(0.5)
                self.obj_serial.setDTR(True)   
                sleep(1)
                self.UART_read(7)
                self.UART_send(b'\x38\x12\x34\x56\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x47\x50')                
                self.UART_read(257)
                self.obj_serial.setDTR(False)   
                # END INICIALIZACAO


                self.tk_app.update_label(f'VERIFICA O MEDIDOR')
                sleep(6)

                if self.optical_reading_code(code=14):
                    self.tk_app.update_label(f'MEDIDOR RESETADO COM SUCESSO')
                   
                else:
                    self.tk_app.update_label(f'OCORREU ALGUMA FALHA NO MEDIDOR ')
                    sleep(0.4)
                    self.tk_app.update_label(f'INICIANDO O PROCESSO NOVAMENTE')
                    self.set01file_ares8023(eqm_display_type)


        except Exception as err:
            _, _, exception_traceback = exc_info()
            self.raise_or_print(line_number=int(exception_traceback.tb_lineno),err=str(err))


