import os
import platform
import subprocess as sproc
from enum import Enum
from typing import Optional


class PathConverter:
    """
    This class contains file path conversion functions for different
    combinations of OS running winIDEA and OS running Python code.
    By instantiating multiple instances it is even possible to cover complex
    use cases, when one winIDEA instance is running in Wine and another
    one natively on Linux (when available).

    Currently the following combinations are possible:

    client   winIDEA
    ----------------
    Windows  Windows
    Linux    WINE
    WSL      WSL_WINE (USB debugging not available)
    """

    class Os(Enum):
        """
        This enum is used to describe type of environment for winIDEA and Python
        script.
        """
        LINUX = 0  # native linux, not yet implemented
        WINE = 2  # wine running on native linux
        WINDOWS = 3  # native windows

    def __init__(self, winidea_os: Optional[Os] = None, winepath_path: str = 'winepath'):
        """
        Client OS (where Python code runs) is determined automatically.

        @param winidea_os: OS where winIDEA is running. If set to None, it is set to 
          Os.WINDOWS if Python is running on Windows, and to Os.WINE if Python is 
          runinng in Linux, and Os.WSL_WINE if Python is running in WSL
        @param winepath_path path to path conversion utility `winepath`. Specify it
        when winIDEA is running on Linux under WINE, and the `winepath` utility is
        not in system PATH.
        """

        self.winepath_path: str = winepath_path
        self.client_os = self._get_os()
        if winidea_os is None:
            match self.client_os:
                case PathConverter.Os.WINDOWS:
                    self.winidea_os = PathConverter.Os.WINDOWS
                case PathConverter.Os.LINUX:
                    self.winidea_os = PathConverter.Os.WINE
                case _:
                    raise Exception(f"No default winIDEA os exists for client OS {self.client_os}."
                                    f"Specify winIDEA Os as constructor parameter.")
        else:
            self.winidea_os = winidea_os

        if self.client_os == PathConverter.Os.LINUX and self.winidea_os == PathConverter.Os.WINE:
            try:
                sproc.check_output([self.winepath])
            except ex:
                raise ValueError(f"It seems Python is running on Linux ({self.client_os}) and "
                                 f"winIDEA is running in WINE ({self.winidea_os}), but WINE "
                                 "utility 'winepath' is not availble. Set path to 'winepath' "
                                 "as constructor parameter.")

    def wi_to_py(self, winidea_path: str) -> str:
        """
        Converts path from winIDEA domain to Python domain.
        """
        if self.client_os == PathConverter.Os.WINDOWS:
            if self.winidea_os == PathConverter.Os.WINDOWS:
                return winidea_path
            raise OSError("If Python is running on Windows, only winIDEA running on "
                          f"Windows is currently supported: "
                          f"client_os: {self.client_os}, winidea_os: {self.winidea_os}")

        elif self.client_os == PathConverter.Os.LINUX:
            if self.winidea_os == PathConverter.Os.WINE:
                return self.to_linux_path(winidea_path)
            elif self.winidea_os == PathConverter.Os.LINUX:
                # to be used when native winIDEA on Linux is implemented
                return winidea_path

        elif self.client_os == PathConverter.Os.WSL:
            if self.winidea_os in [PathConverter.Os.WINE, PathConverter.Os.WSL_WINE]:
                return self.to_linux_path(winidea_path)
            elif self.winidea_os in [PathConverter.Os.LINUX, PathConverter.Os.WSL]:
                # to be used when native winIDEA on Linux is implemented
                return winidea_path
            else:
                raise RuntimeError(f"winIDEA os {self.winidea_os} is not supported "
                                   f"in combination with client os {self.client_os}")
        else:
            raise ValueError(f"Can not convert winIDEA path to client path! "
                             f"Unsupported client OS: {self.client_os}.")

    def py_to_wi(self, client_path: str) -> str:
        """
        Converts path from Python domain to winIDEA domain.
        """
        if self.client_os == PathConverter.Os.WINDOWS:
            if self.winidea_os == PathConverter.Os.WINDOWS:
                return client_path

        if self.client_os == PathConverter.Os.LINUX:
            if self.winidea_os == PathConverter.Os.WINE:
                return self.to_wine_path(client_path)
            elif self.winidea_os == PathConverter.Os.LINUX:
                # to be used when native winIDEA on Linux is implemented
                return client_path
            else:
                raise RuntimeError(f"winIDEA os {self.winidea_os} is not supported "
                                   f"in combination with client os {self.client_os}")

        elif self.client_os == PathConverter.Os.WSL:
            if self.winidea_os in [PathConverter.Os.WINE, PathConverter.Os.WSL_WINE]:
                return self.to_wine_path(client_path)
            elif self.winidea_os in [PathConverter.Os.LINUX, PathConverter.Os.WSL]:
                return client_path
            elif self.winidea_os == PathConverter.Os.WINE:
                return self.to_wine_path(client_path)
            else:
                raise RuntimeError(f"Unknown winIDEA os specified: {self.winidea_os}")
        else:
            raise ValueError(f"Can not convert client path to winIDEA path! "
                             f"Unknown client OS: {self.client_os}.")

    def to_linux_path(self, win_path: str) -> str:
        """
        Converts WINE path to Linux path.
        @param wine_path: path to file in WINE domain.
        @return: path in Linux domain.
        """
        lx_path = sproc.check_output([self.winepath_path, "-u", win_path]).decode("UTF-8").strip()
        return lx_path


    def to_wine_path(self, lx_path: str) -> str:
        """
        Converts Linux path to WINE path.
        @param lx_path: Linux path
        @return: WINE path.
        """
        wine_path = sproc.check_output([self.winepath_path, "-w", lx_path]).decode("UTF-8").strip()
        return wine_path

        
    def _get_os(self) -> Os:
        if platform.system() == 'Windows':
            if 'WINEUSERNAME' in os.environ:
                if 'WSL_DISTRO_NAME' in os.environ:
                    return self.Os.WSL_WINE
                else:
                    return self.Os.WINE
            else:
                return self.Os.WINDOWS
        else:
            if self._is_wsl():
                return self.Os.WSL
            else:
                return self.Os.LINUX

    def _is_wsl(self) -> bool:
        """ Returns true if this code is running in WSL - Windows Subsystem for Linux. """
        uname = platform.uname().release
        return 'Microsoft' in uname or 'microsoft' in uname

