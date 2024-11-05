class Shape:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Rectangle(Shape):
    def __init__(self, width, height, x=0, y=0):
        super().__init__(x, y)
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

class Square(Shape):
    def __init__(self, side, x=0, y=0):
        super().__init__(x, y)
        self._side = side

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = value

    @property
    def width(self):
        return self._side

    @width.setter
    def width(self, value):
        self._side = value

    @property
    def height(self):
        return self._side

    @height.setter
    def height(self, value):
        self._side = value

rect = Rectangle(4, 5)
print(f"Rectangle width: {rect.width}, height: {rect.height}")

square = Square(3)
print(f"Square side: {square.side}")

square.width = 4
print(f"Square new side: {square.side}")

rect.height = 10
print(f"Rectangle new width: {rect.width}, new height: {rect.height}")
