from picamera.array import PiRGBArray
from picamera import PiCamera
import time, cv2, base64, requests, serial

def send_to_EV3(title, content):
	data=[1,0,129,158]
	data.append(len(title)+1)
	for i in title:
		data.append(ord(i))
	data.append(0)
	data.append(len(content)+1)
	data.append(0)
	for i in content:
		data.append(ord(i))
	data.append(0)
	length=len(data)
	data=[length,0]+data
	EV3.write(bytes(data))
def read_from_EV3(length):
	data=EV3.read(length)
	int_values = [x for x in data]
	length_of_title=int_values[6]
	content=int_values[6+length_of_title+3:-1]
	content=list(map(chr,content))
	content=''.join(content)
	return content

EV3 = serial.Serial('/dev/rfcomm0')
camera = PiCamera()
rawCapture = PiRGBArray(camera)
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
check_object_removed=True
time.sleep(0.2)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	try:
		image = frame.array
		rawCapture.truncate(0)
		retval, buffer = cv2.imencode('.jpg',image)
		image_string=base64.b64encode(buffer)
		response=requests.post('http://210.70.165.66:8080', data=image_string)
		response=response.text
		print(response)
		if response!='nothing detected':
			print(check_object_removed)
			if check_object_removed:
				check_object_removed=False
				send_to_EV3('cba', response)
				time.sleep(0.2)
				send_to_EV3('abc', 'start')
				time.sleep(0.2)
				send_to_EV3('abc', 'sdfjgljvsl')
		else:
			send_to_EV3('cba', 'nothing\ndetected')
			check_object_removed=True
		
		cv2.imshow('Frame', image)
		cv2.waitKey(1)
	except:
		cv2.destroyAllWindows()
		break
		
