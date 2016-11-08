# coding: utf-8

"""
Детектор жестов
"""

import cv2
import math
import os

from detection.gesture import TwoPositionGesture
from detection.frame import Point, VideoFrame, GestureFrame


class GestureDetector(object):
    """
    Детектор жестов
    """

    def __init__(self, video_path, haar_classifier_path=None, n_fields=4, gestures=None):
        """
        :param video_path: Полный путь к файлу с видео
        :param haar_classifier_path: Полный путь к классификатору
        :param n_fields: Количество полей, на которые будет разделено изображение
        :param gestures: Список жестов для распознавания (по умолчанию генерятся жесты из двух точек)
        :raise: ValueError

        """

        if not os.path.exists(video_path):
            raise ValueError('Невозможно открыть {}'.format(video_path))

        if haar_classifier_path is None and not os.path.exists(haar_classifier_path):
            raise ValueError('Невозможно открыть {}'.format(haar_classifier_path))

        n_rows_or_cols = math.sqrt(n_fields)

        if not n_rows_or_cols.is_integer():
            raise ValueError('Количество областей должно иметь квадратный корень')

        n_rows_or_cols = int(n_rows_or_cols)

        self.capture = cv2.VideoCapture(video_path)

        _, frame = self.capture.read()
        self.video_frame = VideoFrame(frame)

        self.gesture_frame = GestureFrame(n_rows_or_cols, n_rows_or_cols, self.video_frame.width, self.video_frame.height)

        self.haar_classifier = cv2.CascadeClassifier(haar_classifier_path)

        if gestures is None or not gestures:
            self.gestures = TwoPositionGesture.generate_all(self.gesture_frame.n_fields_in_row, self.gesture_frame.n_rows)
        else:
            self.gestures = gestures

    def exec(self):
        """
        Ищет жесты

        :return:
        """

        x_pos, y_pos, w_pos, h_pos = range(4)

        prev_points = list()
        hitted_fields = list()

        w, h = self.video_frame.width, self.video_frame.height

        while self.capture.isOpened():
            if self.video_frame.frame is None:
                break

            detections = self.haar_classifier.detectMultiScale(self.video_frame.frame, 1.17, minNeighbors=7, minSize=(100,100))

            found_gesture = None

            if len(detections):
                # Поиск самого большого прямоугольника из оставшихся
                max_rect_dim = max(max([(x[w_pos], x[h_pos]) for x in detections]))
                detections = [x for x in detections if x[w_pos] == max_rect_dim or x[h_pos] == max_rect_dim]

                hitted_fields.append(self.gesture_frame.get_hited_fields(detections)[0])

                for gesture in self.gestures:
                    is_gesture = gesture.check_field(hitted_fields)

                    if not is_gesture:
                        continue

                    if is_gesture == TwoPositionGesture.ENTIRE_GESTURE_FOUND:
                        print(gesture)

                        found_gesture = [prev_points + [(detections[0][x_pos], detections[0][y_pos])]]

                        prev_points.clear()
                        hitted_fields.clear()
                    else:
                        if len(hitted_fields) > 1:
                            hitted_fields = hitted_fields[-1:]

                        if prev_points and prev_points[0] in self.gesture_frame.fields[hitted_fields[0]]:
                            prev_points = [Point(detections[0][x_pos], detections[0][y_pos])]
                        else:
                            prev_points.append(Point(detections[0][x_pos], detections[0][y_pos]))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            self.video_frame.show(detections, found_gesture)
            self.gesture_frame.show(detections)

            _, self.video_frame.frame = self.capture.read()

        self.capture.release()
        cv2.destroyAllWindows()