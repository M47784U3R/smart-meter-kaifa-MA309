import io
import logging
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from smart_meter import SmartMeter


class TestSmartMeter(unittest.TestCase):

    def test_check_loging_disabled(self):
        with patch("logging.getLogger") as mock_get_logger:
            mock_info_logger = MagicMock()
            mock_error_logger = MagicMock()

            def get_logger_side_effect(name):
                if name == "info":
                    return mock_info_logger
                elif name == "error":
                    return mock_error_logger
                return MagicMock()

            mock_get_logger.side_effect = get_logger_side_effect

            SmartMeter('key', 'USB', None, False)

            mock_get_logger.assert_any_call("info")
            mock_get_logger.assert_any_call("error")

            self.assertIsInstance(mock_info_logger.info.call_args_list, (list, tuple))
            self.assertIsNotNone(mock_info_logger.info.call_args_list[0][0][0])
            self.assertEqual(mock_info_logger.info.call_args_list[0][0][0], SmartMeter.LOGGING_DISABLED)

    @patch('os.path.exists')
    def test_check_log_path_does_not_exist(self, mock_exists):
        mock_path = '/mock/path'
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            SmartMeter('key', 'USB', mock_path, False)

        mock_exists.assert_called_with(Path(mock_path))

    @patch('pathlib.Path.is_dir')
    @patch('os.path.exists')
    @patch('os.access')
    def test_check_log_path_not_accessible(self, mock_access, mock_exists, mock_is_dir):
        mock_path = '/mock/path'
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_access.return_value = False

        with self.assertRaises(PermissionError):
            SmartMeter('key', 'USB', mock_path, False)

        mock_exists.assert_called_with(Path(mock_path))
        mock_is_dir.assert_called()
        mock_access.assert_called_with(Path(mock_path), os.W_OK)

    def test_check_log_path_exists_and_accessible(self):
        mock_path = '/mock/path'
        mocks = self.mock_logging()
        mock_file_handler = mocks["file_handler"]
        mock_timed_handler = mocks["timed_handler"]
        mock_exists = mocks["exists"]
        mock_access = mocks["access"]
        mock_is_dir = mocks["is_dir"]

        SmartMeter('key', 'USB', mock_path, False)

        mock_exists.assert_called_with(Path(mock_path))
        mock_is_dir.assert_called()
        mock_access.assert_called_with(Path(mock_path), os.W_OK)

        mock_file_handler.assert_called_once_with(mock_path + "/error.log")

        mock_timed_handler.assert_called_once_with(
            mock_path + "/info.log",
            when="midnight",
            interval=1,
            backupCount=14
        )

        mocks["cleanup"]

    def test_check_verbose_mode_active(self):
        mock_path = '/mock/path'
        mocks = self.mock_logging()

        SmartMeter('key', 'USB', mock_path, True)

        mocks["cleanup"]

    def mock_logging(self):
        patchers = {
            "stream_handler": patch("logging.StreamHandler", MagicMock()),
            "file_handler": patch("logging.FileHandler", MagicMock()),
            "timed_handler": patch("logging.handlers.TimedRotatingFileHandler", MagicMock()),
            "is_dir": patch("pathlib.Path.is_dir", MagicMock(return_value=True)),
            "exists": patch("os.path.exists", MagicMock(return_value=True)),
            "access": patch("os.access", MagicMock(return_value=True))
        }

        mocks = {key: patcher.start() for key, patcher in patchers.items()}
        mocks["file_handler_instance"] = mocks["file_handler"].return_value
        mocks["file_handler_instance"].level = logging.ERROR

        mocks["timed_handler_instance"] = mocks["timed_handler"].return_value
        mocks["timed_handler_instance"].level = logging.INFO

        mocks["stream_handler_instance"] = mocks["stream_handler"].return_value
        mocks["stream_handler_instance"].level = logging.INFO

        def cleanup():
            for patcher in patchers.values():
                patcher.stop()

        mocks["cleanup"] = cleanup

        return mocks

    @patch('gurux_dlms.GXByteBuffer')
    @patch('serial.Serial')
    @patch('time.sleep')
    @patch('cryptography.hazmat.primitives.ciphers.aead.AESGCM')
    @patch('binascii.unhexlify')
    @patch('sys.exit')
    @patch('string.ascii_letters')
    @patch('paho.mqtt.client.Client')
    @patch('gurux_dlms.GXDLMSTranslator')
    @patch('gurux_dlms.GXDLMSTranslatorMessage')
    @patch('bs4.BeautifulSoup')
    @patch('os.getenv')
    @patch('dotenv.load_dotenv')
    def test_init_variables(self, mock_load_dotenv, mock_getenv, mock_BeautifulSoup, mock_GXDLMSTranslatorMessage,
                            mock_GXDLMSTranslator,
                            mock_Client, mock_asciiletters, mock_exit, mock_unhexlify, mock_AESGCM, mock_sleep,
                            mock_Serial, mock_GXByteBuffer):
        '''
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
        '''


if __name__ == '__main__':
    unittest.main()
