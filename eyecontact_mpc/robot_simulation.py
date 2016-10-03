import data_sender as udp_send
import datetime
import eye_contact_dynamics as dyn
import math
import mpc_eye_contact as mpc
import numpy as np
import pygame
import random
import serial
import time


ser = serial.Serial('COM12', 115200, parity='N')

gazeKey = 0xA7
gazeFocus = 128
gazePitch = 128
gazeYaw = 128
radiusMin = 32
radiusMax = 64
pi = 3.141592653589

pygame.init()
pygame.display.set_mode((100, 100))

t_now = datetime.datetime.now()
filename = ("./experiment results/%s-%s-%s_%s-%s-%s.txt" % (t_now.year, t_now.month, t_now.day, t_now.hour, t_now.minute, t_now.second) )

fileOutput = open(filename, 'w')
fileOutput.write(filename)
newOutput = "\n\nComfortable Program\n\nsimTime, model.x, model.u, model.d, model.z, systemTime\n\n"
fileOutput.write(newOutput)

M = 3
total_sim_time = 180
dt = 1./3.
num_steps = int( math.ceil( float(total_sim_time)/dt ) )

model = dyn.DynModel(dt)
u = model.u
error_count = 0

data = np.zeros(3 + model.state_dim + model.ctrl_dim)

ctrl_idx = 0

humanLooking = 0
robotLooking = 0
robotLookLast = 0
loopTime = time.time()


for i in range(num_steps):
    #timeStart = time.time()
    if (i % M == 0):
        [x, u_opt, d, z] = mpc.run_mpc(dt, model.x, model.d, model.z, model.u[1], model.u[4])
        ctrl_idx = 0

    try:
        u = u_opt.value[:, ctrl_idx]
        error_count = 0
    except:
        print "Optimizer failed. \nCurrent x: ", x, "\nCurrent u: ", u,"\n"
        if error_count >= 3:
            u[0] = 1 - u[0]
            error_count = 0
        else:
            error_count += 1

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                humanLooking = 1
            elif event.key == pygame.K_r:
                print "reset"
                model.resetStates()
            elif event.key == pygame.K_ESCAPE:
                fileOutput.close()
                gazePitch = 128
                gazeYaw = 128
                newCommand = gazeKey*0x1000000 + gazeFocus*0x10000 + gazePitch*0x100 + gazeYaw
                newMessage = str(newCommand) + "\r"
                ser.write(newMessage)
                print "recentered"
                raise SystemExit(0)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                humanLooking = 0

    # Status of human gaze
    u[1] = humanLooking
    robotLookLast = robotLooking
    robotLooking = u[0]

    
    if robotLooking:   # robot should look at person
        gazePitch = 128
        gazeYaw = 128
        print "at"
    else:   # robot should look away from person
        if (robotLooking != robotLookLast) or (1 == (random.randint(1,int(3./dt)))):
            direction = random.randint(0, 359)
            radius = radiusMin + random.randint(radiusMin, radiusMax)
        gazePitch = int(128 + radius*math.sin(direction*pi/180))
        gazeYaw = int(128 + radius*math.cos(direction*pi/180))
        print "away"
    newCommand = gazeKey*0x1000000 + gazeFocus*0x10000 + gazePitch*0x100 + gazeYaw
    newMessage = str(newCommand) + "\r"
    ser.write(newMessage)

    model.update_udz(u[0],u[1])
    model.update_x()

    data[0]                       = i * dt
    data[1:1+model.state_dim]     = model.x
    data[  1+model.state_dim:-2]  = model.u
    data[-2]                      = model.d
    data[-1]                      = model.z

    newOutput = str(i*dt) + "," + str(model.x) + "," + str(model.u) + "," + str(model.d) + "," + str(model.z) + "," + str(time.time()) + "\n"
    fileOutput.write(newOutput)

    udp_send.update(data)
    udp_send.send()

    ctrl_idx += 1

    loopTime += dt
    timeNow = time.time()
    if timeNow < loopTime:
        time.sleep(loopTime - timeNow)

    #timeEnd = time.time()
    # timeElapsed = timeEnd - timeStart
    # print timeElapsed

fileOutput.close()
gazePitch = 128
gazeYaw = 128
newCommand = gazeKey*0x1000000 + gazeFocus*0x10000 + gazePitch*0x100 + gazeYaw
newMessage = str(newCommand) + "\r"
ser.write(newMessage)
print "recentered"