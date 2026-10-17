class Country:
    def __init__(self, i):
        self.i = i
        self.adj: list[int] = []
        self.owner = None
        self.armies: int = 0
