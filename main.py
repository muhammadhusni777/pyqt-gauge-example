import sys
import os


from PyQt5 import QtGui, QtCore, Qt
from PyQt5.QtCore    import pyqtSlot, pyqtSignal, QUrl, QObject,QStringListModel, Qt
from PyQt5.QtQuick   import QQuickView
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QSlider
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtChart import* #


import paho.mqtt.client as paho
#broker="123.45.0.10"
broker="127.0.0.1"
port = 1883

S1 = 0
S2 = 0
S3 = 0
S4 = 0


def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	t = str(message.topic)

	if(msg[0] == 'c'):
		val =  1
	else:
		val = int(msg)

	if (t == "speedinput1"):
		global S1
		S1 = float(msg)
		print(S1)
        
	if (t == "speedinput2"):
		global S2
		S2 = float(msg)


class Tablero(QQuickView):  

	####### REGISTROS a transferir de PYTHON a QML
	valGauge1 = pyqtSignal(str)
	valGauge2 = pyqtSignal(str)
	valGauge3 = pyqtSignal(str) 
	valGauge4 = pyqtSignal(str)
	
	valPin6 = pyqtSignal(str)
	valPin7 = pyqtSignal(str)
	valPin8 = pyqtSignal(str)
	valPin9 = pyqtSignal(str)
	
	def __init__(self):
		super().__init__()
		self.setSource(QUrl('Tablero_V1_edited.qml'))
		#self.setSource(QUrl('simplegraph.qml'))
		self.rootContext().setContextProperty("Tablero", self)
		self.setGeometry(100, 100, 1100, 520)
		self.show()
		vista = self.rootObject()
		#self.initUART('/dev/ttyUSB0')  # En Linux
		#self.initUART('COM8')  # En windows de COM4 a COM 30
		self.iniTemporizador()
		
		####### DATOS a transferir de PYTHON a QML
		self.valGauge1.connect(vista.actScale1)
		self.valGauge2.connect(vista.actScale2)
		self.valGauge3.connect(vista.actScale3)
		self.valGauge4.connect(vista.actScale4)
		
		self.valPin6.connect(vista.actPin6)
		self.valPin7.connect(vista.actPin7)
		self.valPin8.connect(vista.actPin8)
		self.valPin9.connect(vista.actPin9)
	


	####### DATOS a transferir de QML a (PYTHON ARDUINO)

	@pyqtSlot('int','QString')
	def setLed(self, led, value):
		dataled=str(led)+value
		#print("led ",led," value ",value)
		#self.ser.write(dataled.encode())

	@pyqtSlot('QString','QString')
	def setPwm(self, pin, value):
		datapinpwm =pin+value
		#print (datapinpwm)
		#self.ser.write((pin+value).encode())

	def iniTemporizador(self):
		self.temporizador = QtCore.QTimer()
		self.temporizador.timeout.connect(self.metMuestreo)
		self.temporizador.start(500)
		
	def metMuestreo(self):
		####### Transferencia a QML
		#data = self.ser.read(1)
		#n = self.ser.inWaiting()
		#print (n)
		#while n:
			#data = data + self.ser.read(n)
			#n = self.ser.inWaiting()
			####### lecturas analogas
		st1=S1#data[0]*256+data[1]
		st2=S2#data[2]*256+data[3]
		st3=0#data[4]*256+data[5]
		st4=0#data[6]*256+data[7]
			#print (st1," ",st2," ",st3," ",st4)
			
			######## Lecturas de pulsadores
		Pin6=0#data[16]*256+data[17]
		Pin7=0#data[18]*256+data[19]
		Pin8=0#data[20]*256+data[21]
		Pin9=0#data[22]*256+data[23]
			#print (Pin6," ",Pin7," ",Pin8," ",Pin9)
			
			######## Envio datos a funciones de transferencia
		self.valGauge1.emit(str(st1))
		self.valGauge2.emit(str(st2))
		self.valGauge3.emit(str(st3))
		self.valGauge4.emit(str(st4))
			
		self.valPin6.emit(str(Pin6))
		self.valPin7.emit(str(Pin7))
		self.valPin8.emit(str(Pin8))
		self.valPin9.emit(str(Pin9))
			
		self.temporizador.start(50)

if __name__ == '__main__':
    
	app = QApplication(sys.argv)
	
	client= paho.Client("GUI")
	client.on_message=on_message

	print("connecting to broker ",broker)
	client.connect(broker,port)#connect
	print(broker," connected")


	client.loop_start()
	print("Subscribing")
    
	client.subscribe("speedinput1")
	client.subscribe("speedinput2")
	
	w = Tablero()
	sys.exit(app.exec_())

