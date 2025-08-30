from spyne.error import (
    Fault,
)


class SpyneException(Fault):
    """Переопределенный Exception базового exception`а spyne.

    По спецификации спайна faultcode
    It's a dot-delimited string whose first fragment is
            either 'Client' or 'Server'.
    """

    def __init__(self, code=0, message=''):
        if isinstance(code, str):
            Fault.__init__(self, faultstring=code)
        else:
            Fault.__init__(self, faultcode='Server;%d' % code, faultstring=message)
