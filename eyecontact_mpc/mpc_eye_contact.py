from cvxpy import *
import gurobipy
import eye_contact_dynamics as dyn
import numpy as np


####################
###   Constants  ###
####################
P = 8
[A, B, m_z, b_z] = dyn.assign_matrix_coeffs()

# Cost function parameters
[x_sp, Qx] = dyn.get_cost_params()


# Min and max of state variables
x_min = np.transpose([[   0.,    0.]])
x_max = np.transpose([[ 100.,  100.]])
d_min = 0.
d_max = 20.*P
z_min = 0
z_max = 2.*(x_max * m_z + b_z)




####################
### Optimization ###
####################
x = Variable(2,P)
u = Bool(5,P)
d = Variable(P)
z = Variable(P)
aux = Bool(2,P)


def run_mpc(dt, x_init, d_init, z_init, u1_init, u4_init):
    states = []
    for p in range(P-1):
    	constraints =[
    		# State equation constraint
    		x[:,p+1] == x[:,p] + dt*(A*x[:,p] + B*u[:,p])                 ,

            # Set awkward duration time:
            # z = m_z * x[0] + b_z
            z[p+1] == m_z * x[0,p] + b_z                                  ,

    		# Set duration, d:
    		# d[p+1]=u[0,p]*(d[p]+dt)
    		d[p+1] >= u[0,p] * d_min							          ,
    		d[p+1] <= u[0,p] * d_max						              ,
    		(d[p]+dt)-d[p+1] <= (1.-u[0,p])*(d_max-d_min)			      ,
    		(d[p]+dt)-d[p+1] >= (1.-u[0,p])*(d_min-d_max)			      ,

    		# Set u[2]:
            # (u0 && (1-u1)) || (u1 && (1-u0))
    		u[2,p+1] == u[0,p+1]*(1.-u1_init) + (1.-u[0,p+1])*u1_init	  ,

            # Set u[3], staring state:
    		# u[3,p] == 1  iff  d >= z
    		d[p+1] - z[p+1] <=       u[3,p+1] *(d_max - z_min)		      ,
    		d[p+1] - z[p+1] >= (1. - u[3,p+1])*(d_min - z_max)	   	      ,

    		# Set u[4], switching state:
            u[4,p+1] == aux[0,p+1] + aux[1,p+1]     ,

            # Set aux[0]
            aux[0,p+1] <= u[0,p+1]                  ,
            aux[0,p+1] <= 1.-u[0,p]                 ,
            aux[0,p+1] >= u[0,p+1] - u[0,p]         ,

            # Set aux[1]
            aux[1,p+1] <= u[0,p]                    ,
            aux[1,p+1] <= 1.-u[0,p+1]               ,
            aux[1,p+1] >= u[0,p] - u[0,p+1]

    		# Min and max x values
    		# x_min <= x[:,p+1],	x[:,p+1] <= x_max
    	]

    	cost = quad_form(x[:,p+1]-x_sp,Qx)
    	states.append(Problem(Minimize(cost),constraints))
    prob = sum(states)
    prob.constraints += [
            # Variables dependent on prev step:
            x[:,0] == x_init                ,
            d[0]   == d_init                ,
            z[0]   == z_init                ,
            u[1,:] == np.full((1,P),u1_init)    ,  # pot dim issue
            u[4,0] == u4_init               ,

            # Set u[2] @ p=0:
            # (u0 && (1-u1)) || (u1 && (1-u0))
            u[2,0] == u[0,0]*(1.-u1_init) + (1.-u[0,0])*u1_init	    ,

            # Set u[3], staring state:
            # u[3,p] == 1  iff  d >= z
            d[0] - z[0] <=       u[3,0] *(d_max - z_min)            ,
            d[0] - z[0] >= (1. - u[3,0])*(d_min - z_max)            ,

            # aux variables @ time p=0 are not used:
            aux[0,0] == 0. , aux[1,0] == 0.

            # When u4 not used:
            # u[4,:] == np.zeros((1,P))
  		]


    prob.solve(verbose=False, solver=GUROBI)

    print prob.status

    # print "x:"
    # print x.value
    # print "u:"
    # print u.value
    # print "d:"
    # print d.value
    # print "z:"
    # print z.value

    return x,u,d,z

# run_mpc()
