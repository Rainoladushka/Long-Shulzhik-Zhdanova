class Rectangle:
    def __init__(self, width: float, height: float):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive numbers.")
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    def area(self) -> float:
        """Вычислите площадь прямоугольника."""
        return self._width * self._height

    def perimeter(self) -> float:
        """Вычислите периметр прямоугольника."""
        return 2 * (self._width + self._height)


class Square(Rectangle):
    def __init__(self, side: float):
        """Инициализируем квадрат с равными сторонами."""
        super().__init__(side, side)

    @property
    def side(self) -> float:
        return self._width  # Hoặc self._height vì chúng bằng nhau

    def __str__(self):
        return f"Square(side={self.side})"


def main():
    # Создаём прямоугольник
    rectangle = Rectangle(4, 5)
    print(f"Rectangle: width={rectangle.width}, height={rectangle.height}")
    print(f"Rectangle area: {rectangle.area()}")
    print(f"Rectangle perimeter: {rectangle.perimeter()}")
    print()

    # Создадим квадрат
    square = Square(4)
    print(f"Square: side={square.side}")
    print(f"Square area: {square.area()}")
    print(f"Square perimeter: {square.perimeter()}")
    print()

    # Проверьте принцип Барбари Лисков
 # Заменить объект Прямоугольник на Квадрат
    def print_rectangle_info(rect: Rectangle):
        print(f"Width: {rect.width}, Height: {rect.height}")
        print(f"Area: {rect.area()}")
        print(f"Perimeter: {rect.perimeter()}")
    
    print("Rectangle Info:")
    print_rectangle_info(rectangle)

    print("\nSquare as Rectangle Info:")
    print_rectangle_info(square)


if __name__ == "__main__":
    main()
