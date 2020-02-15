from django.shortcuts import render 
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import numpy as np
import cv2
import pickle
from sklearn.neighbors import KNeighborsClassifier
from skimage import io
from darkflow.net.build import TFNet
from sklearn.cluster import KMeans
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
import os
from test_color import ColorNames as color
import pandas as pd
from django.http import FileResponse
from wsgiref.util import FileWrapper
from django.views.decorators import gzip

options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1}
tfnet = TFNet(options)

index=["color","color_name","hex","R","G","B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

class Test(APIView):
    def post(self, request):
    
        return Response("Nice")
        
class Video(APIView):
    def post(self, request):
        cap = cv2.VideoCapture('sample_fb.mp4')
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
        file = FileWrapper(open('out.avi', 'rb'))
        response = HttpResponse(file, content_type='video/avi')
        response['Content-Disposition'] = 'attachment; filename=out.avi'
        return response
        
class Frame(APIView):
    @gzip.gzip_page
    def get(self, request, stream_path="video"):
        try:
            return StreamingHttpResponse(Frame.get_frame(), content_type="multipart/x-mixed-replace;boundary=frame")
        except:
            return "error"
    
  
    def get_frame():
        camera=cv2.VideoCapture(0)
        
        while True:
            _, img = camera.read()
            imgencode=cv2.imencode('.jpg', img)[1]
            stringData=imgencode.toString()
            yield(b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        del(camera)
       
        
            

class Detector(APIView):
    def post(self, request):
        #url = request.POST.get('image_url','')
        image_file = request.FILES['image'].read()
        npimg = np.fromstring(image_file, np.uint8)
        img = cv2.imdecode(npimg, cv2.COLOR_BGR2RGB)

        if image_file:
            imgcv = img
            results = tfnet.return_predict(imgcv)
            font = cv2.FONT_HERSHEY_SIMPLEX #Creates a font

            for result in results:
            
                if result["confidence"] > 0.3:
                    x = result["topleft"]["x"]
                    y = result["topleft"]["y"]
                    w = result["bottomright"]["x"]
                    h = result["bottomright"]["y"]
                    
                    new_img = imgcv[y:h, x:w]
                    text = Detector.convert_image(new_img)
                    cv2.rectangle(imgcv, (x,y), (w,h), (255, 0, 0), 2)
                    #print(len(prediction))
                    
                    
                    cv2.putText(imgcv, text, (x,y-20), font, 0.7, (0,0,0))
            data = cv2.imencode('.jpg', imgcv)[1].tobytes()
            return HttpResponse(data, content_type="image/jpg")
            #return HttpResponse(type(data), content_type="application/json")
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
