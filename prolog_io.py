__author__ = "cloudstrife9999"

from pwn import process
from printer import print_exception_maybe
from common import global_config
from strings import *

class PrologIO():
    def __init__(self, cmd):
        if isinstance(cmd, list):
            self.__cmd: list = cmd
        elif isinstance(cmd, str):
            self.__cmd: list = cmd.split(" ")
        else:
            raise ValueError("Unsupported command type: {}".format(type(cmd)))

        self.__proc: process = None
        self.__timeout: int = self.__validate_timeout()

    def __validate_timeout(self) -> int:
        timeout: int = global_config[timeout_key]

        if not isinstance(timeout, (int, float)) or timeout < 0:
            raise ValueError("{} is not a valid timeout value.")
        else:
            return timeout

    # This is for a potential concurrent-friendly re-implementation in the future.
    def start(self) -> None:
        self.run()

    def stop(self) -> None:
        self.__proc.kill()

    def restart(self) -> None:
        self.stop()
        self.start()
    
    def run(self) -> None:
        try:
            self.__proc = process(self.__cmd)

            # This command tells swipl not to abbreviate its output anymore.
            self.__proc.sendline("set_prolog_flag(answer_write_options,[quoted(true), portray(true), spacing(next_argument)]).")

            # We always want to discard the swipl header message.
            self.__receive_and_discard()
        except Exception:
            print_exception_maybe()

    def stop(self) -> None:
        self.__proc.kill()

    def __recv_utf8_str(self) -> str:
        output = self.__proc.recv(timeout=self.__timeout)
        to_return: str = str(output, "utf-8")

        if to_return == "":
            raise TimeoutError()
        else:
            return to_return
    
    def send_and_receive(self, to_send: str):
        if self.__proc is None:
            raise ValueError("The process has not been initialised yet.")

        try:
            return self.__send_and_receive(to_send=to_send)
        except Exception as e:
            print_exception_maybe()
            return "ERROR: got {} while running".format(str(e))

    def __send_and_receive(self, to_send: str):
        if to_send.endswith("\n"):
            self.__proc.send(to_send)
        else:
            self.__proc.sendline(to_send)

        return self.__receive_data()

    def __receive_data(self):
        try:
            self.__receive_and_discard_optional_data()

            return self.__recv_utf8_str()
        except SyntaxError as e:
            self.restart()

            return str(e)
        except TimeoutError:
            self.restart()

            return ""

    def __receive_and_discard_optional_data(self) -> None:
        while True:
            tmp = self.__recv_utf8_str()

            for error_pattern in global_config[error_patterns_key]:
                if error_pattern in tmp:
                    raise SyntaxError(tmp)
            
            if not self.__must_receive_again(data=tmp):
                self.__proc.unrecv(tmp)
                break

    def __must_receive_again(self, data: str) -> bool:
        for elm in global_config[keep_receiving_if_received_key]:
            if elm in data:
                return True
        
        return False

    def __receive_and_discard(self) -> None:
        self.__recv_utf8_str()
