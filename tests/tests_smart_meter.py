import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from smart_meter import SmartMeter


class TestSmartMeter(unittest.TestCase):

    @patch('os.path.exists')
    def test_check_path_not_exist(self, mock_exists):
        mock_path = '/mock/path'
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            SmartMeter('key', 'USB', mock_path, False)

        mock_exists.assert_called_with(Path(mock_path))

    @patch('os.path.exists')
    @patch('os.access')
    def test_check_path_not_accessible(self, mock_access, mock_exists):
        mock_path = '/mock/path'
        mock_exists.return_value = True
        mock_access.return_value = False

        with self.assertRaises(PermissionError):
            SmartMeter('key', 'USB', mock_path, False)

        mock_exists.assert_called_with(Path(mock_path))
        mock_access.assert_called_with(Path(mock_path), os.R_OK)

    def test_dummy(self):
        smart_meter = SmartMeter('key', 'USB', None, False)
        self.assertEqual(True, True)
        pass

    @patch('gurux_dlms.GXByteBuffer.GXByteBuffer')
    @patch('serial.Serial')
    @patch('time.sleep')
    @patch('cryptography.hazmat.primitives.ciphers.aead.AESGCM')
    @patch('binascii.unhexlify')
    @patch('sys.exit')
    @patch('string.ascii_letters')
    @patch('paho.mqtt.client.Client')
    @patch('gurux_dlms.GXDLMSTranslator.GXDLMSTranslator')
    @patch('gurux_dlms.GXDLMSTranslatorMessage.GXDLMSTranslatorMessage')
    @patch('bs4.BeautifulSoup')
    @patch('os.getenv')
    @patch('dotenv.load_dotenv')
    def test_init_variables(self, mock_load_dotenv, mock_getenv, mock_BeautifulSoup, mock_GXDLMSTranslatorMessage,
                            mock_GXDLMSTranslator,
                            mock_Client, mock_asciiletters, mock_exit, mock_unhexlify, mock_AESGCM, mock_sleep,
                            mock_Serial, mock_GXByteBuffer):
        mock_buffer = MagicMock()
        mock_GXByteBuffer.return_value = mock_buffer

        mock_serial = MagicMock()
        mock_Serial.return_value = mock_serial

        mock_sleep.return_value = None

        mock_aes = MagicMock()
        mock_AESGCM.return_value = mock_aes

        mock_unhexlify.return_value = b'mock data'

        mock_exit.return_value = None

        mock_asciiletters.return_value = "abcdefghijklmnopqrstuvwxyz"

        mock_mqtt = MagicMock()
        mock_Client.return_value = mock_mqtt

        mock_translator = MagicMock()
        mock_GXDLMSTranslator.return_value = mock_translator

        mock_translator_message = MagicMock()
        mock_GXDLMSTranslatorMessage.return_value = mock_translator_message

        mock_soup = MagicMock()
        mock_BeautifulSoup.return_value = mock_soup

        mock_getenv.return_value = "mock_value"

        mock_load_dotenv.return_value = None

        self.assertEqual(True, True)
        mock_GXByteBuffer.assert_called_once()
        mock_Serial.assert_called_once()
        mock_sleep.assert_called_once()
        mock_AESGCM.assert_called_once()
        mock_unhexlify.assert_called_once()
        mock_exit.assert_called_once()
        mock_asciiletters.assert_called_once()
        mock_Client.assert_called_once()
        mock_GXDLMSTranslator.assert_called_once()
        mock_GXDLMSTranslatorMessage.assert_called_once()
        mock_BeautifulSoup.assert_called_once()
        mock_getenv.assert_called_once()
        mock_load_dotenv.assert_called_once()


if __name__ == '__main__':
    unittest.main()
