import numpy as np
from scipy.optimize import linear_sum_assignment
from itertools import combinations
import cvxpy as cp
from math import inf
from tqdm.autonotebook import tqdm

class Assignment():

    robot_places = np.array([1, 3, 2])
    picker_places = np.array([1, 1, 2, 2, 2, 2, 3, 4, 4, 4, 5, 8, 9, 9, 10])

    min_place = np.min(picker_places)
    max_place = np.max(picker_places)

    def __init__(self, pickers=None, robots=None):
        if robots:
            self.robot_places = np.array(robots)
        if pickers:
            self.picker_places = np.array(pickers)
        self.min_place = np.min(self.picker_places)
        self.max_place = np.max(self.picker_places)

    def state_space_size(self, n_r=3, n_p=10):
        return np.math.factorial(n_p) / np.math.factorial(n_r) / np.math.factorial(n_p - n_r)

    def search(self):
        n_robots = self.robot_places.size
        cs = list(combinations(range(self.min_place,self.max_place + 1), n_robots))
        lowest_costs = inf
        best_alloc = None
        for c in tqdm(cs):
            self.robot_places = np.array(c)
            #self.compute_cost_matrices()
            costs = self.compute_assignment(pickers=self.picker_places, robots=np.array(c))
            #print(c, costs, lowest_costs)
            if costs < lowest_costs:
                lowest_costs = costs
                best_alloc = c
        return best_alloc, lowest_costs
            #self.show_allocation()

        

    def show_allocation(self):
        rows = self.assignment[0]
        cols = self.assignment[1]
        n_robots = self.robot_places.size
        for i in range(0, len(cols)):
            if cols[i] < n_robots:
                print(f'robot {cols[i]} serves picker {rows[i]}.')
            else:
                print(f'picker {rows[i]} is currently not served')
        c = self.cost[rows, cols].sum()
        print(f'total costs: {c}')
        return c

    def compute_cost_matrices_old(self):
        # repeat the positions as columns and rows to prepare for diff
        self.robot_places_mat = np.tile(self.robot_places, (self.picker_places.size,1))
        #robot_places_mat = np.append(robot_places_mat, np.zeros((picker_places.,)), axis=1)
        self.picker_places_mat = np.tile(self.picker_places, (self.robot_places.size,1)).transpose()

        #display('robot_places_mat: ', self.robot_places_mat)
        #display('picker_places_mat: ', self.picker_places_mat)

        # calculate costs simply as 
        self.cost = np.abs(self.picker_places_mat - self.robot_places_mat)

        # add zero costs for unassigned relations (make it square)
        self.cost = np.append(self.cost, np.zeros((self.picker_places.size,self.picker_places.size - self.robot_places.size)), axis=1)
        #display('costs (rows: pickers, columns: robots): ', self.cost)

    def get_costs_assignment(self, p=picker_places, r=robot_places, urgency=None):
        # repeat the positions as columns and rows to prepare for diff
        r_mat = np.tile(r, (p.size,1))
        #robot_places_mat = np.append(robot_places_mat, np.zeros((picker_places.,)), axis=1)
        p_mat = np.tile(p, (r.size,1)).transpose()

        #display('robot_places_mat: ', r_mat)
        #display('picker_places_mat: ', p_mat)

        # calculate costs simply as 
        cost = np.abs(p_mat - r_mat)
        if urgency is not None:
            cost = cost * np.tile(urgency, (r.size,1)).transpose()

        # add zero costs for unassigned relations (make it square)
        #cost = np.append(cost, 0*np.ones((p.size, p.size - r.size)), axis=1)
        #display('costs (rows: pickers, columns: robots): ', cost)

        return cost

    def compute_assignment_old(self):
        self.assignment = linear_sum_assignment(self.cost)


    def compute_assignment(self, pickers=picker_places, robots=robot_places, urgency=None, debug=False):
        #pickers = np.array([1, 2, 3, 9, 9, 9])
        #urgency = [0.0, 0.0, 1, .1, .1, 1]
        #robots = np.array([3, 9])

        cost = self.get_costs_assignment(pickers, robots, urgency=urgency)
        #cost = np.array([[0, 1, 2, 3], [1, 0, 1, 2], [3, 2, 1, 0], [0,0,0,0]])
        allocation = cp.Variable(cost.shape, integer=False)
        #print(cost)
        b = np.ones((3,3))
        c = np.zeros((3,3))
        #b = np.array([100, 100, 100])
        # Define and solve the CVXPY problem.
        prob = cp.Problem(cp.Minimize(cp.sum(cp.diag(cost.T@allocation))),
                        [
                            cp.sum(allocation,axis=1) == 1,
                            cp.sum(allocation,axis=0) >= 1,
                            allocation >= 0
                        ]
                        )
        prob.solve(verbose=False)

        # Print result.
        res_costs = prob.value / np.sum(cost)
        if debug:
            print("\nThe optimal value is", prob.value)
            print("A solution is")
            print(np.round(allocation.value * 100))
            #print(cost.T @ allocation.value)
            print('residual costs: %f%%' % (100* res_costs))
        return res_costs
#from math import min, max
#pickers = [1,2,3,5,6,7,9,10,11,13,14,15]
#robots = [1,1,1,1]  # for `search` only the number of element matters, as values are searched for

#ac = Assignment(pickers=pickers, robots=robots)
#print('state space to be explored by search: %d' % (ac.state_space_size(len(robots), max(pickers))-min(pickers)))
##ac.get_costs_assignment()
#ac.compute_assignment()
##ac.show_allocation()
#(best, costs) = ac.search()
#print('best robot places: %s, residual costs: %.2f%%' %(best, costs*100))

