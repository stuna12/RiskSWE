
class Territory:
    def __init__(self, i):
        self.i = i
        self.adj: list[Territory] = []
        self.owner: Player | None = None
        self.armies: int = 0
