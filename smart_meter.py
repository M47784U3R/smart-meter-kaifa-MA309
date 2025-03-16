import os
from gurux_dlms.GXByteBuffer import GXByteBuffer
import serial
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from binascii import unhexlify
import sys
import string
import paho.mqtt.client as mqtt
from gurux_dlms.GXDLMSTranslator import GXDLMSTranslator
from gurux_dlms.GXDLMSTranslatorMessage import GXDLMSTranslatorMessage
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler, MemoryHandler
import traceback
from datetime import datetime
from pathlib import Path


class SmartMeter:
    LOGGING_DISABLED = "Logging disabled"

    # @var str key: The key that is provided by the operator (e.g. EVN)
    __smart_meter_key: str
    # @var str com_port: Name of the com port that is used for connecting to the smart meter
    __com_port: str
    # @var bool verbose_mode: Activates/disables the debug mode. Default: false
    __verbose_mode: bool = False
    # @var Logger info_logger: Log file used for storing informational logs
    __info_logger: logging.Logger = None
    # @var Logger error_logger: Log file used for storing error logs
    __error_logger: logging.Logger = None
    # @var Serial serial_connection Connection to the USB dongle that is connected to the smart meter
    __serial_connection: serial.Serial

    def __init__(self, key: str, com_port: str, log_path: str = None, verbose: bool = False):
        """
        Initializes the SmartMeter class and sets the required values to connect to the smart meter and read out its data

        @param str key: The key that is provided by the operator (e.g. EVN)
        @param str com_port: Name of the com port that is used for connecting to the smart meter
        @param str log_path: defines the path that is used for storing the SmartMeter logs. Logging is disabled if
        not set.
        @param bool verbose: Activates/disables the verbose mode. Default: false
        @return: self
        """
        self.__smart_meter_key = key
        self.__com_port = com_port
        self.__verbose_mode = verbose
        self.__validate_variables()
        self.__init_logging(log_path)
        self.__log_info("SmartMeter started")
        # self.__connect_to_com_device()
        return None

    def __validate_variables(self):
        return

    def __add_trailing_slash(self, path: str) -> str:
        return os.path.join(path, '')

    def __init_logging(self, log_path):
        if log_path is None:
            print(self.LOGGING_DISABLED)
        else:

            if self.__validate_path(log_path):
                error_handler = logging.FileHandler(self.__add_trailing_slash(log_path) + "error.log")
                error_handler.setLevel(logging.ERROR)

                formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                if self.__verbose_mode:
                    console_handler = logging.StreamHandler()
                    console_handler.setFormatter(formatter)

                error_handler.setFormatter(formatter)

                self.__error_logger = logging.getLogger('error')
                self.__error_logger.setLevel(logging.ERROR)
                self.__error_logger.addHandler(error_handler)
                if self.__verbose_mode:
                    print("init console logging")
                    self.__error_logger.addHandler(console_handler)

                info_handler = logging.handlers.TimedRotatingFileHandler(
                    self.__add_trailing_slash(log_path) + "info.log",
                    when="midnight",
                    interval=1,
                    backupCount=14
                )
                info_handler.setLevel(logging.INFO)

                info_handler.setFormatter(formatter)

                self.__info_logger = logging.getLogger('info')
                self.__info_logger.setLevel(logging.INFO)
                self.__info_logger.addHandler(info_handler)

                if self.__verbose_mode:
                    print("init console logging")
                    self.__info_logger.addHandler(console_handler)

    def __connect_to_com_device(self):
        try:
            __serial_connection = serial.Serial(
                port=self.__com_port,
                baudrate=2400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE
            )
            print(__serial_connection)
        except Exception as e:
            print(e)

    def __validate_path(self, log_path) -> bool:
        path = Path(log_path)
        if not os.path.exists(path):
            raise FileNotFoundError("The specified path '" + log_path + "' does not exist")
        if not path.is_dir() or not os.access(path, os.W_OK):
            raise PermissionError("The specified path '" + log_path + "' is not accessible")
        return True

    def __log_error(self, message: string) -> None:
        if self.__error_logger is not None:
            self.__error_logger.error(message + traceback.format_exc())

    def __log_info(self, message: string) -> None:
        print("LOGGING INFO")
        if self.__info_logger is not None:
            print("LOG INFO: " + message)
            self.__info_logger.info(message)

