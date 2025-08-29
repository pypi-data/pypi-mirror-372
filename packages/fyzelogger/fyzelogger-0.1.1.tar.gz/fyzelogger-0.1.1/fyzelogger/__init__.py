import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class FyzeLogger:
    def __init__(self, name="FyZe"):
        self.name = name

    def _time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def log(self, msg):
        print(f"[{self._time()}] [{self.name}] » {msg}")

    def success(self, msg):
        print(f"[{self._time()}] [{Fore.GREEN}● SUCCESS{Style.RESET_ALL}] » {msg}")

    def error(self, msg):
        print(f"[{self._time()}] [{Fore.RED}● ERROR{Style.RESET_ALL}] » {msg}")

    def debug(self, msg):
        print(f"[{self._time()}] [{Fore.CYAN}● DEBUG{Style.RESET_ALL}] » {msg}")

    def warn(self, msg):
        print(f"[{self._time()}] [{Fore.YELLOW}● WARN{Style.RESET_ALL}] » {msg}")

    def ratelimit(self, msg):
        print(f"[{self._time()}] [{Fore.MAGENTA}● RATELIMIT{Style.RESET_ALL}] » {msg}")

    def input(self, prompt):
        return input(f"[{self._time()}] [{Fore.MAGENTA}● INPUT{Style.RESET_ALL}] » {prompt}")
