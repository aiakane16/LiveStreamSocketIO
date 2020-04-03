# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import base64
import io
import cv2
from imageio import imread
import numpy as np
from darkflow.net.build import TFNet
from sklearn.cluster import KMeans
import pandas as pd

options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1  }
tfnet = TFNet(options)

index=["color","color_name","hex","R","G","B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

class ChatConsumer(AsyncWebsocketConsumer):
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
                #print("feature", feature_data)

        #print(feature_data[0])
        #print(feature_data[1])
        #print(feature_data[2])
        
        return ChatConsumer.getColorName(int(feature_data[0]), int(feature_data[1]), int(feature_data[2]))
    
    #function to calculate minimum distance from all colors and get the most matching color
    def getColorName(R,G,B):
        minimum = 10000
        for i in range(len(csv)):
            d = abs(R- int(csv.loc[i,"R"])) + abs(G- int(csv.loc[i,"G"]))+ abs(B- int(csv.loc[i,"B"]))
            if(d<=minimum):
                minimum = d
                cname = csv.loc[i,"color_name"]
        #print(cname)
        return cname


    async def connect(self):
        

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        pass

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("///////////////////////")
        #print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print("this is the message *****************")
        #print(message)

        #out = cv2.VideoWriter('out.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 30, (frame_width,frame_height), 1)
        img = imread(io.BytesIO(base64.b64decode(message)))
        imgcv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        results = tfnet.return_predict(imgcv)
        font = cv2.FONT_HERSHEY_TRIPLEX #Creates a font

        for result in results:
        
            if result["confidence"]:
                x = result["topleft"]["x"]
                y = result["topleft"]["y"]
                w = result["bottomright"]["x"]
                h = result["bottomright"]["y"]
                
                new_img = imgcv[y:h, x:w]
                text = ChatConsumer.convert_image(new_img)
                cv2.rectangle(imgcv, (x,y), (w,h), (255, 0, 0), 10)
                cv2.putText(imgcv, text, (x,y-20), font, 0.7, (0,0,0))
            
            data = cv2.imencode('.jpg', imgcv)[1].tobytes()
        
            b64_bytes = base64.b64encode(data)
            b64_string = b64_bytes.decode()
      
        while True:
            await self.send(text_data=json.dumps({
                'message': str(b64_string)
            }))
            


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))