class Player:
    def __init__(self, address, name, x, y, size: int, color, speed=1):
        self.address = address
        self.name = name
        self.position_x = x
        self.position_y = y
        self.color = color
        self.size = size
        self.speed = speed

    def __str__(self):
        return f"address={self.address}, name = {self.name} , x={self.position_x}, y={self.position_y}  , size={self.size}, color={self.color} , speed = {self.speed}"

    def to_string(self):  
        return f"{self.address},{self.name},{self.position_x},{self.position_y},{self.size},{self.color},{self.speed}"
