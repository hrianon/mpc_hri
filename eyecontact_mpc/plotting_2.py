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
current_idx = 0


steps_to_show = 80

STEP = 1
LINE = 0
plot_label = ['x_1','x_2',
              'u_0','u_1',
              'u_2','u_3',
              'u_4','d','z']
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
max_data_list = [100., 100.,
              1.1, 1.1,
              1.1, 1.1,
              11., 11., 11.]
min_data_list = [0., 0.,
              -0.1, -0.1,
              -0.1, -0.1,
              -1., -1., -1.]

# Add latex string formatting
for i in range(len(plot_label)):
    plot_label[i] = r"$"+plot_label[i]+"$"


for i in range(num_state):
    # align_state = '%d2%d' % (num_state, i+1)
    ## Position
    # fig_ax.append( fig_state.add_subplot(align_state) )
    # fig_ax.append( fig_state.add_subplot(num_state,1,i+1))
    fig_ax.append( fig_state.add_subplot(max(axis_index),1,axis_index[i]) )
    fig_ax[i].autoscale_view(True,True,True)
    fig_ax[i].grid(True)

    name_slice = [idx for idx, curr in enumerate(axis_index) if curr == axis_index[i]]
    label_name = [ plot_label[idx] for idx in name_slice ]
    plt.ylabel(', '.join(label_name), fontsize=16)



    if plot_type[i] == LINE:
        line, = fig_ax[i].plot([], [], line_style[i], lw = 2, label=plot_label[i])
    else: # plot_type[i] == STEP
        line, = fig_ax[i].step([], [], line_style[i], lw = 2, label=plot_label[i])


    line_state.append(line)
    data_list.append([])

for i in range(max(axis_index)):
    name_slice = [idx for idx, curr in enumerate(axis_index) if curr == i+1]
    fig_ax[name_slice[0]].legend(loc=7)


plt.xlabel(r"$t$"+" (seconds)", fontsize=16)



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

    if len(time_list) == steps_to_show:
      time_list = time_list[1:]
    time_list.append(sim_time)

    for k in range(0, num_state):
        # print num_string
        if len(data_list[k]) == steps_to_show:
          data_list[k] = data_list[k][1:]
        data_list[k].append(float(num_string[k + 1]) + y_offset[k])

        line_state[k].set_data(time_list, data_list[k])

        # print k
        data_list_slice = [idx for idx, curr in enumerate(axis_index) if curr == axis_index[k]]
        # print data_list_slice

        max_data = max_data_list[k]
        min_data = min_data_list[k]
        #max_data = max([ max(data_list[idx]) for idx in data_list_slice if len(data_list[idx]) > 0 ])
        #min_data = min([ min(data_list[idx]) for idx in data_list_slice if len(data_list[idx]) > 0 ])

        # max_data = max(data_list[k])
        # min_data = min(data_list[k])
        difference =  max_data - min_data
        max_data += difference*0.1
        min_data -= difference*0.1
        fig_ax[k].set_ylim(min_data, max_data)
        min_time = min(time_list)
        max_time = max(time_list)
        fig_ax[k].set_xlim( min_time , max_time)

    return line_state


state = animation.FuncAnimation(fig_state, plot_data, np.arange(1, 800),
                               interval = 5, blit = False, init_func = init_state)

plt.show()
