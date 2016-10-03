import socket
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

##=== State
fig_state = plt.figure(figsize=(12,8), tight_layout=True)
fig_state.patch.set_facecolor('white')
#num_state = 5
num_state = 8 
data_list = []

line_state = []
fig_ax = []


steps_to_show = 80

STEP = 1
LINE = 0
plot_label = ['R_x', 'R_b', 'R_d', 'R_p', 'H_l',
              'u_{pu}','u_{do}',
              '\delta_{charge}']
plot_type = [LINE,LINE,LINE,LINE,LINE,
             LINE,LINE,
             STEP]
axis_index = [1,2,3,4,5,
              3,3,
              2]
line_style = ['r-','r-', 'r-','r-', 'r-',
              'b-','g-',
              '-b']
y_offset =   [0.0,  0.0, 0.0, 0.0, 0.0,
              -0.01, -0.01,
              0.0]
max_data_list = [10.0, 1.1, 1.0, 0.5, 1.0,
                 1.1, 1.1,
                 1.1]
min_data_list = [0.0, 0.0, 0.0, -0.5, 0.0,
                 0.0, 0.0,
                 0.0]

# Add latex string formatting
for i in range(len(plot_label)):
    plot_label[i] = r"$"+plot_label[i]+"$"


for i in range(0, num_state):
    align_state = '%d1%d' % (num_state, i+1)
    ## Position
    #fig_ax.append( fig_state.add_subplot(align_state) )
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
    
    #line, = fig_ax[i].plot([], [], 'r-', lw = 2)
    line_state.append(line)
    data_list.append([])

for i in range(max(axis_index)):
    name_slice = [idx for idx, curr in enumerate(axis_index) if curr == i+1]
    fig_ax[name_slice[0]].legend(loc=7)

#plt.xlabel(r"$t$"+" (minutes)", fontsize=16)

def init_state():
    for i in range (0, num_state):
        line_state[i].set_data([], [])
    return

time_list = []

def plot_data(i):
    global time_list, data_list, act_list
    # Link locations
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    num_string = data.split(', ')
    
    sim_time = float(num_string[0])
    print "simulation time: %f" %(sim_time)
    
    # Initialize
    if sim_time < 0.05:
        time_list = []
        for k in range(0, num_state):
            data_list[k] = []
            line_state[k].set_data([], [])
                
    time_list.append(sim_time)

    for k in range(0, num_state):
        data_list[k].append(float(num_string[k + 1]) + y_offset[k])
        line_state[k].set_data(time_list, data_list[k])

        max_data = max_data_list[k] #max(data_list[k]) + 0.01
        min_data = min_data_list[k] #min(data_list[k]) - 0.01
        fig_ax[k].set_ylim(min_data, max_data)
        fig_ax[k].set_xlim(min(time_list), max(time_list))

    return line_state


state = animation.FuncAnimation(fig_state, plot_data, np.arange(1, 800),
                               interval = 5, blit = False, init_func = init_state)



plt.show()        
