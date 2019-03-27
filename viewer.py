# -*- coding: utf-8 -*-
from pymba import Vimba
from display_frame import display_frame


if __name__ == '__main__':

    with Vimba() as vimba:
        camera = vimba.camera(0)
        camera.open()

        camera.arm('SingleFrame')

        acquiring = True
        while acquiring:
            frame = camera.acquire_frame()
            try:
                display_frame(frame, 0)
            except StopIteration:
                acquiring = False

        camera.disarm()
        camera.close()
