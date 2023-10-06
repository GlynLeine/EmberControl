def clearConsole():
    print("\033c", end='')

def clearLine():
    print("\033[2K", end="\r", flush=True)

def printLog(*values: object, _sep: str | None = " ", _end: str | None = ""):
    clearLine()
    print(*values, sep=_sep, end=_end, flush=True)

def nextLine():
    print("")

def prevLine():
    print("\033[F", end="")