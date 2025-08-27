import _io
from unittest.mock import patch, MagicMock
from unittest import TestCase
import io
import re

from argenta.app import App
from argenta.command import Command
from argenta.response import Response
from argenta.router import Router
from argenta.orchestrator import Orchestrator
from argenta.command.flag import Flag
from argenta.command.flag.flags import Flags
from argenta.command.flag.defaults import PredefinedFlags



class TestSystemHandlerNormalWork(TestCase):
    @patch("builtins.input", side_effect=["test", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()

        @router.command(Command('test'))
        def test(response):
            print('test command')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\ntest command\n', output)


    @patch("builtins.input", side_effect=["TeSt", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command2(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()

        @router.command(Command('test'))
        def test(response):
            print('test command')

        app = App(ignore_command_register=True,
                  override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\ntest command\n', output)


    @patch("builtins.input", side_effect=["test --help", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command_with_custom_flag(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()
        flag = Flag('help', '--', False)

        @router.command(Command('test', flags=flag))
        def test(response: Response):
            print(f'\nhelp for {response.valid_flags.get_flag('help').get_name()} flag\n')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\nhelp for help flag\n', output)

    @patch("builtins.input", side_effect=["test --port 22", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command_with_custom_flag2(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()
        flag = Flag('port', '--', re.compile(r'^\d{1,5}$'))

        @router.command(Command('test', flags=flag))
        def test(response: Response):
            input_flag = response.valid_flags.get_flag('port')
            print(f'flag value for {input_flag.get_name()} flag : {input_flag.get_value()}')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\nflag value for port flag : 22\n', output)


    @patch("builtins.input", side_effect=["test -H", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command_with_default_flag(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()
        flag = PredefinedFlags.SHORT_HELP

        @router.command(Command('test', flags=flag))
        def test(response: Response):
            print(f'help for {response.valid_flags.get_flag('H').get_name()} flag')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\nhelp for H flag\n', output)


    @patch("builtins.input", side_effect=["test --info", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command_with_default_flag2(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()
        flag = PredefinedFlags.INFO

        @router.command(Command('test', flags=flag))
        def test(response: Response):
            if response.valid_flags.get_flag('info'):
                print('info about test command')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\ninfo about test command\n', output)


    @patch("builtins.input", side_effect=["test --host 192.168.0.1", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command_with_default_flag3(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()
        flag = PredefinedFlags.HOST

        @router.command(Command('test', flags=flag))
        def test(response: Response):
            print(f'connecting to host {response.valid_flags.get_flag('host').get_value()}')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\nconnecting to host 192.168.0.1\n', output)


    @patch("builtins.input", side_effect=["test --host 192.168.32.1 --port 132", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_correct_command_with_two_flags(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()
        flags = Flags(PredefinedFlags.HOST, PredefinedFlags.PORT)

        @router.command(Command('test', flags=flags))
        def test(response: Response):
            valid_flags = response.valid_flags
            print(f'connecting to host {valid_flags.get_flag('host').get_value()} and port {valid_flags.get_flag('port').get_value()}')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertIn('\nconnecting to host 192.168.32.1 and port 132\n', output)


    @patch("builtins.input", side_effect=["test", "some", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_two_correct_command(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()

        @router.command(Command('test'))
        def test(response):
            print(f'test command')

        @router.command(Command('some'))
        def test2(response):
            print(f'some command')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertRegex(output, re.compile(r'\ntest command\n(.|\n)*\nsome command\n'))


    @patch("builtins.input", side_effect=["test", "some", "more", "q"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_input_three_correct_command(self, mock_stdout: _io.StringIO, magick_mock: MagicMock):
        router = Router()
        orchestrator = Orchestrator()

        @router.command(Command('test'))
        def test(response):
            print(f'test command')

        @router.command(Command('some'))
        def test(response):
            print(f'some command')

        @router.command(Command('more'))
        def test(response):
            print(f'more command')

        app = App(override_system_messages=True,
                  print_func=print)
        app.include_router(router)
        orchestrator.start_polling(app)

        output = mock_stdout.getvalue()

        self.assertRegex(output, re.compile(r'\ntest command\n(.|\n)*\nsome command\n(.|\n)*\nmore command'))
