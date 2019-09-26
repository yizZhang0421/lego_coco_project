#import os
#os.chdir('C:/Users/Administrator/Desktop/face_recognize_demo/darkflow-master')
from darkflow.net.build import TFNet
import cv2, base64
import numpy as np
options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.1}
tfnet = TFNet(options)
detect_list=['bottle','pottedplant']
from flask import Flask, request
from keras.models import load_model
from tensorflow import Graph, Session
app = Flask(__name__)

graph=Graph()
with graph.as_default():
    session=Session(graph=graph)
    with session.as_default():
        model=load_model('CNNmodel/bottle.h5')

@app.route('/',methods=['POST'])
def login():
    global graph
    global session
    global model
    img=bytes(request.data)
    img=base64.b64decode(img)
    img=np.frombuffer(img, dtype=np.uint8)
    img=cv2.imdecode(img,cv2.IMREAD_COLOR)
    #cv2.imwrite('test.png',img)
    
    result = tfnet.return_predict(img)
    final_obj=None
    return_string=''
    for obj in result:
        try:
            detect_list.index(obj['label'])
        except:
            continue
        if final_obj==None or obj['confidence']>final_obj['confidence']:
            final_obj=obj
        if final_obj!=None:
            tl = (final_obj['topleft']['x'],final_obj['topleft']['y'])
            br = (final_obj['bottomright']['x'],final_obj['bottomright']['y'])
            img_crop = img[tl[1]:br[1] , tl[0]:br[0]]
            img_crop=cv2.resize(img_crop,(64,64),interpolation=cv2.INTER_CUBIC)
            img_crop=img_crop/255
            img_crop=np.array([img_crop])
            with graph.as_default():
                with session.as_default():
                    return_string=str(model.predict_classes(img_crop)[0])
                    print(return_string)
        break
    if return_string=='':
        return 'nothing detected'
    else:
        return return_string


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9487)