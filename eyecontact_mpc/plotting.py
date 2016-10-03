import socket
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

##=== State
fig_state = plt.figure(figsize=(12,8), tight_layout=True)

num_state = 9
data_list = []
time_list = []
line_state = []
fig_ax = []


max_time_on_x_axis = 90.


STEP = 1
LINE = 0
plot_label = ['x1','x2',
              'u0','u1',
              'u2','u3',
              'u4','d','z']
plot_type = [LINE,LINE,
             STEP,STEP,
             STEP,STEP,STEP,
             STEP,LINE]
axis_index = [1,1,
              2,2,
              3,3,
              4,4,4]
line_style = ['r-','b-',
              'r-','b-',
              'r-','g-',
              'b-','r-','g-']
y_offset =   [0.0,  0.0,
              0.0, 0.03,
              0.0, 0.03,
              0.03, 0.0, 0.0]





for i in range(0, num_state):
    # align_state = '%d2%d' % (num_state, i+1)
    ## Position
    # fig_ax.append( fig_state.add_subplot(align_state) )
    # fig_ax.append( fig_state.add_subplot(num_state,1,i+1))
    fig_ax.append( fig_state.add_subplot(max(axis_index),1,axis_index[i]) )
    fig_ax[i].autoscale_view(True,True,True)
    fig_ax[i].grid()
    # print i
    # print [idx for idx, curr in enumerate(axis_index) if curr == axis_index[i]]
    name_slice = [idx for idx, curr in enumerate(axis_index) if curr == axis_index[i]]
    label_name = [ plot_label[idx] for idx in name_slice ]
    # print label_name
    plt.ylabel(', '.join(label_name))

    # if plot_type[i] == LINE:
    #     line, = fig_ax[axis_index[i]-1].plot([], [], 'r-', lw = 2)
    # else:
    #     line, = fig_ax[axis_index[i]-1].step([], [], 'r-', lw = 2)

    if plot_type[i] == LINE:
        line, = fig_ax[i].plot([], [], line_style[i], lw = 2)
    else: # plot_type[i] == STEP
        line, = fig_ax[i].step([], [], line_style[i], lw = 2)

    line_state.append(line)
    data_list.append([])

# plt.tight_layout()


def init_state():
    for i in range (0, num_state):
        line_state[i].set_data([], [])
    return



def plot_data(i):
    global time_list, data_list, act_list
    # Link locations
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # print data
    num_string = data.split(', ')

    sim_time = float(num_string[0])
    print "sim time: %f" %(sim_time)

    # Initialize
    if sim_time < 0.05:
        time_list = []
        for k in range(0, num_state):
            data_list[k] = []
            line_state[k].set_data([], [])

    time_list.append(sim_time)

    for k in range(0, num_state):
        # print num_string
        data_list[k].append(float(num_string[k + 1]) + y_offset[k])
        line_state[k].set_data(time_list, data_list[k])

        # print k
        data_list_slice = [idx for idx, curr in enumerate(axis_index) if curr == axis_index[k]]
        # print data_list_slice

        max_data = max([ max(data_list[idx]) for idx in data_list_slice if len(data_list[idx]) > 0 ])
        min_data = min([ min(data_list[idx]) for idx in data_list_slice if len(data_list[idx]) > 0 ])

        # max_data = max(data_list[k])
        # min_data = min(data_list[k])
        difference =  max_data - min_data
        max_data += difference*0.1
        min_data -= difference*0.1
        fig_ax[k].set_ylim(min_data, max_data)
        min_time = min(time_list)
        max_time = max(time_list)
        fig_ax[k].set_xlim( max( min_time, max_time-max_time_on_x_axis ) , max_time)

    return line_state


state = animation.FuncAnimation(fig_state, plot_data, np.arange(1, 800),
                               interval = 5, blit = False, init_func = init_state)

plt.show()
