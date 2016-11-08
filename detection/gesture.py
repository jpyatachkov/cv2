# coding: utf-8

"""
Жесты
"""

import itertools


class Gesture(object):
    """
    Базовый класс иерархии
    """

    PART_OF_GESURE_FOUND = 1
    ENTIRE_GESTURE_FOUND = 2

    def __init__(self, fields=None):
        """
        :param fields: Список номеров полей жеста (в порядке следования)

        """

        self.fields = fields
        # Оставшиеся точки жеста
        self.remain_fields = fields.copy()

    def __str__(self):
        return 'Жест {}'.format(self.fields)

    def check_field(self, fields):
        """
        Проверяет, относится ли пройденное поле к жесту (соответствует ли нулевой элемент массива remain_fieldsолю с номером
        num.

        :param num:
        :return: 1 если найден не весь жест, 2, если весь, 0 если ничего

        """

        if fields == self.fields:
            return self.ENTIRE_GESTURE_FOUND

        match_counter = 0

        for field, self_field in zip(fields, self.fields):
            if field != self_field:
                break
            else:
                match_counter += 1

        if not match_counter:
            return 0
        else:
            return self.PART_OF_GESURE_FOUND


class TwoPositionGesture(Gesture):
    """
    Жест, состоящий в перемещении между двумя полями
    """

    @classmethod
    def generate_all(cls, fields_in_row, n_rows):
        """
        Генерирует все возможные простые жесты по количеству полей кроме диагональных

        :param fields_in_row:
        :param nrows:
        :return:
        """

        return [TwoPositionGesture(list(gesture_fields)) for gesture_fields in itertools.combinations(range(fields_in_row * n_rows + 1), r=2)]

    def __init__(self, fields):
        super().__init__(fields)
