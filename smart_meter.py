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
from logging.handlers import TimedRotatingFileHandler
import traceback
from datetime import datetime
from pathlib import Path


class SmartMeter:

    # @param string key: The key that is provided by the operator (e.g. EVN)
    __smart_meter_key: string
    # @param string com_port: Name of the com port that is used for connecting to the smart meter
    __com_port: string
    # @param string log_path: defines the path that is used for storing the SmartMeter logs. Logging is disabled if
    #                         not set.
    __log_file_path: string = None
    # @param bool debug: Activates/disables the debug mode. Default: false
    __debug_mode: bool = False

    def __init__(self, key: string, com_port: string, log_path: string = None, debug: bool = False):
        """
        Initializes the SmartMeter class and sets the required values to connect to the smart meter and read out its data

        @param string key: The key that is provided by the operator (e.g. EVN)
        @param string com_port: Name of the com port that is used for connecting to the smart meter
        @param string log_path: defines the path that is used for storing the SmartMeter logs. Logging is disabled if
        not set.
        @param bool debug: Activates/disables the debug mode. Default: false
        @return: None
        """
        self.__smart_meter_key = key
        self.__com_port = com_port
        self.__log_file_path = log_path
        self.__debug_mode = debug
        self.__validate_variables()
        return

    def __validate_variables(self):
        print([self.__smart_meter_key, self.__debug_mode, self.__log_file_path, self.__com_port])
        self.__init_logging()
        self.__connect_to_com_device()
        return

    def __init_logging(self):
        if self.__log_file_path is None:
            print("Logging disabled")
        else:

            if self.__validate_path():

                # --- ERROR LOGGING (nicht löschen) ---
                # Fehler-Log in einem spezifischen Verzeichnis speichern
                error_handler = logging.FileHandler("error.log")  # Fehler-Logs in eine Datei schreiben
                error_handler.setLevel(logging.ERROR)

                # Formatierung der Fehler-Logs
                error_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                error_handler.setFormatter(error_formatter)

                # Logger für Fehler
                error_logger = logging.getLogger('error')
                error_logger.setLevel(logging.ERROR)
                error_logger.addHandler(error_handler)

                # --- INFO LOGGING (täglich rotieren, 14 Tage behalten) ---
                info_handler = TimedRotatingFileHandler(
                    "info_logs.log",  # Basis-Dateiname für Info-Logs
                    when="midnight",  # Tägliche Rotation um Mitternacht
                    interval=1,  # Alle 1 Tag rotieren
                    backupCount=14  # Maximal 14 Tage aufbewahren
                )
                info_handler.setLevel(logging.INFO)

                # Formatierung der Info-Logs
                info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
                info_handler.setFormatter(info_formatter)

                # Logger für Info
                info_logger = logging.getLogger('info')
                info_logger.setLevel(logging.INFO)
                info_logger.addHandler(info_handler)

                # --- Beispiel für Log-Erstellung ---
                try:
                    x = 1 / 0  # Beispiel für einen Fehler (Division durch 0)
                except Exception as e:
                    # Error-Log mit Traceback
                    error_logger.error("Fehler aufgetreten:\n" + traceback.format_exc())  # Traceback hinzufügen

                info_logger.info("Info-Log: Programm gestartet.")  # Info-Log

                print("Logging to path: " + self.__log_file_path)

    def __connect_to_com_device(self):
        try:
            ser = serial.Serial(port=self.__com_port,
                                baudrate=2400,
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE,
                                )
            print(ser)
        except Exception as e:
            print(e)

    def __validate_path(self):
        path = Path(self.__log_file_path)
        if not os.path.exists(path):
            raise FileNotFoundError("The specified path '" + self.__log_file_path + "' does not exist")
        if not path.is_dir() or not os.access(path, os.W_OK):
            raise PermissionError("The specified path '" + self.__log_file_path + "' is not accessible")
        return True


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