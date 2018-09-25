#!/usr/bin/env python
# Author: Francois Boulogne


import threading
import queue as Queue
import time
import datetime
import os
import logging

import pymba as pb
import numpy as np
import cv2
import imageio

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

BUF_SIZE = 1000
q = Queue.Queue(BUF_SIZE)

class GrabberThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(GrabberThread,self).__init__()
        self.target = target
        self.name = name
        self.event = args[0]
        self.frame = args[1]
        self.c0 = args[2]

        self.framenumber = 0
        self.prev_time_in_ms = 0

    def run(self):

        while self.event.is_set():
            if not q.full():

                try:
                    self.frame.queueFrameCapture()
                    success = True
                except:
                    #droppedframes.append(framecount)
                    success = False
                self.c0.runFeatureCommand("AcquisitionStart")
                self.c0.runFeatureCommand("AcquisitionStop")
                self.frame.waitFrameCapture(1000)
                frame_data = self.frame.getBufferByteData()

                if success:

                    # Timer
                    time_in_ms = int(time.perf_counter() * 1000)
                    duration = time_in_ms - self.prev_time_in_ms
                    self.prev_time_in_ms = time_in_ms
                    logging.debug('Frame duration: %f, %f', duration, 1/(duration * 1e-3))



                    img = np.ndarray(buffer=frame_data,
                                 dtype=np.uint8,
                                 shape=(self.frame.height, self.frame.width, 1))

                    #cv2.imshow('Viewer', img)
                    q.put((self.framenumber, img, time.perf_counter()))
                    logging.debug('Putting ' + ' : ' + str(q.qsize()) + ' items in queue')
                    self.framenumber += 1

        return


class WriterThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(WriterThread, self).__init__()
        self.target = target
        self.name = name
        self.event = args[0]
        self.prev_time_in_ms = 0
        return

    def run(self):
        global display_img
        while True:
            if not self.event.is_set() and q.empty():
                logging.debug('End of the writer loop')
                break
            if not q.empty():
                num, img, time_counter = q.get()
                display_img = img
                filename = str(num).zfill(8) + '.png'
                logging.debug('Getting '
                              + ' : ' + str(q.qsize()) + ' items in queue')

                #imageio.imsave(os.path.join(datadir, filename), img, format='png')
                prev_time_in_ms = int(time.perf_counter() * 1000)
                cv2.imwrite(os.path.join(datadir, filename), img)
                with open(os.path.join(datadir, 'metadata.txt'), 'a') as metadata:
                    metadata.write(f'{num} {time_counter} {filename}\n')
                # Timer
                time_in_ms = int(time.perf_counter() * 1000)
                duration = time_in_ms - prev_time_in_ms
                logging.debug('---------------------Saving duration: %f', duration)
                self.prev_time_in_ms = time_in_ms
                if self.event.is_set():
                    # Wait a little to avoid emptying the queue
                    # and slowing down the process
                    if 45 - duration > 0:
                        time.sleep((45 - duration) * 1e-3)
                    else:
                        time.sleep(25 * 1e-3)


        return


if __name__ == '__main__':


    date = datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')
    datadir = os.path.join(os.path.abspath('E:\\data'), date)
    os.makedirs(datadir, exist_ok=True)


    with pb.Vimba() as vimba:
        system = vimba.getSystem()

        system.runFeatureCommand('GeVDiscoveryAllOnce')
        time.sleep(0.2)

        camera_ids = vimba.getCameraIds()

        for cam_id in camera_ids:
            print('Camera found: ', cam_id)

        c0 = vimba.getCamera(camera_ids[0])
        c0.openCamera()

        try:
            # gigE camera
            print('This is a gigE camera')
            print(c0.GevSCPSPacketSize)
            print(c0.StreamBytesPerSecond)
            #c0.StreamBytesPerSecond = 20000
        except:
            # not a gigE camera
            print('This is NOT a gigE camera')
            pass

        time.sleep(2)

        # Set pixel format
        c0.PixelFormat = 'Mono8'
        #c0.ExposureTimeAbs = 60000

        frame = c0.getFrame()
        frame.announceFrame()

        c0.startCapture()



        run_event = threading.Event()
        run_event.set()
        p = GrabberThread(name='grabber', args=(run_event, frame, c0))
        c = WriterThread(name='writer', args=(run_event,))

        cv2.namedWindow('Viewer')
        p.start()
        #time.sleep(10)
        c.start()
        #time.sleep(1)

        time.sleep(1)

        try:
            while True:
                cv2.imshow('Viewer', display_img)
                # This has the role of a time.sleep() call
                cv2.waitKey(1)
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            logging.debug('attempting to close threads')
            run_event.clear()
            p.join()
            c.join()
            logging.debug('threads successfully closed')
