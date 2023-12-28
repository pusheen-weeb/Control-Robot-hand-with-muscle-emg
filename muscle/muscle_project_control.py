import cv2
import PySimpleGUI as sg
import numpy as np
from collections import deque 
import time
import serial
from threading import Thread
from threading import enumerate
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pyformulas as pf
import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from PyQt5.QtCore import QTimer

#khoi tao serial 
arduinoSerial = serial.Serial('com8', 9600,timeout = 1)
def queue_flush(queue,num_flush):
	for i in range(0,num_flush):
		try:
			queue.get(block=False)
		except:
			break
def gui_data(varCRT_ITF_Queue):
	while True:
		data_gui = varCRT_ITF_Queue.get(block= True)
		data_gui = data_gui[4:10]#only get from variable 4 to 9
		print("Da gui tap tin",data_gui)
		
		arduinoSerial.write(f"<".encode())
		for i in range(0,len(data_gui)-1):
			#gui tung bien co dau phay <n,n,n,>
			arduinoSerial.write(f"{data_gui[i]},".encode())
		#gui bien cuoi khong dau phay <,n>
		arduinoSerial.write(f"{data_gui[-1]}".encode())
		arduinoSerial.write(f">".encode())
		varCRT_ITF_Queue.task_done()

def nhan_data(varCRT_ITF_Queue_FB,
	handMtr_ITF_Queue,
	sen_ITF_Queue):
	print("Listening for incoming seiral")
	while True:
		if arduinoSerial.inWaiting() > 0:
			serial_char = arduinoSerial.read()
			if serial_char == b'<':
				mark_index = 0
				serial_deque = deque()
				while serial_char != b'>':
					serial_char = arduinoSerial.read()
					if serial_char == b'>':
						break
					if serial_char == b',':
						mark_index = mark_index+1
					#int cuoi co 4 byte
					if mark_index == 11:
						serial_deque.append("")
						serial_char = b'0'
						while serial_char != b'>':
							#last is long int read it by concatinate string
							serial_deque[-1]=serial_deque[-1]+(serial_char.decode()) 
							serial_char = arduinoSerial.read()
						mark_index = 0
						break						
					else:
						serial_deque.append(serial_char.decode())
				try:
					dataPacket = "".join(serial_deque)
					#print("dataPacket",dataPacket)
					splitPacket = dataPacket.split(",")
					splitPacket_int = list(map(int, splitPacket))
					#print("splitPacket_int",splitPacket_int)
				except TypeError:
					print("Typeerror cant join:",serial_deque)
					pass
				except ValueError:
					print("ValueError convert int for:",serial_deque)
					pass
				try:
					varCRT_ITF_Queue_FB.put(splitPacket_int,
						block=False,timeout=1)
				except:
					print("varCRT_ITF_Queue_FB full,dumped")
					queue_flush(varCRT_ITF_Queue_FB,9000)
					pass
				try:
					handMtr_ITF_Queue.put(splitPacket_int,
						block=False,timeout=1)
				except:
					print("handMtr_ITF_Queue full,dumped")
					queue_flush(handMtr_ITF_Queue,9000)
					pass 	
				try:
					sen_ITF_Queue.put(splitPacket_int,
						block=False,timeout=1)
				except:
					print("sen_ITF_Queue full,dumped")
					queue_flush(sen_ITF_Queue,9000)
					pass

