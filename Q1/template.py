import json

########################################################################

# Do not install any external packages. You can only use Python's default libraries such as:
# json, math, itertools, collections, functools, random, heapq, etc.

########################################################################

class JunctionChain:
    def __init__(self):
        self.cliques = []

    def add_clique(self, clique):
        self.cliques.append(clique)

class Clique:
    def __init__(self, num_nodes, num_states, vars=None):
        self.num_nodes = num_nodes
        self.potential = [1,] * (num_states ** num_nodes)
        self.vars = vars
        self.num_states = num_states
        self.index_map = dict()
        for i in range(len(vars)):
            self.index_map[vars[i]] = i

    def get_potential(self, assignment):
        index = 0
        for i, val in enumerate(assignment):
            index += val * (self.num_nodes ** (len(assignment) - i - 1))
        return self.potential[index]
    
    def set_potential_from_assignment(self, assignment, value):
        index = 0
        for i, val in enumerate(assignment):
            index += val * (self.num_nodes ** (len(assignment) - i - 1))
        self.potential[index] = value

    def set_potential_from_index(self, index, value):
        self.potential[index] = value

    def set_potential(self, potential):
        self.potential = potential

    def get_index_of_var(self, var):
        return self.index_map[var]

class Message:
    def __init__(self, vars, potential):
        self.vars = vars
        self.potential = potential
        self.index_map = dict()
        for i in range(len(vars)):
            self.index_map[vars[i]] = i

    def get_potential(self, assignment):
        index = 0
        for i, val in enumerate(assignment):
            index += val * (self.num_nodes ** (len(assignment) - i - 1))
        return self.potential[index]
    
    def get_index_of_var(self, var):
        return self.index_map[var]

