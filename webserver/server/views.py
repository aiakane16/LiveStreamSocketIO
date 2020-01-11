from django.shortcuts import render 
from django.http import HttpResponse, JsonResponse
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
options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1}
tfnet = TFNet(options)

class Detector(APIView):

    def post(self, request):
        #url = request.POST.get('image_url','')
        image_file = request.FILES.get('image', False)

        if image_file:
            imgcv = cv2.cvtColor(np.array(io.imread(image_file)), cv2.COLOR_RGB2BGR)
            results = tfnet.return_predict(imgcv)
            font = cv2.FONT_HERSHEY_SIMPLEX #Creates a font

            for result in results:
                x = result["topleft"]["x"]
                y = result["topleft"]["y"]
                w = result["bottomright"]["x"]
                h = result["bottomright"]["y"]
                
                new_img = cv2.cvtColor(imgcv[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
                prediction = Detector.get_colors(new_img,3,False)
                #prediction_text = ""

                if result["confidence"] > 0.5:
                    cv2.rectangle(imgcv, (x,y), (w,h), (255, 0, 0), 2)
                    #print(len(prediction))
                    cv2.putText(imgcv, color.findNearestWebColorName((prediction[0][0],prediction[0][1],prediction[0][2])), (x,y-60), font, 0.7, (0,0,0))
                    cv2.putText(imgcv, color.findNearestWebColorName((prediction[1][0],prediction[1][1],prediction[1][2])), (x,y-40), font, 0.7, (0,0,0))
                    cv2.putText(imgcv, color.findNearestWebColorName((prediction[2][0],prediction[2][1],prediction[2][2])), (x,y-20), font, 0.7, (0,0,0))
                    #print(prediction)
            data = cv2.imencode('.jpg', imgcv)[1].tobytes()
            return HttpResponse(data, content_type="image/jpg")
        else:
            return Response("No image")

    def RGB2HEX(color):
        
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

    def get_colors(image, number_of_colors, show_chart):
        modified_image = cv2.resize(image, (600, 400), interpolation = cv2.INTER_AREA)
        modified_image = modified_image.reshape(modified_image.shape[0]*modified_image.shape[1], 3)

        clf = KMeans(n_clusters = number_of_colors)
        labels = clf.fit_predict(modified_image)

        counts = Counter(labels)

        center_colors = clf.cluster_centers_
        # We get ordered colors by iterating through the keys
        ordered_colors = [center_colors[i] for i in counts.keys()]
        hex_colors = [Detector.RGB2HEX(ordered_colors[i]) for i in counts.keys()]
        rgb_colors = [ordered_colors[i] for i in counts.keys()]
        if (show_chart):
            plt.figure(figsize = (8, 6))
            plt.pie(counts.values(), labels = hex_colors, colors = hex_colors)
        return rgb_colors
