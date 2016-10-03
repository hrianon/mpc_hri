import serial
from msvcrt import getch

gazeKey = 0xA7
gazeFocus = 128
gazePitch = 128
gazeYaw = 128

ser = serial.Serial('COM12', 115200, parity='N')

gazePitch = 128
gazeYaw = 128

newCommand = gazeKey*0x1000000 + gazeFocus*0x10000 + gazePitch*0x100 + gazeYaw
newMessage = str(newCommand) + "\r"
ser.write(newMessage)