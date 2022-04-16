


class Ledger():
    """
            0              1                 2
    [ [IP Address] [IP Connection] [Min to Experation] ]
    [ [          ] [             ] [                 ] ]
    ...
    """

    def __init__(self) -> None:
        
        self.ledger = []

    