from pwn import process
from traceback import print_exc
from sys import stdout


class PrologIO():
    def __init__(self, cmd, timeout):
        if type(cmd) == list:
            self.__cmd = cmd
        elif type(cmd) == str:
            self.__cmd = cmd.split(" ")
        else:
            raise ValueError("Unsupported command type: {}".format(type(cmd)))

        if timeout < 0:
            raise ValueError("{} is not a valid value for a timeout.")

        self.__proc: process = None
        self.__timeout: int = timeout

    
    def run(self) -> None:
        try:
            self.__proc = process(self.__cmd)
            self.__proc.sendline("set_prolog_flag(answer_write_options,[quoted(true), portray(true), spacing(next_argument)]).")
            self.__receive_and_discard()
        except Exception:
            # TODO: maybe remove this?
            print_exc(file=stdout)

    def stop(self) -> None:
        self.__proc.kill()

    def __recv_utf8_str(self) -> str:
        output = self.__proc.recv(timeout=self.__timeout)
        to_return: str = str(output, "utf-8")

        if to_return == "":
            raise TimeoutError()
        else:
            return to_return
    
    def send_and_receive(self, to_send: str, keep_receiving_if_received: list):
        if self.__proc is None:
            raise ValueError("The process has not been initialised yet.")

        try:
            return self.__send_and_receive(to_send=to_send, keep_receiving_if_received=keep_receiving_if_received)
        except Exception as e:
            # TODO: maybe remove this?
            print_exc(file=stdout)
            return "Got {} while running".format(e)

    def __send_and_receive(self, to_send: str, keep_receiving_if_received: list):
        if to_send.endswith("\n"):
            self.__proc.send(to_send)
        else:
            self.__proc.sendline(to_send)

        return self.__receive_data(keep_receiving_if_received=keep_receiving_if_received)

    def __receive_data(self, keep_receiving_if_received: list):
        try:
            self.__receive_and_discard_optional_data(keep_receiving_if_received=keep_receiving_if_received)

            return self.__recv_utf8_str()
        except SyntaxError as e:
            self.__kill_and_restart_swipl()

            return str(e)
        except TimeoutError:
            self.__kill_and_restart_swipl()

            return ""

    def __receive_and_discard_optional_data(self, keep_receiving_if_received: list) -> None:
        while True:
            tmp = self.__recv_utf8_str()

            if "ERROR:" in tmp:
                raise SyntaxError(tmp)
            elif not self.__must_receive_again(data=tmp, keep_receiving_if_received=keep_receiving_if_received):
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
        self.run()
