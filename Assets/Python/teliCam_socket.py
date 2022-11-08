#
# grab_next_image_ndarray.py (for Python 3)
#
# Copyright (c) 2020 Toshiba-Teli Corporation
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#

import sys
import schedule
import cv2
import numpy as np
import json
import socket
import pytelicam

TCP_IP = "127.0.0.1"
TCP_PORT = 5066

address=(TCP_IP,TCP_PORT)

count = 0

def fps():
    global count
    print(count)
    count=0

schedule.every(1/60).minutes.do(fps)
# It is recommended that the settings of unused interfaces be removed.
#  (U3v / Gev / GenTL)

cam_system = pytelicam.get_camera_system( \
    int(pytelicam.CameraType.U3v) | \
    int(pytelicam.CameraType.Gev))

try:
    cam_num = cam_system.get_num_of_cameras()
    if cam_num == 0:
        print('Camera not found.')
        sys.exit()

    print('{0} camera(s) found.'.format(cam_num))

    # Open camera that is detected first, in this sample code.
    cam_no = 0
    cam_device = cam_system.create_device_object(cam_no)
    cam_device.open()

    res = cam_device.genapi.set_enum_str_value('TriggerMode', 'Off')
    if res != pytelicam.CamApiStatus.Success:
        raise Exception("Can't set TriggerMode.")

    cam_device.cam_stream.open()
    cam_device.cam_stream.start()

    while True:
    #for i in range(100):
        # If you don't use 'with' statement, image_data.release() must be called after using image_data.
        schedule.run_pending()
        with cam_device.cam_stream.get_next_image() as image_data:
            if image_data.status != pytelicam.CamApiStatus.Success:
                print('Grab error! status = {0}'.format(image_data.status))
                break
            else:
                np_arr = image_data.get_ndarray(pytelicam.OutputImageType.Bgr24)
                count += 1
                img_data={'image':cv2.imencode('.jpg',np_arr)[1].ravel().tolist()}
                data=json.dumps(img_data)
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.connect(address)
                sock.sendall(bytes(data,encoding='utf-8'))  
                cv2.imshow('image', np_arr)
                sock.close()
        #sock.close()

        k = cv2.waitKey(5) & 0xFF
        if k == ord('q') or k == 27 :       # 'q' or ESC key
            break

except pytelicam.PytelicamError as teli_exception:
    print('An error occurred!')
    print('  message : {0}'.format(teli_exception.message))
    print('  status  : {0}'.format(teli_exception.status))
except Exception as exception:
    print(exception)

finally:
    if 'cam_device' in globals():
        if cam_device.cam_stream.is_open == True:
            cam_device.cam_stream.stop()
            cam_device.cam_stream.close()

        if cam_device.is_open == True:
            cam_device.close()

    cam_system.terminate()

    cv2.destroyAllWindows()

    print('Finished.')
