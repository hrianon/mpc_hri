from cvxpy import *
from productivity_dynamics import *
import numpy as np

model = DynModel(init_state_dim, init_control_dim)
assign_Matrix_coeffs(model.A, model.B)

print model.A
print model.B
print model.eta_k.shape

Ax = model.A * delta_t + np.identity(init_state_dim)
B1 = model.B * delta_t
C = model.C
x_0 = model.eta_k


# ### MPC paramters
num_bool = 3
p = 5 # controller horizon p
T = p
# x = [Rpos, Rbattery, Rconsumables, Rproductivity, Hload]
# u = [move, charge, u_InventoryPickUp, u_InventoryDropOff, u_WorkSationPickUp, u_WorkstationDropoff]
# y = [battery, prod, workload]

x = Variable(init_state_dim, T+1)
u = Variable(init_control_dim, T)
y = Variable(n_y, T+1)
delta = Bool(num_bool, T)

# delta = []
# 0 - delta_battery (battery left)
# 1 - delta_charge INPUT
# 2 - delta_cpu (consumables pick up) INPUT
# 3 - delta_cdo (consumables drop off) INPUT
# 4 - delta_wpu (waste pick up) INPUT
# 5 - delta_wdo (waste drop off) INPUT
# 6 - delta_prod (human productivity) INPUT

#delta = [delta_battery, delta_charge, delta_joke]

delta_move_pos = Bool(1, T)
delta_move_neg = Bool(1, T)

# Constraint parameters
u_move_min = -12
u_move_max = 12

battery_max = 1.0
battery_min = 0

x_pos_max = 9.8


battery_level_no_movement = 0.2
battery_pos = 1
dist_tresh = 0.0
human_pos = 9


productivity_target = 1.0
workload_target = 0.15

# Weights
w_battery = 1.0
w_prod = 1.0
w_load = 10.0


w_y = np.array([w_battery, w_prod, w_load])
Qy = np.matrix([ [w_battery, 0, 0],
                 [0, w_prod, 0],
                 [0, 0, w_load] ])

w_move = 0.00005
Qw = np.matrix([ [w_move] ])

print Qy

gamma_move_penalty = 0.04

y_ref = [battery_max, productivity_target, workload_target]
def run_mpc(starting_x_state=model.eta_k):
  states = []
  for t in range(T):
      cost = quad_form((y[:, t+1] - y_ref), Qy) #+ quad_form(u[0,t], Qw)
      constr = [x[:,t+1] == Ax*x[:,t] + B1*u[:,t] ,
                y[:,t+1] == C * x[:, t+1],
                # ucharge = delta_charge
                u[1,t] == delta[1,t] - ( (delta_move_pos[0,t] + delta_move_neg[0,t]) * gamma_move_penalty ),

                # Movement penalty
                u[0,t] < delta_move_pos[0,t]*(u_move_max),
                u[0,t] > (1 - delta_move_pos[0,t])*(u_move_min),                
                u[0,t] < (1-delta_move_neg[0,t])*u_move_max,
                u[0,t] > delta_move_neg[0,t]*(u_move_min),    

                # umove = only move when battery has enough charge:
                u[0,t] >= delta[0,t]*u_move_min,
                u[0,t] <= delta[0,t]*u_move_max,

                # Battery level constraint:
                x[1,t] - battery_level_no_movement <= delta[0,t]*(battery_max - battery_min),
                x[1,t] - battery_level_no_movement >= (1 - delta[0,t])*(battery_min - battery_max),
                # Distance to battery constraint:
                (x[0,t] - battery_pos) - (dist_tresh) <= (1-delta[1,t])*x_pos_max,
                (x[0,t] - battery_pos) - (dist_tresh) >= delta[1,t]*(-x_pos_max), 
                # Distance to human constraint:
                (x[0,t] - human_pos) - (dist_tresh) <= (delta[2,t])*x_pos_max,
                (x[0,t] - human_pos) - (dist_tresh) >= (1-delta[2,t])*(-x_pos_max),

                # Robot can only pick up inventory near inventory station
                u[2,t] <= delta[1,t],
                u[2,t] >= 0,
                # Robot can drop off inventory near inventory station
                u[3,t] <= delta[1,t],
                u[3,t] >= 0,

                # Robot can pick up work load from human when its near the human
                u[4,t] <= delta[2,t],
                u[4,t] >= 0,
                # Robot can drop off work only when its near the human
                u[5,t] <= delta[2,t],
                u[5,t] >= 0,        

                # Robot cannot drop off more than what he has
                x[2,t] >= 0,
                # Robot cannot pick up more than his capacity
                x[2,t] <= 1,
                #Work load of the human cannot go negative
                x[4,t] >= 0,

                # Robot should not go out of bounds
                x[0, t] <= 10,
                x[0, t] >= 0
                ]


      states.append( Problem(Minimize(cost), constr) )
  prob = sum(states)
  prob.constraints += [x[:,0] == starting_x_state]
  prob.solve( solver = ECOS_BB)

  print "x:"
  print x.value
  print "u:"
  print u.value
  print "y:"
  print y.value
  print "delta:"
  print delta.value

  return x,y,u, delta

run_mpc()
