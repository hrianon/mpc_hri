import numpy as np

# x = [connection, awkwardness]
# u = [ u0: robot_looking_at_human,
#       u1: human_looking_at_robot,
#       u2: (u0 && (1-u1)) || (u1 && (1-u0)),
#       u3: robot_staring_at_human,
#       u4: robot_switches_gaze ]


def get_cost_params():
    x_sp = np.transpose([[80., 0.]])
    Qx = np.diag([1.,1.])

    return x_sp, Qx


def assign_matrix_coeffs():

    speed_factor = 2.

    tau = np.array([50.,50.])
    tau = tau/speed_factor

    # Define A
    A21 = 0.
    A12 = 0.
    A=np.array([[ -1./tau[0] , A21 ],
                [ A12 , -1./tau[1] ]])

    # Define B
    B00 = 1.5  # robot looking at human              -> connection
    B01 = 1.0  # human looking at robot              -> connection
    B12 = 1.0  # (u0 && (1-u1)) || (u1 && (1-u0))    -> awkwardness
    B13 = 2.0  # robot staring at human              -> awkwardness
    B14 = 0.5  # robot switches gaze                 -> awkwardness

    B=np.array([[ B00, B01,   0, -B00,   0 ],
                [ 0  ,   0, B12,  B13, B14 ]])

    B *= speed_factor

    m_z = 1./12.
    b_z = 3.

    return A, B, m_z, b_z



class DynModel:
    def __init__(self, dt):
        self.dt = dt
        self.state_dim = 2
        self.ctrl_dim = 5

        [self.A,self.B,self.m_z,self.b_z] = assign_matrix_coeffs()

        self.resetStates()

    def resetStates(self):
        self.x = np.zeros(self.state_dim)
        self.u = np.zeros(self.ctrl_dim)
        self.d = 0.
        self.z = 0.

        # Initialize values
        self.x = np.array([0. , 0.])
        u0 = 0.
        u1 = 0.
        self.update_udz(u0,u1)

    def update_udz(self, u0, u1):
        # Set based on previous timestep:
        self.u[4] = int(round(self.u[0]) != round(u0))            # evaluates to 0 for init cond
        self.d = self.u[0] * (self.d + self.dt)     # d is set based on the previous timestep's u[0]
        self.z = self.m_z * self.x[0] + self.b_z    # z is set based on the previous timestep's x[0]

        self.u[0] = round(u0)
        self.u[1] = round(u1)
        self.u[2] = int(round(u0) != round(u1))           # potential numerical rounding issue here
        self.u[3] = int(self.d >= self.z)

    def update_x(self):
        # xdot = Ax + Bu
        dx = (self.A.dot(self.x) + self.B.dot(self.u) )
        self.x = dx*self.dt + self.x