class Inference:
    def __init__(self, data):
        """
        Initialize the Inference class with the input data.
        
        Parameters:
        -----------
        data : dict
            The input data containing the graphical model details, such as variables, cliques, potentials, and k value.
        
        What to do here:
        ----------------
        - Parse the input data and store necessary attributes (e.g., variables, cliques, potentials, k value).
        - Initialize any data structures required for triangulation, junction tree creation, and message passing.
        
        Refer to the sample test case for the structure of the input data.
        """
        self.factors_count = data['Factors_Count']
        self.states_count = data['State_Count']
        self.num_observations = data['Number of Observations']
        self.observation_sequence = data['Observation Sequence']
        self.transition_potentials = data['Transition Potentials']
        self.transition_potentials = list(self.transition_potentials.values())
        self.transition_potentials_sum = [[sum(self.transition_potentials[i][j:j+self.states_count]) for j in range(0, len(self.transition_potentials[i]), self.states_count)] for i in range(len(self.transition_potentials))]
        self.transition_potentials = [[potential/self.transition_potentials_sum[i][j//self.states_count] for j, potential in enumerate(self.transition_potentials[i])] for i in range(len(self.transition_potentials))]
        self.state_factor_potentials = data['State_Factor_Potentials']
        self.state_factor_potentials_sum = [sum(self.state_factor_potentials[i:i+self.states_count]) for i in range(0, len(self.state_factor_potentials), self.states_count)]
        self.state_factor_potentials = [potential/self.state_factor_potentials_sum[i//self.states_count] for i, potential in enumerate(self.state_factor_potentials)]
        self.k = data['K']

        self.junction_chain = JunctionChain()

        # print('Factors count: ', self.factors_count)
        # print('States count: ', self.states_count)
        # print('Number of observations: ', self.num_observations)
        # print('Observation sequence: ', self.observation_sequence)
        # print('Transition potentials: ', self.transition_potentials)
        # print('State factor potentials: ', self.state_factor_potentials)
        # print('K: ', self.k)
        # self.triangulate_and_get_cliques()
        self.get_junction_tree()
        
        
    def triangulate_and_get_cliques(self):
        """
        Triangulate the undirected graph and extract the maximal cliques.
        
        What to do here:
        ----------------
        - Implement the triangulation algorithm to make the graph chordal.
        - Extract the maximal cliques from the triangulated graph.
        - Store the cliques for later use in junction tree creation.

        Refer to the problem statement for details on triangulation and clique extraction.
        """
        pass        

    def get_junction_tree(self):
        """
        Construct the junction tree from the maximal cliques.
        
        What to do here:
        ----------------
        - Create a junction tree using the maximal cliques obtained from the triangulated graph.
        - Ensure the junction tree satisfies the running intersection property.
        - Store the junction tree for later use in message passing.

        Refer to the problem statement for details on junction tree construction.
        """
        print('No of observations: ', self.num_observations)
        for i in range(self.num_observations):
            vars = list(range(i*self.factors_count, i*self.factors_count + self.factors_count))
            clique = Clique(self.factors_count + 1, \
                            self.states_count, \
                            vars=list(range(i*self.factors_count, i*self.factors_count + self.factors_count)) + \
                                [self.num_observations * self.factors_count + i, ])
            clique.set_potential(self.state_factor_potentials)

            if (i*self.factors_count + self.factors_count) < (self.num_observations * self.factors_count):
                for j in range(self.factors_count):
                    child_clique = Clique(self.factors_count + 1, \
                                          self.states_count, \
                                            vars=list(range(i*self.factors_count + j, i*self.factors_count + j + self.factors_count + 1)))
                    
                    mod = self.states_count ** (self.factors_count - 1)
                    for i in range(self.states_count * mod):
                        child_clique.set_potential_from_index(i, \
                                                              self.transition_potentials[j][(i // mod) * 2 + (i % 2)])


    def assign_potentials_to_cliques(self):
        """
        Assign potentials to the cliques in the junction tree.
        
        What to do here:
        ----------------
        - Map the given potentials (from the input data) to the corresponding cliques in the junction tree.
        - Ensure the potentials are correctly associated with the cliques for message passing.
        
        Refer to the sample test case for how potentials are associated with cliques.
        """
        pass

    def get_z_value(self):
        """
        Compute the partition function (Z value) of the graphical model.
        
        What to do here:
        ----------------
        - Implement the message passing algorithm to compute the partition function (Z value).
        - The Z value is the normalization constant for the probability distribution.
        
        Refer to the problem statement for details on computing the partition function.
        """
        first_message = Message([], [1,])
        for clique in self.junction_chain.cliques:
            for i in range(self.num_states ** (self.factors_count + 1)):
                pass

    def compute_marginals(self):
        """
        Compute the marginal probabilities for all variables in the graphical model.
        
        What to do here:
        ----------------
        - Use the message passing algorithm to compute the marginal probabilities for each variable.
        - Return the marginals as a list of lists, where each inner list contains the probabilities for a variable.
        
        Refer to the sample test case for the expected format of the marginals.
        """
        pass

    def compute_top_k(self):
        """
        Compute the top-k most probable assignments in the graphical model.
        
        What to do here:
        ----------------
        - Use the message passing algorithm to find the top-k assignments with the highest probabilities.
        - Return the assignments along with their probabilities in the specified format.
        
        Refer to the sample test case for the expected format of the top-k assignments.
        """
        pass



########################################################################

# Do not change anything below this line

########################################################################

class Get_Input_and_Check_Output:
    def __init__(self, file_name):
        with open(file_name, 'r') as file:
            self.data = json.load(file)
    
    def get_output(self):
        n = len(self.data)
        output = []
        for i in range(n):
            inference = Inference(self.data[i]['Input'])
            z_value = inference.get_z_value()
            marginals = inference.compute_marginals()
            top_k_assignments = inference.compute_top_k()
            output.append({
                'Marginals': marginals,
                'Top_k_assignments': top_k_assignments,
                'Z_value' : z_value
            })
        self.output = output

    def write_output(self, file_name):
        with open(file_name, 'w') as file:
            json.dump(self.output, file, indent=4)


if __name__ == '__main__':
    evaluator = Get_Input_and_Check_Output('TestCases.json')
    evaluator.get_output()
    evaluator.write_output('Sample_Testcase_Output.json')