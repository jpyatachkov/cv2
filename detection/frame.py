# coding: utf-8

"""
Классы для представления окна с видео и области внутри этого окна
"""

import abc
import collections
import cv2

import numpy as np


class Point(collections.namedtuple('PointBase', 'x y')):
    """
    Точка на видео
    """

    def __init__(self, x, y):
        pass

    def __eq__(self, other):
        """
        self == other

        :param other:
        :return: bool
        :raise: ValueError

        """

        Point._check_wrong_arg(other)

        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        """
        self != other

        :param other:
        :return: bool
        :raise: ValueError

        """

        Point._check_wrong_arg(other)

        return self.x != other.x or self.y != other.y

    def __lt__(self, other):
        """
        self < other

        :param other:
        :return: bool
        :raise: ValueError

        """

        Point._check_wrong_arg(other)

        return self.x < other.x or self.y < other.y

    def __gt__(self, other):
        """
        self > other

        :param other:
        :return: bool
        :raise: ValueError

        """

        Point._check_wrong_arg(other)

        return self.x > other.x and self.y > other.y

    def __le__(self, other):
        """
        self > other

        :param other:
        :return: bool
        :raise: ValueError

        """

        Point._check_wrong_arg(other)

        return self.x <= other.x and self.y <= other.y

    def __ge__(self, other):
        """
        self > other

        :param other:
        :return: bool
        :raise: ValueError

        """

        Point._check_wrong_arg(other)

        return self.x >= other.x and self.y >= other.y

    @classmethod
    def _check_wrong_arg(cls, arg):
        """
        Проверка правильности переданного аргумента для операций сравнения

        :param arg:
        :return: bool
        :raise: ValueError

        """

        if arg is None or not isinstance(arg, Point):
            raise ValueError('Невозможно сравнить экземпляр классa Point c {}'.format(type(arg).__name__))


class Field(object):
    """
    Область окна с видео

    Оси из левого верхнего угла экрана
    X - горизонтальная, ширина
    Y - вертикальная, высота
    """

    def __init__(self, top_left, width, height):
        """
        :param top_left: Левая верхняя точка области
        :type top_left: Point

        :param width:
        :type width: int

        :param height:
        :type height: int

        """

        self.top_left = top_left
        self.bottom_right = Point(top_left.x + width - 1, top_left.y + height - 1)
        self.width = width
        self.height = height

    def __contains__(self, item):
        """
        Проверка вхождения точки в область

        :param item: Точка для проверки
        :type item: Point

        :return: bool

        """

        return self.top_left <= item <= self.bottom_right


class Frame(object):
    """
    Базовый класс иерархии
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, width, height, name='Frame'):
        """
        :param width: Ширина окна
        :type width: int

        :param height: Высота окна
        :type height: int

        :param name: Имя окна
        :type name: str

        """

        self.width = width
        self.height = height
        self.name = name

        self.frame = None

    @abc.abstractclassmethod
    def show(self, detections=None):
        pass


class VideoFrame(Frame):
    """
    Кадр окна с видео
    """

    def __init__(self, frame, name='VideoFrame'):
        """
        :param frame: Кадр видео
        :type frame: nd.array of nd.arrays of np.uint8
        :raise: ValueError

        """

        if not frame.size:
            raise ValueError('Невозможно инициализировать экземпляр класса Frame пустым массивом')

        super().__init__(len(frame[0]), len(frame), name)

        self.frame = frame

    def show(self, detections=None, gestures=None):
        """
        :param detections: Области, которые предположительно содержат искомый объект
        :param gestures: Найденные жесты
        :return:

        """

        if detections is not None:
            for x, y, w, h in detections:
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if gestures is not None and len(gestures) > 1:
            for gesture in gestures:
                for point_prev, point_next in zip(gesture, gesture[1:]):
                    cv2.line(self.frame, point_prev, point_next, (255, 0, 0))

        cv2.imshow(self.name, self.frame)


class GestureFrame(Frame):
    """
    Кадр окна с изображением положения руки
    """

    radius = 2
    color = (255, 0, 0)
    # Для получения заполненного цветом круга
    thickness = -1

    def __init__(self, n_fields_in_row, n_rows, width, height, name='GestureFrame'):
        """
        :param n_fields: Количество прямоугольных областей на видео
        :type n_fields: int

        :raise: ValueError
        """

        super().__init__(width, height, name)

        self.n_fields_in_row = n_fields_in_row
        self.n_rows = n_rows

        self.fields = list()

        import math

        field_width = math.ceil(width / self.n_fields_in_row)
        field_height = math.ceil(height / self.n_rows)

        for row_num in range(self.n_rows):
            y_top = row_num * field_height

            # Если последняя строка и высота фрейма взята больше на 1 из-за нечеттной высоты окна
            if row_num == self.n_rows - 1 and not height % self.n_rows:
                field_height -= 1

            # Если последний столбец и ширина фрейма взята больше на 1 из-за нечетной ширины окна
            if width % self.n_fields_in_row:
                last_field_in_row = Field(Point(width - field_width - 1, y_top), field_width - 1, field_height)
            else:
                last_field_in_row = Field(Point(width - field_width, y_top), field_width, field_height)

            self.fields += [Field(Point(x, y_top), field_width, field_height) for x
                            in range(0, width - field_width, width - field_width)] + [last_field_in_row]

        # Пустое черное изображение
        self.frame = np.zeros((height, width), dtype=np.uint8)

    def show(self, detections=None):
        """
        :param args:
        :return:
        :raise: ValueError

        """

        if detections is not None:
            for x, y, w, h in detections:
                cv2.circle(self.frame, (x + w - w // 2, y + h - h // 2), self.radius, self.color, thickness=self.thickness)

        cv2.imshow(self.name, self.frame)

    def get_hited_fields(self, detections):
        """
        Возвращает номера полей, в которые попал распознанный объект, в порядке следования элеметнов поданного на вход
        массива

        :param detections:
        :type detections: nd.array of tuples of np.uint8

        :return: tuple of Points или None

        """

        if not len(detections):
            return

        hitted_points = [Point(x + w // 2, y + h // 2) for x, y, w, h in detections]

        return [self.fields.index([field for field in self.fields if point in field][0]) for point in hitted_points]
