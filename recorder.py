# -*- coding: utf-8 -*-
from pymba import Vimba
from display_frame import write_frame
  

if __name__ == '__main__':

    time_between_frame_ms = 1000 # ms
    
    with Vimba() as vimba:
        camera = vimba.camera(0)
        camera.open()

        camera.arm('SingleFrame')

        acquiring = True
        while acquiring:
            frame = camera.acquire_frame()
            try:
                write_frame(frame, time_between_frame_ms, 0)
            except StopIteration:
                acquiring = False

        camera.disarm()
        camera.close()