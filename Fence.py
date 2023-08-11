class Fence:
    def __init__(self, x1, y1, x2, y2, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color

    def __str__(self):
        return f"x1={self.x1} , y1={self.y1} ,x2={self.x2},y2={self.y2},color={self.color}"

    def to_string(self):
        return f"x1={self.x1},y1={self.y1},x2={self.x2},y2={self.y2},color={self.color}"


