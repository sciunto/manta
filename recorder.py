# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 11:54:05 2019

@author: Administrateur
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 11:45:18 2019

@author: Administrateur
"""

from pymba import Vimba
from display_frame import write_frame


if __name__ == '__main__':

    with Vimba() as vimba:
        camera = vimba.camera(0)
        camera.open()

        camera.arm('SingleFrame')

        acquiring = True

        # capture a single frame, more than once if desired
        while acquiring:
            frame = camera.acquire_frame()
            try:
                write_frame(frame, 0)
            except StopIteration:
                acquiring = False
                
                
        camera.disarm()

        camera.close()