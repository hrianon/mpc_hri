import numpy as np

#---------------------------------------------------------------------------------------
# Initialize Bounds 
#---------------------------------------------------------------------------------------
# x = [Rpos, Rbattery, Rconsumables, Rproductivity, Hload]
# u = [move, charge, u_InventoryPickUp, u_InventoryDropOff, u_WorkSationPickUp, u_WorkstationDropoff]
# y = [battery, prod, workload]

init_state_dim = 5
init_control_dim = 6

delta_t = 0.1

n_u = 6
n_y = 3

def assign_Matrix_coeffs(A, B):
    tau_battery = 20.0
    tau_prod = 10.0
    tau_workload = 20.0

    beta_battery = 0.1

    gamma_move = 3.0
    gamma_charge = 0.3

    # Maximum amount robot can pick up/drop off from/to inventory station
    gamma_inv = 0.4 
    gamma_workstation = 0.4 
    
    # Productivity Change due pick up/drop off from/to workstation
    gamma_prod = 0.3

    # Human Load change due to pick up/drop off from/to workstation
    gamma_load = 0.2       

    A[1][1] = -1.0/tau_battery
    A[3][1] = beta_battery/tau_prod
    A[3][3] = -1.0/tau_prod    
    A[4][4] = -1.0/tau_workload    


    B[0][0] = gamma_move
    B[1][1] = gamma_charge
    

    B[2][2] = gamma_inv #Inventory pick up
    B[2][3] = -gamma_inv #Inventory Drop off
    B[2][4] = gamma_workstation #Workstation pickup
    B[2][5] = -gamma_workstation #Workstation dropoff             

    B[3][4] = -gamma_prod # Productivity decrease from picking up work from workstation
    B[3][5] = gamma_prod # Productivity increase from dropping off work to workstation    

    B[4][4] = -gamma_load # Workload decrease from picking up work from workstation
    B[4][5] = gamma_load # Workload increase from dropping off work to workstation    

#---------------------------------------------------------------------------------------
# End of initialization
#---------------------------------------------------------------------------------------

class DynModel:
    def __init__(self, state_dim, control_dim):
        self.A = np.zeros( (state_dim, state_dim) )
        self.B = np.zeros( (state_dim, control_dim))
        self.C = np.zeros( (n_y, state_dim) )
        self.C[0][1] = 1
        self.C[1][3] = 1
        self.C[2][4] = 1

        self.eta_k = np.zeros(state_dim)
        self.xi_k = np.zeros(control_dim)
        self.dt = delta_t
        self.state_dim = state_dim
        self.ctrl_dim = control_dim

        # Initialization values
        self.eta_k[0] = 5.0  # Robot Position
        self.eta_k[1] = 0.5#0.5  #1.0  # Robot battery
        self.eta_k[2] = 0.2  # Robot Consumables carry
        self.eta_k[3] = 0.01 # Robot Productivity 
        self.eta_k[4] = 0.90#0.01#0.6 # Human WorkLoad
            
    def compute_x_k1(self):
        # xdot = Ax + Bu            
        deta_k = (self.A.dot(self.eta_k ) + self.B.dot(self.xi_k ) )
        # x_k+1 = xdot*dt + x_k
        eta_k1 = deta_k*self.dt + self.eta_k
        # x_k, u_k = x_k+1, u_k+1
        return eta_k1

    def compute_xi_input(self, state, delta):
        # TODO
        xi_input = np.zeros(self.control_dim)
        return xi_input

    def compute_u(self, delta):
        # TODO
        u = np.zeros(n_u)
        return u
        
        
    def compute_y_k1(self):
        # y = [y2, y3, y4, y5]
        return self.C.dot(self.eta_k)

    def set_eta_k_xi_k(self, eta_in, xi_in):
        for i in range(self.state_dim):
            self.eta_k[i] = eta_in[i]

        for j in range(self.ctrl_dim):
            self.xi_k[j] = xi_in[j]
