import os
import sys
import time
from dbr import *
import cv2

# you can change the following variables' value to your own value.
license_key = "Input your own license"
json_file = r"Please input your own template path"

reader = BarcodeReader()

results = None

# The callback function for receiving barcode results
def on_barcode_result(data):
    global results
    results = data

def get_time():
    localtime = time.localtime()
    capturetime = time.strftime("%Y%m%d%H%M%S", localtime)
    return capturetime

def read_barcode():
    global results
    video_width = 0
    video_height = 0
    
    vc = cv2.VideoCapture(0)
    video_width  = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
    vc.set(3, video_width) #set width
    vc.set(4, video_height) #set height

    stride = 0
    if vc.isOpened():  
        rval, frame = vc.read()
        stride = frame.strides[0]
    else:
        return

    windowName = "Barcode Reader"

    parameters = reader.init_frame_decoding_parameters()
    # you can modify these following parameters.
    parameters.max_queue_length = 30
    parameters.max_result_queue_length = 30
    parameters.width = video_width
    parameters.height = video_height
    parameters.stride = stride
    parameters.image_pixel_format = EnumImagePixelFormat.IPF_RGB_888
    parameters.region_top = 0
    parameters.region_bottom = 100
    parameters.region_left = 0
    parameters.region_right = 100
    parameters.region_measured_by_percentage = 1
    parameters.threshold = 0.01
    parameters.fps = 0
    parameters.auto_filter = 1

    reader.start_video_mode(parameters, on_barcode_result)

    while True:
        if results != None:
            thickness = 2
            color = (0,255,0)
            for result in results:
                text_result = TextResult(result)
                print("Barcode Format :")
                print(text_result.barcode_format_string)
                print("Barcode Text :")
                print(text_result.barcode_text)
                print("Localization Points : ")
                print(text_result.localization_result.localization_points)
                print("-------------")

                points = text_result.localization_result.localization_points

                cv2.line(frame, points[0], points[1], color, thickness)
                cv2.line(frame, points[1], points[2], color, thickness)
                cv2.line(frame, points[2], points[3], color, thickness)
                cv2.line(frame, points[3], points[0], color, thickness)
                cv2.putText(frame, text_result.barcode_text, points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
            results = None

        cv2.imshow(windowName, frame)
        rval, frame = vc.read()
        if rval == False:
            break
        
        try:
            ret = reader.append_video_frame(frame)
        except:
            pass
        
        # 'ESC' for quit
        key = cv2.waitKey(1)
        if key == 27:
            break

    reader.stop_video_mode()
    cv2.destroyWindow(windowName)


print("-------------------start------------------------")

# Apply for a trial license: https://www.dynamsoft.com/customer/license/trialLicense
reader.init_license(license_key)

## The code snippet below shows how to use the full license in DBR 8.x:
# connection_paras = BarcodeReader.init_lts_connection_parameters()
## If DBR service is already built on your server, you can fill in the address of your server, or leave this property's default value.
# connection_paras.main_server_url = "Input your own server url"
# connection_paras.handshake_code = "Input your own handshake"
# connection_paras.deployment_type = EnumDMDeploymentType.DM_DT_DESKTOP
# connection_paras.uuid_generation_method = EnumDMUUIDGenerationMethod.DM_UUIDGM_RANDOM
# try:
#     error = BarcodeReader.init_license_from_lts(connection_paras)
#     if error[0] != EnumErrorCode.DBR_OK:
#         print(error[1])
# except BarcodeReaderError as bre:
#     print(bre)

error = reader.init_runtime_settings_with_file(json_file)
if error[0] != EnumErrorCode.DBR_OK:
    print(error[1])

read_barcode()
print("-------------------over------------------------")