def twoDof_hand_img(width, height, Q1, Q2, crane1, crane2):
	# width , height: chiều dài, chiều rộng của ảnh, Q1,Q2: góc alpha và beta
	# Crane1,crane2: L1,L2
	# Tạo ảnh đen
	img_crane = np.zeros((height, width, 3), dtype=np.uint8)
	img = np.zeros((height, width, 3), dtype=np.uint8)

	# Khai báo các điểm tay -> từ dưới lên trên O, N, M
	pos_ox, pos_oy = 0, 0
	pos_nx, pos_ny = 0, 0
	pos_mx, pos_my = 0, 0

	# Y phải nhỏ hơn height
	alpha = Q1
	beta = Q2
	# Đổi từ Q độ sang radian
	Q1 = (Q1 * 3.141592) / 180
	Q2 = (Q2 * 3.141592) / 180

	# Hàm tính toán điểm N, M
	pos_nx = crane1 * np.cos(Q1)
	pos_ny = crane1 * np.sin(Q1)

	pos_mx = pos_nx + crane2 * np.cos(Q1+Q2)
	pos_my = pos_ny + crane2 * np.sin(Q1+Q2)

	# Lat hinh 90 do
	temx = [pos_ox,pos_nx,pos_mx]
	temy = [pos_oy,pos_ny,pos_my]
	# lat x
	shift_x = 400
	pos_ox = -temy[0]+shift_x
	pos_nx = -temy[1]+shift_x
	pos_mx = -temy[2]+shift_x
	# lat y
	shift_y = 100
	pos_oy = temx[0]+shift_y
	pos_ny = temx[1]+shift_y
	pos_my = temx[2]+shift_y

	# Vẽ
	# Màu
	rgb1 = [0, 255, 255]
	# Màu 2
	rgb2 = [255, 0, 0]
	# Màu 3
	rgb3 = [255, 221, 0]
	thickness = 2

	# Vẽ cánh tay
	cv2.line(img_crane, (int(pos_ox), int(pos_oy)), (int(pos_nx), int(pos_ny)), (rgb1), thickness)
	cv2.line(img_crane, (int(pos_nx), int(pos_ny)), (int(pos_mx), int(pos_my)), ([255,50,100]), thickness)

	# Vẽ hình tròn đại diện dau tay
	cv2.circle(img_crane, (int(pos_mx), int(pos_my)), 10, (rgb2), -1, 8)

	# Vẽ hình tròn đại diện cho khop thu 1
	cv2.circle(img_crane, (int(pos_ox), int(pos_oy)), 10, (rgb2), -1, 8)

	# Vẽ hình tròn đại diện kho thu 2
	cv2.circle(img_crane, (int(pos_nx), int(pos_ny)), 10, ([255,0,100]), -1, 8)

	# Thêm văn bản (tên khu vực)
	text_down = 25  # Khoảng cách giữa đỉnh và văn bản

	cv2.putText(img_crane, "Alpha = "+str(alpha), (10, text_down), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (rgb1), 1)
	cv2.putText(img_crane, "Beta = "+str(beta), (int(pos_ox) + 200, text_down), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (rgb1), 1)

	# Gộp ảnh
	img = img + img_crane
	return img_crane

def handMtr_ITF(handMtr_ITF_Queue):
	print("running handMtr_ITF")
	while True:
		try:
			new_data = handMtr_ITF_Queue.get(block=True)
		except:
			print("handMtr_ITF got nothing")
			pass
		image = twoDof_hand_img(800, 500, new_data[2],new_data[3], 200,176)
		cv2.imshow('Hand monitor',image)
		if cv2.waitKey(25) & 0xFF == ord('q'):
			break

class RealTimePlot(QMainWindow):
	def __init__(self,sen_ITF_Queue):
		super().__init__()

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_plot)
		self.timer.start(1)  # Update every 1000 milliseconds (1 second)

		self.queue_size = 1000
		self.cb1 = deque()
		self.cb2 = deque()
		self.thresh_array = np.ones((self.queue_size,), dtype=int)
		self.timestamp = deque()

		self.minY=0
		self.maxY=200
		self.minX=0
		self.maxX=200
		
		self.queue = sen_ITF_Queue
		self.new_data = [0,0,0,0,0,0,0,0,0,0,0]

		self.initUI()

	def initUI(self):
		self.centralWidget = pg.GraphicsLayoutWidget(self)
		self.setCentralWidget(self.centralWidget)

		self.plot_widget = self.centralWidget.addPlot(title="Real-time plot")
		self.plot_widget.showGrid(True, True)
		self.plot_widget.setYRange(self.minY, self.maxY)

		# Add legends
		self.plot_widget.addLegend()

		self.plot_sensor1= self.plot_widget.plot(pen='r', name='Sensor 1')
		self.plot_sensor2 = self.plot_widget.plot(pen='b', name='Sensor 2')
		self.plot_sen1_thresh_top = self.plot_widget.plot(pen='y', name='Sensor 1 top limit')
		self.plot_sen1_thresh_bot = self.plot_widget.plot(pen='y', name='Sensor 1 bot limit')
		self.plot_sen2_thresh_top = self.plot_widget.plot(pen='g', name='Sensor 2 top limit')
		self.plot_sen2_thresh_bot = self.plot_widget.plot(pen='g', name='Sensor 2 bot limit')

	def update_plot(self):
		# get new value from queue
		self.new_data = self.queue.get(block=True)

		#print(self.new_data)
		new_cb1 = self.new_data[0]
		new_cb2 = self.new_data[1]
		new_timestamp = self.new_data[10]

		# Accumulate data
		#time stamp overflow handle
		if (new_timestamp<0 and self.timestamp[-1]>0):
			self.cb1.clear()
			self.cb2.clear()
			self.timestamp.clear()

		self.cb1.append(new_cb1)
		self.cb2.append(new_cb2)
		self.timestamp.append(new_timestamp)
		if len(self.cb1) >= self.queue_size:
			self.cb1.popleft()
			self.cb2.popleft()
			self.timestamp.popleft()

		#thresh line
		self.thresh_array = np.ones((len(self.cb1),), dtype=int)
		cb1_bot= self.thresh_array*self.new_data[4]
		cb1_top= self.thresh_array*self.new_data[5]
		cb2_bot= self.thresh_array*self.new_data[7]
		cb2_top= self.thresh_array*self.new_data[8]

		self.minY=min(self.minY,min(new_cb1,new_cb2))
		self.maxY=max(self.maxY,max(new_cb1,new_cb2))
		#print("new timeStamp",new_timestamp)
		# Update the entire plot data
		self.plot_widget.setXRange(new_timestamp-10000,new_timestamp+10000)		
		self.plot_widget.setYRange(self.minY, self.maxY+50)
		
		self.plot_sensor1.setData(x=self.timestamp,y=self.cb1, name='Sensor 1')
		self.plot_sensor2.setData(x=self.timestamp,y=self.cb2, name='Sensor 2')
		self.plot_sen1_thresh_bot.setData(x=self.timestamp,y=cb1_bot, name='Sensor 1 bot limit')
		self.plot_sen1_thresh_top.setData(x=self.timestamp,y=cb1_top, name='Sensor 1 top limit')
		self.plot_sen2_thresh_bot.setData(x=self.timestamp,y=cb2_bot, name='Sensor 2 bot limit')
		self.plot_sen2_thresh_top.setData(x=self.timestamp,y=cb2_top, name='Sensor 2 top limit')

