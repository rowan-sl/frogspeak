class BadUsageException(Exception):
    def __init__(self, *args: object, **kwdargs) -> None:
        super().__init__(*args, **kwdargs)