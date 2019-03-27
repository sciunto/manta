# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 17:07:59 2019

@author: Administrateur
"""

from typing import Optional
import cv2
from pymba import Frame

import os.path
import os
import datetime
import itertools
import time

# todo add more colours
PIXEL_FORMATS_CONVERSIONS = {
    'BayerRG8': cv2.COLOR_BAYER_RG2RGB,
}

previous_time_in_ms = int(time.perf_counter() * 1000)
counter = itertools.count(start=0, step=1)
date = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')

def display_frame(frame: Frame, delay: Optional[int] = 1) -> None:
    """
    Displays the acquired frame.
    :param frame: The frame object to display.
    :param delay: Display delay in milliseconds, use 0 for indefinite.
    """
    print(f'frame {frame.data.frameID}')

    # get a copy of the frame data
    image = frame.buffer_data_numpy()

    # convert colour space if desired
    try:
        image = cv2.cvtColor(image, PIXEL_FORMATS_CONVERSIONS[frame.pixel_format])
    except KeyError:
        pass

    # display image
    cv2.imshow('Viewer', image)
    cv2.waitKey(10)
    if cv2.getWindowProperty('Viewer', 0) < 0:
        raise StopIteration
    
    
    
def write_frame(frame: Frame, delay: Optional[int] = 1) -> None:
    """
    Displays the acquired frame.
    :param frame: The frame object to display.
    :param delay: Display delay in milliseconds, use 0 for indefinite.
    """
    global previous_time_in_ms
    print(f'frame {frame.data.frameID}')

    # get a copy of the frame data
    image = frame.buffer_data_numpy()

    # convert colour space if desired
    try:
        image = cv2.cvtColor(image, PIXEL_FORMATS_CONVERSIONS[frame.pixel_format])
    except KeyError:
        pass

    output_dir = os.path.abspath(r'E:\data')
    #date = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')
    #date = 'tptp'
    datadir = os.path.join(output_dir, date)
    os.makedirs(datadir, exist_ok=True)
    num = counter.__next__()
    filename = str(num).zfill(8) + '.png'

    print(datadir)
    
    time_in_ms = int(time.perf_counter() * 1000)
    duration = time_in_ms - previous_time_in_ms
    previous_time_in_ms = time_in_ms
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss%fµs')
    with open(os.path.join(datadir, 'metadata.txt'), 'a',
                          encoding='utf8') as metadata:
        metadata.write(f'{filename} {timestamp} {num} {duration}\n')
    
   
    
    cv2.imwrite(os.path.join(datadir, filename), image)
    cv2.imshow('Viewer', image)

    cv2.waitKey(1)
    if cv2.getWindowProperty('Viewer', 0) < 0:
        raise StopIteration