def plot_real_time(sen_ITF_Queue):
	app = QApplication(sys.argv)
	mainWindow = RealTimePlot(sen_ITF_Queue)
	mainWindow.setGeometry(100, 100, 800, 600)  # Set window size
	mainWindow.show()
	sys.exit(app.exec_())

def varCRT_ITF(varCRT_ITF_Queue,varCRT_ITF_Queue_FB):
	print("running varCRT_ITF")
	#khoi tao cac bien bang dieu khien
	prechanged_values = [0,0,0,0,0,0,0,0,0,0,0]
	changed_values = [0,0,0,0,0,0,0,0,0,0,0]
	#prechanged_values[4] = minSensor1
	#prechanged_values[5] = maxSensor1
	#prechanged_values[6] = nLSkipServo1
	#prechanged_values[7] = minSensor2
	#prechanged_values[8] = maxSensor2
	#prechanged_values[9] = nLSkipServo2

	# Define the layout of the GUI
	layout = [
		[sg.Text('Enter new values:'), sg.Text(' ' * 85), sg.Text('Current values:')],
		[
			sg.Column([
				[sg.Text('minSensor1:'), sg.InputText(default_text=str(prechanged_values[4]), key='prechange_minSensor1')],
				[sg.Text('maxSensor1:'), sg.InputText(default_text=str(prechanged_values[5]), key='prechange_maxSensor1')],
				[sg.Text('nLSkipServo1:'), sg.InputText(default_text=str(prechanged_values[6]), key='prechange_nLSkipServo1')],
				[sg.Text('minSensor2:'), sg.InputText(default_text=str(prechanged_values[7]), key='prechange_minSensor2')],
				[sg.Text('maxSensor2:'), sg.InputText(default_text=str(prechanged_values[8]), key='prechange_maxSensor2')],
				[sg.Text('nLSkipServo2:'), sg.InputText(default_text=str(prechanged_values[9]), key='prechange_nLSkipServo2')],
			], element_justification='right'),
			sg.VerticalSeparator(),
			sg.Column([
				[sg.Text('minSensor1:', size=(15, 1), justification='right'), sg.Text('', size=(10, 1), key='changed_minSensor1')],
				[sg.Text('maxSensor1:', size=(15, 1), justification='right'), sg.Text('', size=(10, 1), key='changed_maxSensor1')],
				[sg.Text('nLSkipServo1:', size=(15, 1), justification='right'), sg.Text('', size=(10, 1), key='changed_nLSkipServo1')],
				[sg.Text('minSensor2:', size=(15, 1), justification='right'), sg.Text('', size=(10, 1), key='changed_minSensor2')],
				[sg.Text('maxSensor2:', size=(15, 1), justification='right'), sg.Text('', size=(10, 1), key='changed_maxSensor2')],
				[sg.Text('nLSkipServo2:', size=(15, 1), justification='right'), sg.Text('', size=(10, 1), key='changed_nLSkipServo2')],
			], element_justification='right', key='changed_values_column')
		],
		[sg.Button('Update Values'), sg.Button('Exit')],
	]

	# Create the window
	window = sg.Window('Values Settings', layout)

	# Event loop
	while True:
		event, values = window.read(timeout=0)
		if event == sg.WIN_CLOSED or event == 'Exit':
			break
		# Update GUI valuable
		if event == sg.WIN_CLOSED or event == 'Update Values':
			try:
				prechanged_values[4] = int(values['prechange_minSensor1'])
				prechanged_values[5] = int(values['prechange_maxSensor1'])
				prechanged_values[6] = int(values['prechange_nLSkipServo1'])
				prechanged_values[7] = int(values['prechange_minSensor2'])
				prechanged_values[8] = int(values['prechange_maxSensor2'])
				prechanged_values[9] = int(values['prechange_nLSkipServo2'])
			except:
				pass
		
		#check min max threshold if min > max reset both to 0
		if prechanged_values[4]>prechanged_values[5]:
			prechanged_values[4]=0
			prechanged_values[5]=0
			print("Error min sensor 1 > max sensor 1, reset not to 0")
		if prechanged_values[7]>prechanged_values[8]:
			prechanged_values[7]=0
			prechanged_values[8]=0
			print("Error min sensor 2 > max sensor 2, reset not to 0")
		
		#update new value to send down
		if (prechanged_values[4:10] != changed_values[4:10]):
			print("value not match updating value")
			try:
				varCRT_ITF_Queue.put(prechanged_values)
			except:
				print("Cant update prechange value")
				pass
		#print(prechanged_values[4:10])
		#get current value of variables from queue
		try:
			changed_values = varCRT_ITF_Queue_FB.get(block=True)
		except:
			print("varCRT_ITF_Queue empty interface receive nothing")
			pass
		# Update the 'Changed values' text elements
		window['changed_minSensor1'].update(changed_values[4])
		window['changed_maxSensor1'].update(changed_values[5])
		window['changed_nLSkipServo1'].update(changed_values[6])
		window['changed_minSensor2'].update(changed_values[7])
		window['changed_maxSensor2'].update(changed_values[8])
		window['changed_nLSkipServo2'].update(changed_values[9])

	# Close the window
	print("Closed variable control")
	window.close()
	for thread in enumerate(): 
		print(thread.name)

