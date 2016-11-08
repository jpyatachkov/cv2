# coding: utf-8

import os

import argparse as ap

from detection.detector import GestureDetector


def setup_parser():
    parser = ap.ArgumentParser()

    parser.add_argument('in_file', type=str, help='Video file to find gestures', default='')
    parser.add_argument('--cascade', type=str, help='Haar cascade classifier to use (default is haar-hand.xml)',
                        default='haar-hand.xml')

    return parser


def main(args):
    if '\\' not in os.path.split(args.in_file)[0]:
        args.in_file = os.path.join(os.getcwd(), args.in_file)

    if '\\' not in os.path.split(args.cascade)[0]:
        args.cascade = os.path.join(os.getcwd(), args.cascade)

    gesture_detector = GestureDetector(args.in_file, args.cascade)
    gesture_detector.exec()


if __name__ == "__main__":
    parser = setup_parser()
    main(parser.parse_args())
    # main()