'''
# EVN Schlüssel eingeben zB. "36C66639E48A8CA4D6BC8B282A793BBB"
evn_schluessel = smart_meter_key

# MQTT Verwenden (True | False)
useMQTT = False

# MQTT Broker IP adresse Eingeben ohne Port!
mqttBroker = "192.168.1.10"
mqttuser = ""
mqttpasswort = ""
# Aktuelle Werte auf Console ausgeben (True | False)
printValue = debug_mode

# MQTT Init
if useMQTT:
    try:
        client = mqtt.Client("SmartMeter")
        client.username_pw_set(mqttuser, mqttpasswort)
        client.connect(mqttBroker, port=1883)
    except:
        print("Die Ip Adresse des Brokers ist falsch!")
        sys.exit()

tr = GXDLMSTranslator()
tr.blockCipherKey = GXByteBuffer(evn_schluessel)
tr.comments = True
ser = serial.Serial(port=comport,
                    baudrate=2400,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    )

while 1:
    daten = ser.read(size=282).hex()
    print(daten)

    msg = GXDLMSTranslatorMessage()
    msg.message = GXByteBuffer(daten)
    xml = ""
    pdu = GXByteBuffer()
    tr.completePdu = True
    while tr.findNextFrame(msg, pdu):
        pdu.clear()
        xml += tr.messageToXml(msg)

    soup = BeautifulSoup(xml, 'html5lib')

    results_32 = soup.find_all('uint32')
    results_16 = soup.find_all('uint16')
    # print(results_16)

    # Wirkenergie A+ in Wattstunden
    WirkenergieP = int(str(results_32)[16:16 + 8], 16)

    # Wirkenergie A- in Wattstunden
    WirkenergieN = int(str(results_32)[52:52 + 8], 16)

    # Momentanleistung P+ in Watt
    MomentanleistungP = int(str(results_32)[88:88 + 8], 16)

    # Momentanleistung P- in Watt
    MomentanleistungN = int(str(results_32)[124:124 + 8], 16)

    # Spannung L1 in Volt
    SpannungL1 = int(str(results_16)[16:20], 16) / 10

    # Spannung L2 in Volt
    SpannungL2 = int(str(results_16)[48:52], 16) / 10

    # Spannung L3 in Volt
    SpannungL3 = int(str(results_16)[80:84], 16) / 10

    # Strom L1 in Ampere
    StromL1 = int(str(results_16)[112:116], 16) / 100

    # Strom L2 in Ampere
    StromL2 = int(str(results_16)[144:148], 16) / 100

    # Strom L3 in Ampere
    StromL3 = int(str(results_16)[176:180], 16) / 100

    # Leistungsfaktor
    Leistungsfaktor = int(str(results_16)[208:212], 16) / 1000

    if printValue:
        print('Wirkenergie+: ' + str(WirkenergieP))
        print('Wirkenergie: ' + str(WirkenergieN))
        print('MomentanleistungP+: ' + str(MomentanleistungP))
        print('MomentanleistungP-: ' + str(MomentanleistungN))
        print('Spannung L1: ' + str(SpannungL1))
        print('Spannung L2: ' + str(SpannungL2))
        print('Spannung L3: ' + str(SpannungL3))
        print('Strom L1: ' + str(StromL1))
        print('Strom L2: ' + str(StromL2))
        print('Strom L3: ' + str(StromL3))
        print('Leistungsfaktor: ' + str(Leistungsfaktor))
        print('Momentanleistung: ' + str(MomentanleistungP - MomentanleistungN))
        print()
        print()

    # MQTT
    if useMQTT:
        connected = False
        while not connected:
            try:
                client.reconnect()
                connected = True
            except:
                print("Lost Connection to MQTT...Trying to reconnect in 2 Seconds")
                time.sleep(2)

        client.publish("Smartmeter/WirkenergieP", WirkenergieP)
        client.publish("Smartmeter/WirkenergieN", WirkenergieN)
        client.publish("Smartmeter/MomentanleistungP", MomentanleistungP)
        client.publish("Smartmeter/MomentanleistungN", MomentanleistungN)
        client.publish("Smartmeter/Momentanleistung", MomentanleistungP - MomentanleistungN)
        client.publish("Smartmeter/SpannungL1", SpannungL1)
        client.publish("Smartmeter/SpannungL2", SpannungL2)
        client.publish("Smartmeter/SpannungL3", SpannungL3)
        client.publish("Smartmeter/StromL1", StromL1)
        client.publish("Smartmeter/StromL2", StromL2)
        client.publish("Smartmeter/StromL3", StromL3)
        client.publish("Smartmeter/Leistungsfaktor", Leistungsfaktor)
    # except BaseException as err:
    #   print("Fehler beim Synchronisieren. Programm bitte ein weiteres mal Starten.")
    #   print()
    #   print("Fehler: ", format(err))

    #   sys.exit()
'''
