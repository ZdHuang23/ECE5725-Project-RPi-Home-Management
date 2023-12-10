import cv2
import numpy as np
import os 

class face_recog():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trained_faces.yml')
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    image_path = '/home/pi/proj/my_photo.jpg'
    folder_path = '/home/pi/proj/photohistory'
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # names related to ids: example ==> Marcelo: id=1,  etc
    names = ['Unknown', 'Zidong'] 
    
    # Initialize and start realtime video capture
    
    # Define min window size to be recognized as a face
    def __init__(self):
        return

    
    def recognize(self,threshold):
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video widht
        cam.set(4, 480) # set video height
        minW = 0.1*cam.get(3)
        minH = 0.1*cam.get(4)
    
        counter = {"Unknown": 0, "Zidong": 0}

        #iniciate id counter
        id = 0 
        frame = 0
        code_run = True
        while code_run:
            ret, img =cam.read()
            #img = cv2.flip(img, -1) # Flip vertically
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            
            faces = self.faceCascade.detectMultiScale( 
                gray,
                scaleFactor = 1.1,
                minNeighbors = 3,
                minSize = (int(minW), int(minH)),
            )

            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = self.recognizer.predict(gray[y:y+h,x:x+w])
        
                # Check if confidence is less than 100 ==> "0" is perfect match 
                if (confidence < 100):                  
                    name = self.names[id]
                    counter[name] = counter[name] + 1
                    #confidence = "  {0}%".format(round(100 - confidence))
                else:
                    counter["Unknown"] = counter["Unknown"] + 1
                    #confidence = "  {0}%".format(round(100 - confidence))
                # cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
                # cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
            
            # cv2.imshow('camera',img) 
        
            k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break
            frame += 1 
            if frame >= 10 :
                code_run = False
        #cv2.destroyAllWindows()
        #print(f"Zidong: {counter['Zidong']}")
        #print(f"Unknown: {counter['Unknown']}")
        # if counter[max(counter, key=counter.get)] > 0:

        
        if (counter['Zidong']+counter['Unknown'] == 0) :
            return 'No Face' , "None"  # no face
        else :
            # print("Zidong:"+str(counter['Zidong']),"Unknown:"+str(counter['Unknown']))
            existing_images = [int(filename.split('_')[1].split('.')[0]) for filename in os.listdir(self.folder_path) if filename.endswith('.jpg')]
            max_index = max(existing_images) if existing_images else 0

            ret, frame = cam.read()

            image_path = os.path.join(self.folder_path, f"image_{max_index + 1}.jpg")
            cam.release()
            if counter['Unknown'] > threshold:
                cv2.imwrite(image_path, frame)
                return 'Unknown' , image_path
            elif counter["Zidong"] > threshold:
                cv2.imwrite(image_path, frame)
                return 'Zidong' , image_path #Unknown
            else:
                return 'No Face' , "None"  # no face

        # Do a bit of cleanup
        #print("\n [INFO] Exiting Program and cleanup stuff")
        
        # else:
        #     return "No face"
        # cam.release()
        # return max(counter, key=counter.get)

if __name__ == "__main__":
    face = face_recog()
    while True:
        a, b = face.recognize(2)
        print(a,b)
# import cv2
# import numpy as np
# import picamera
# import time

# # 加载人脸检测器和人脸识别器
# face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# recognizer = cv2.face.LBPHFaceRecognizer_create()

# # 加载预训练的人脸识别模型（这里假设已经有预先保存的模型）
# recognizer.read('trained_faces.yml')

# # 拍摄照片并保存
# def take_photo(file_path):
#     with picamera.PiCamera() as camera:
#         camera.resolution = (320, 240)  # 设置摄像头分辨率
#         camera.start_preview()  # 开启预览
#         time.sleep(2)  # 等待摄像头启动

#         camera.capture(file_path)  # 拍照并保存到指定路径
#         print(f"照片已保存至 {file_path}")

# # 保存拍摄的照片
# image_path = '/home/pi/proj/my_photo.jpg'
# take_photo(image_path)

# # 加载拍摄的照片
# img = cv2.imread(image_path)

# # 将图像转换为灰度图像（人脸检测需要）
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # 使用人脸检测器检测图像中的人脸
# faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

# if len(faces) > 0:
#     # 对每张检测到的人脸进行识别
#     for (x, y, w, h) in faces:
#         roi_gray = gray[y:y+h, x:x+w]  # 获取感兴趣区域（ROI）
        
#         # 尝试识别人脸
#         id, confidence = recognizer.predict(roi_gray)
        
#         # 显示识别结果
#         if confidence < 100:  # 设置阈值
#             if id==1:
#                 label = f"Yuqiang"
#         else:
#             label = "Unknown"
        
#         cv2.putText(img, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
#     # 在窗口中显示图像
#     cv2.imshow('Detected Faces', img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# else:
#     print("未检测到人脸")