def main():
	#data he thong = [0,0,0,0,0,0,0,0,0,0,0] # 11 bien int
	# 0,1 valsensor 1,2
	# 2,3 servo 1,2
	# 4,5,6 min,max,sensor 1,skip_step servo 1
	# 7,8,9 min,max,sensor 2,skip_step servo 2
	# 10 time elapse of microchip

	varCRT_ITF_Queue = queue.Queue(maxsize = 100)
	varCRT_ITF_Queue_FB = queue.Queue(maxsize = 100)
	handMtr_ITF_Queue = queue.Queue(maxsize = 100)
	sen_ITF_Queue = queue.Queue(maxsize = 100)
	
	#thread man hinh dieu khien bien
	varCRT_ITF_thread = Thread(target=varCRT_ITF,
		args=(varCRT_ITF_Queue,
			varCRT_ITF_Queue_FB))
	varCRT_ITF_thread.start()

	#thread nhan serial
	nhan_serial_thread = Thread(target=nhan_data,
		args=(varCRT_ITF_Queue_FB,
			handMtr_ITF_Queue,
			sen_ITF_Queue))
	nhan_serial_thread.deamon =True
	nhan_serial_thread.start()
	
	#thread gui serial
	gui_serial_thread = Thread(target=gui_data,
		args=(varCRT_ITF_Queue,))
	gui_serial_thread.deamon =True
	gui_serial_thread.start()

	#thread hand monitor
	handMtr_ITF_thread = Thread(target=handMtr_ITF,
		args=(handMtr_ITF_Queue,))
	handMtr_ITF_thread.deamon=True
	handMtr_ITF_thread.start()

	#thread plot sensor
	plot_real_time(sen_ITF_Queue)

	varCRT_ITF_thread.join()
def main_test():
	varCRT_ITF_Queue = queue.Queue(maxsize = 100)
	varCRT_ITF_Queue_FB = queue.Queue(maxsize = 100)
	handMtr_ITF_Queue = queue.Queue(maxsize = 100)
	sen_ITF_Queue = queue.Queue(maxsize = 100)

	#thread nhan serial
	nhan_serial_thread = Thread(target=nhan_data,
		args=(varCRT_ITF_Queue_FB,
			handMtr_ITF_Queue,
			sen_ITF_Queue))
	nhan_serial_thread.deamon =True
	nhan_serial_thread.start()

if __name__=='__main__':
	main()
	
