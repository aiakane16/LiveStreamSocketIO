from django.shortcuts import render 
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np
import cv2
import pickle
from darkflow.net.build import TFNet
import os
from test_color import ColorNames as color
import pandas as pd
from django.http import FileResponse
from wsgiref.util import FileWrapper
from django.views.decorators import gzip
import base64
import uuid

options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1}
tfnet = TFNet(options)

index=["color","color_name","hex","R","G","B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

class Test(APIView):
    def post(self, request):
    
        return Response("Nice")
        
class Video(APIView):
    def handle_uploaded_file(f):
        with open('C:/Users/enrik.p.sabalvaro/Desktop/LiveStreamSocketIO/webserver/test.avi', 'wb+') as destination:
            destination.write(f)
                

    def get(self, request):
        file = open('out.avi', 'rb').read()
        response = HttpResponse(file, content_type='video/avi')
        response['Content-Disposition'] = 'attachment; filename=out.avi'
        return response
        
    def post(self, request):
        cap = request.FILES['video'].read()
        Video.handle_uploaded_file(cap)
        cap = cv2.VideoCapture("C:/Users/enrik.p.sabalvaro/Desktop/LiveStreamSocketIO/webserver/test.avi")
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        frameRate = cap.get(5) #frame rate
        
        out = cv2.VideoWriter('out.avi',cv2.VideoWriter_fourcc(*'MJPG'), 30, (frame_width,frame_height), 1)
        font = cv2.FONT_HERSHEY_SIMPLEX #Creates a font
        
        count = 0
        while(cap.isOpened()):
            frameId = cap.get(1) #current frame number
            ret, frame = cap.read()
            print(count)
            if ret==True:
                # write the flipped frame
                results = tfnet.return_predict(frame)
                for result in results:
                    if result["confidence"] > 0.3:
                        x = result["topleft"]["x"]
                        y = result["topleft"]["y"]
                        w = result["bottomright"]["x"]
                        h = result["bottomright"]["y"]
                        cv2.rectangle(frame, (x,y), (w,h), (255, 0, 0), 2) 
                        new_img = cv2.cvtColor(frame[y:h, x:w], cv2.COLOR_RGB2BGR)     
                        text = Detector.convert_image(new_img)
                        cv2.putText(frame, text, (x,y-20), font, 0.7, (0,0,0))
                           
                out.write(frame)
                
                count += 1
            else:
                break
                
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        file = open('C:/Users/enrik.p.sabalvaro/Desktop/LiveStreamSocketIO/webserver/out.avi', 'rb').read()
        response = HttpResponse(file, content_type='video/avi')
        response['Content-Disposition'] = 'attachment; filename=out.avi'
        return response
        # file_name = 'out.avi'
        # path_to_file = 'C:/Users/enrik.p.sabalvaro/Desktop/LiveStreamSocketIO/webserver/'
        # response = HttpResponse(mimetype='application/force-download')
        # response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
        # response['X-Sendfile'] = smart_str(path_to_file)
        # return response
        
class Frame(APIView):
    @gzip.gzip_page
    def get(self, request):
        try:
            return StreamingHttpResponse(VideoCamera.gen(VideoCamera()), content_type="multipart/x-mixed-replace;boundary=frame")
        except:  # This is bad! replace it with proper handling
            pass

class Detector(APIView):
    def post(self, request):
        #url = request.POST.get('image_url','')
        image_file = request.FILES['image'].read()
        img = cv2.imdecode(np.fromstring(image_file, np.uint8), cv2.IMREAD_UNCHANGED)
        #img = cv2.imdecode(npimg, cv2.COLOR_BGR2RGB)
        h, w, _ = img.shape
        thick = int((h + w) // 300)

        if image_file:
            imgcv = img
            results = tfnet.return_predict(imgcv)
            font = cv2.FONT_HERSHEY_TRIPLEX #Creates a font

            for result in results:
            
                if result["confidence"] > 0.3:
                    x = result["topleft"]["x"]
                    y = result["topleft"]["y"]
                    w = result["bottomright"]["x"]
                    h = result["bottomright"]["y"]
                    
                    new_img = imgcv[y:h, x:w]
                    text = Detector.convert_image(new_img)
                    cv2.rectangle(imgcv, (x,y), (w,h), (255, 0, 0), 10)
                    #print(len(prediction))
                    
                    
                    cv2.putText(imgcv, text, (x,y-12), 0, 1e-3 * h + 5, (0,0,0), 25)
            # full_path = os.path.dirname(os.path.realpath(__file__))
            # path = "D:/programming/Color Detection/LiveStreamSocketIO/webserver/server/static/"
            # path_file = '/static/test.jpg'
            # cv2.imwrite(r'D:\programming\Color Detection\LiveStreamSocketIO\webserver\server\static\test.jpg', imgcv)
            # return HttpResponse(path_file)
            data = cv2.imencode('.jpg', imgcv)[1].tobytes()
            return HttpResponse(data, content_type="image/jpg")
            return HttpResponse(path_file, content_type="application/json")
        else:
            return Response("No image")

    def convert_image(src_image):
        # load the image
        image = src_image

        chans = cv2.split(image)
        colors = ('b', 'g', 'r')
        features = []
        feature_data = ''
        counter = 0
        for (chan, color) in zip(chans, colors):
            counter = counter + 1

            hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
            features.extend(hist)

            # find the peak pixel values for R, G, and B
            elem = np.argmax(hist)

            if counter == 1:
                blue = str(elem)
            elif counter == 2:
                green = str(elem)
            elif counter == 3:
                red = str(elem)
                feature_data = [red, green, blue]
                print("feature", feature_data)

        print(feature_data[0])
        print(feature_data[1])
        print(feature_data[2])
        
        return Detector.getColorName(int(feature_data[0]), int(feature_data[1]), int(feature_data[2]))
    
    #function to calculate minimum distance from all colors and get the most matching color
    def getColorName(R,G,B):
        minimum = 10000
        for i in range(len(csv)):
            d = abs(R- int(csv.loc[i,"R"])) + abs(G- int(csv.loc[i,"G"]))+ abs(B- int(csv.loc[i,"B"]))
            if(d<=minimum):
                minimum = d
                cname = csv.loc[i,"color_name"]
        print(cname)
        return cname

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

    def gen(camera):
        cam = VideoCamera()
        while True:
            frame = cam.get_frame()
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

