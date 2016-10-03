import productivity_dynamics as robot
import mpc_productivity as mpc
import data_sender as udp_send
import numpy as np

m = 3
num_steps = 101

sim_model = robot.DynModel(robot.init_state_dim, robot.init_control_dim)
robot.assign_Matrix_coeffs(sim_model.A, sim_model.B)

additional_data = 3
# Total Deliverables Pickup, Total Deliverables Dropoff, delta_charge 
data = np.zeros(1 + sim_model.state_dim + additional_data)

curr_state = sim_model.eta_k
ctrl_idx = 0
for i in range(num_steps):
    
    if (i%m == 0):
        #[result_x, y, delta, u_opt, z] = mpc.run_mpc(curr_state)
        [x, y, u_opt, delta] = mpc.run_mpc(curr_state)        
        ctrl_idx = 0
        print u_opt.value
    
    u = u_opt.value[:, ctrl_idx]

    # See MPC Productivity.py
    # u_pickup = u_ipu + u_wpu
    # u_dropoff = u_ido + u_wdo
    u_total_pickup = u[2] + u[4] - (u[3] + u[5])
    u_total_dropoff = u[3] + u[5] - (u[2] + u[4])
    delta_charge = delta.value[1, ctrl_idx] 

    # print "input: "
    # print u

    if i == 0:
        data[0] = i * robot.delta_t;
        for j in range(sim_model.state_dim):
            data[j+1] = curr_state[j]

        data[-3] = u_total_pickup
        data[-2] = u_total_dropoff
        data[-1] = delta_charge        

        udp_send.update(data)
        udp_send.send()        

    sim_model.set_eta_k_xi_k(curr_state, u)
    curr_state = sim_model.compute_x_k1()

    # print "state: "
    # print curr_state
    
    data[0] = (i+1) * robot.delta_t;
    for j in range(sim_model.state_dim):
        data[j+1] = curr_state[j]

    data[-3] = u_total_pickup
    data[-2] = u_total_dropoff
    data[-1] = delta_charge        

    udp_send.update(data)
    udp_send.send()

    ctrl_idx += 1
