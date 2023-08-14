class SpeedBoostPowerUp:
    def __init__(self, x, y, color_inside , color_outside):
        self.x = x
        self.y = y
        self.color_inside = color_inside
        self.color_outside = color_outside

    def get_points_for_polygon(self):
        points = [self.x, self.y,
                  self.x + 4, self.y,
                  self.x + 8, self.y + 8,
                  self.x + 4, self.y + 8,
                  self.x + 8, self.y + 16,
                  self.x - 2.4, self.y + 6,
                  self.x + 4.8, self.y + 6]
        return points

    def __str__(self):
        return f"x1={self.x} x2={self.y},color_inside={self.color_inside} , color_outside={self.color_outside}"

    def to_string(self):
        return f"x1={self.x} x2={self.y},color_inside={self.color_inside},color_outside={self.color_outside}"


