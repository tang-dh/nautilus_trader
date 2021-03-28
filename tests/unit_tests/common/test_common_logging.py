# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2021 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import asyncio
import os
import shutil

import pytest

from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.clock import TestClock
from nautilus_trader.common.logging import LiveLogger
from nautilus_trader.common.logging import LogColor
from nautilus_trader.common.logging import LogLevel
from nautilus_trader.common.logging import LogLevelParser
from nautilus_trader.common.logging import LogMessage
from nautilus_trader.common.logging import Logger
from nautilus_trader.common.logging import LoggerAdapter
from nautilus_trader.common.logging import TestLogger
from tests.test_kit.stubs import UNIX_EPOCH


class TestLogLevelParser:
    @pytest.mark.parametrize(
        "enum,expected",
        [
            [LogLevel.VERBOSE, "VRB"],
            [LogLevel.DEBUG, "DBG"],
            [LogLevel.INFO, "INF"],
            [LogLevel.WARNING, "WRN"],
            [LogLevel.ERROR, "ERR"],
            [LogLevel.CRITICAL, "CRT"],
            [LogLevel.FATAL, "FTL"],
        ],
    )
    def test_log_level_to_str(self, enum, expected):
        # Arrange
        # Act
        result = LogLevelParser.to_str_py(enum)

        # Assert
        assert result == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ["VRB", LogLevel.VERBOSE],
            ["DBG", LogLevel.DEBUG],
            ["INF", LogLevel.INFO],
            ["ERR", LogLevel.ERROR],
            ["CRT", LogLevel.CRITICAL],
            ["FTL", LogLevel.FATAL],
        ],
    )
    def test_log_level_from_str(self, string, expected):
        # Arrange
        # Act
        result = LogLevelParser.from_str_py(string)

        # Assert
        assert result == expected


class TestLoggerBase:
    def test_log_when_not_implemented_raises_not_implemented(self):
        # Arrange
        logger = Logger(clock=TestClock())

        # Act
        # Assert
        with pytest.raises(NotImplementedError):
            msg = LogMessage(
                timestamp=UNIX_EPOCH,
                level=LogLevel.INFO,
                color=LogColor.NORMAL,
                text="test message",
            )

            logger.log(msg)

    def test_setup_logger_log_to_file_with_no_path(self):
        # Arrange
        # Act
        logger = TestLogger(
            clock=TestClock(),
            level_console=LogLevel.VERBOSE,
            log_to_file=True,
        )

        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        logger_adapter.info("hello, world")

        # Assert
        assert os.path.isdir(logger.get_log_file_dir())
        assert os.path.exists(logger.get_log_file_path())
        assert logger.get_log_file_dir().endswith("log/")
        assert logger.get_log_file_path().endswith("tmp-1970-01-01.log")

        # Teardown
        shutil.rmtree(logger.get_log_file_dir())

    def test_setup_logger_log_to_file_given_path(self):
        # Arrange
        # Act
        logger = TestLogger(
            name="TEST",
            clock=TestClock(),
            level_console=LogLevel.VERBOSE,
            log_to_file=True,
            log_file_dir="log1/",
        )

        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        logger_adapter.info("hello, world")

        # Assert
        assert os.path.isdir(logger.get_log_file_dir())
        assert os.path.exists(logger.get_log_file_path())
        assert logger.get_log_file_dir().endswith("log1/")
        assert logger.get_log_file_path().endswith("TEST-1970-01-01.log")

        # Teardown
        shutil.rmtree(logger.get_log_file_dir())

    def test_change_log_file_name(self):
        # Arrange
        # Act
        logger = Logger(
            name="TEST",
            clock=TestClock(),
            level_console=LogLevel.VERBOSE,
            log_to_file=True,
            log_file_dir="log2/",
        )

        logger.change_log_file_name("TEST-1970-01-02")

        # Assert
        assert os.path.isdir(logger.get_log_file_dir())
        assert os.path.exists(logger.get_log_file_path())
        assert logger.get_log_file_dir().endswith("log2/")
        assert logger.get_log_file_path().endswith("TEST-1970-01-02.log")

        # Teardown
        shutil.rmtree(logger.get_log_file_dir())


class TestLoggerTests:
    def test_log_verbose_messages_to_console(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.VERBOSE)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.verbose("This is a log message.")

        # Assert
        assert True  # No exception raised

    def test_log_debug_messages_to_console(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.DEBUG)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.debug("This is a log message.")

        # Assert
        assert True  # No exception raised

    def test_log_info_messages_to_console(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.INFO)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.info("This is a log message.")

        # Assert
        assert True  # No exception raised

    def test_log_info_messages_to_console_with_blue_colour(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.INFO)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.info("This is a log message.", LogColor.BLUE)

        # Assert
        assert True  # No exception raised

    def test_log_info_messages_to_console_with_green_colour(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.INFO)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.info("This is a log message.", LogColor.GREEN)

        # Assert
        assert True  # No exception raised

    def test_log_info_messages_to_console_with_invalid_colour(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.INFO)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.info("This is a log message.", 30)

        # Assert
        assert True  # No exception raised

    def test_log_warning_messages_to_console(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.WARNING)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.warning("This is a log message.")

        # Assert
        assert True  # No exception raised

    def test_log_error_messages_to_console(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.ERROR)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.error("This is a log message.")

        # Assert
        assert True  # No exception raised

    def test_log_critical_messages_to_console(self):
        # Arrange
        logger = TestLogger(clock=TestClock(), level_console=LogLevel.CRITICAL)
        logger_adapter = LoggerAdapter("TEST_LOGGER", logger)

        # Act
        logger_adapter.critical("This is a log message.")

        # Assert
        assert True  # No exception raised


class TestLiveLogger:
    def setup(self):
        # Fresh isolated loop testing pattern
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.logger = LiveLogger(
            loop=self.loop,
            clock=LiveClock(),
        )

        self.logger_adapter = LoggerAdapter("LIVE_LOGGER", logger=self.logger)

    def test_log_when_not_running_on_event_loop_successfully_logs(self):
        # Arrange
        # Act
        self.logger_adapter.info("test message")

        # Assert
        assert True  # No exception raised

    def test_start_runs_on_event_loop(self):
        async def run_test():
            # Arrange
            self.logger.start()

            self.logger_adapter.info("A log message.")
            await asyncio.sleep(0)

            # Act
            # Assert
            assert self.logger.is_running
            self.logger.stop()

        self.loop.run_until_complete(run_test())

    def test_stop_when_running_stops_logger(self):
        async def run_test():
            # Arrange
            self.logger.start()

            self.logger_adapter.info("A log message.")
            await asyncio.sleep(0)

            # Act
            self.logger.stop()
            self.logger_adapter.info("A log message.")

            # Assert
            assert not self.logger.is_running

        self.loop.run_until_complete(run_test())

    def test_log_when_queue_over_maxsize_blocks(self):
        async def run_test():
            # Arrange
            logger = LiveLogger(
                loop=self.loop,
                clock=LiveClock(),
                maxsize=1,
            )

            logger_adapter = LoggerAdapter("LIVE_LOGGER", logger=logger)
            logger.start()

            # Act
            logger_adapter.info("A log message.")
            logger_adapter.info("A log message.")  # <-- blocks
            logger_adapter.info("A log message.")  # <-- blocks
            logger_adapter.info("A log message.")  # <-- blocks

            await asyncio.sleep(0.1)  # <-- processes all log messages
            self.logger.stop()

            # Assert
            assert not self.logger.is_running

        self.loop.run_until_complete(run_test())
