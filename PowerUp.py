class PowerUp:
    def __init__(self, x1, x2, x3, y1, y2, y3, color):
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.color = color

    def __str__(self):
        return f"x1={self.x1} x2={self.x2}, x3={self.x3} ,y1={self.y1} ,y2={self.y2}, y3={self.y3} , color={self.color}"

    def to_string(self):
        return f"x1={self.x1} x2={self.x2}, x3={self.x3} ,y1={self.y1} ,y2={self.y2}, y3={self.y3} , color={self.color}"

