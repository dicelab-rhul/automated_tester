__author__ = "cloudstrife9999"

from pwn import process
from printer import print_exception


class PrologIO():
    def __init__(self, cmd, timeout: int):
        if type(cmd) == list:
            self.__cmd = cmd
        elif type(cmd) == str:
            self.__cmd = cmd.split(" ")
        else:
            raise ValueError("Unsupported command type: {}".format(type(cmd)))

        if type(timeout) != int or timeout < 0:
            raise ValueError("{} is not a valid timeout value.")

        self.__proc: process = None
        self.__timeout: int = timeout


    # This is for a potential concurrent-friendly re-implementation in the future.
    def start(self) -> None:
        self.run()
    
    def run(self) -> None:
        try:
            self.__proc = process(self.__cmd)

            # This command tells swipl not to abbreviate its output anymore.
            self.__proc.sendline("set_prolog_flag(answer_write_options,[quoted(true), portray(true), spacing(next_argument)]).")

            self.__receive_and_discard()
        except Exception:
            # TODO: is this the right/only thing to do?
            print_exception()

    def stop(self) -> None:
        self.__proc.kill()

    def __recv_utf8_str(self) -> str:
        output = self.__proc.recv(timeout=self.__timeout)
        to_return: str = str(output, "utf-8")

        if to_return == "":
            raise TimeoutError()
        else:
            return to_return
    
    def send_and_receive(self, to_send: str, keep_receiving_if_received: list, error_patterns: list=["ERROR:"]):
        if self.__proc is None:
            raise ValueError("The process has not been initialised yet.")

        try:
            return self.__send_and_receive(to_send=to_send, keep_receiving_if_received=keep_receiving_if_received, error_patterns=error_patterns)
        except Exception as e:
            # TODO: is this the right/only thing to do?
            print_exception()
            return "Got {} while running".format(e)

    def __send_and_receive(self, to_send: str, keep_receiving_if_received: list, error_patterns: list):
        if to_send.endswith("\n"):
            self.__proc.send(to_send)
        else:
            self.__proc.sendline(to_send)

        return self.__receive_data(keep_receiving_if_received=keep_receiving_if_received, error_patterns=error_patterns)

    def __receive_data(self, keep_receiving_if_received: list, error_patterns: list):
        try:
            self.__receive_and_discard_optional_data(keep_receiving_if_received=keep_receiving_if_received, error_patterns=error_patterns)

            return self.__recv_utf8_str()
        except SyntaxError as e:
            self.__kill_and_restart_swipl()

            return str(e)
        except TimeoutError:
            self.__kill_and_restart_swipl()

            return ""

    def __receive_and_discard_optional_data(self, keep_receiving_if_received: list, error_patterns: list) -> None:
        while True:
            tmp = self.__recv_utf8_str()

            for error_pattern in error_patterns:
                if error_pattern in tmp:
                    raise SyntaxError(tmp)
            
            if not self.__must_receive_again(data=tmp, keep_receiving_if_received=keep_receiving_if_received):
                self.__proc.unrecv(tmp)
                break

    def __must_receive_again(self, data: str, keep_receiving_if_received: list) -> bool:
        for elm in keep_receiving_if_received:
            if elm in data:
                return True
        
        return False


    def __receive_and_discard(self) -> None:
        self.__recv_utf8_str()


    def __kill_and_restart_swipl(self) -> None:
        self.__proc.kill()
        self.start()
