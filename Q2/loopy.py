import json
import heapq
import itertools
import copy

########################################################################

# Do not install any external packages. You can only use Python's default libraries such as:
# json, math, itertools, collections, functools, random, heapq, etc.

########################################################################
def normalise(vec, K):
    total = sum(vec)
    if total > 1e-12:
        return [x / total for x in vec]
    return [1.0 / K] * K

class Inference:
    def __init__(self, data):
        self.factors_count = data['Factors_Count']
        self.states_count = data['State_Count']
        self.num_observations = data['Number of Observations']
        self.observation_sequence = data['Observation Sequence']
        self.transition_potentials = data['Transition Potentials']
        self.transition_potentials = list(self.transition_potentials.values())
        self.transition_potentials_sum = [[sum(self.transition_potentials[i][j:j+self.states_count]) for j in range(0, len(self.transition_potentials[i]), self.states_count)] for i in range(len(self.transition_potentials))]
        self.transition_potentials = [[potential/self.transition_potentials_sum[i][j // self.states_count] for j, potential in enumerate(self.transition_potentials[i])] for i in range(len(self.transition_potentials))]
        self.state_factor_potentials = data['State_Factor_Potentials']
        self.state_factor_potentials_sum = [sum(self.state_factor_potentials[i:i+self.states_count]) for i in range(0, len(self.state_factor_potentials), self.states_count)]
        self.state_factor_potentials = [potential/self.state_factor_potentials_sum[i//self.states_count] for i, potential in enumerate(self.state_factor_potentials)]
        self.variables_count = self.factors_count * self.num_observations
        self.messages_from_factors_to_variables = [[[1]*self.states_count for _ in range(self.factors_count)] for _ in range(self.num_observations)]
        self.messages_from_transitions_to_variables = [[[ [1]*self.states_count for _ in range(2) ] for _ in range(self.factors_count)] for _ in range(self.num_observations - 1)]
        self.messages_from_variables_to_factors = [[[1]*self.states_count for _ in range(self.factors_count)] for _ in range(self.num_observations)]
        self.messages_from_variables_to_transitions = [[[ [1]*self.states_count for _ in range(2) ] for _ in range(self.factors_count)] for _ in range(self.num_observations - 1)]
        
        self.state_potentials_given_observation = []

        for observation in range(self.num_observations):
            self.state_potentials_given_observation.append(self.state_factor_potentials[self.observation_sequence[observation]::self.states_count])

        self.variable_beliefs = [[1.0 / self.states_count] * self.states_count for _ in range(self.variables_count)]

        self.factor_beliefs = []
        for i_ob in range(self.num_observations):
            observation = self.observation_sequence[i_ob]
            self.factor_beliefs.append(self.state_potentials_given_observation[observation][:])

        self.transition_beliefs = []
        for i_ob in range(self.num_observations - 1):
            transition_potentials = []
            for i_fact in range(self.factors_count):
                transition_potential = self.transition_potentials[i_fact]
                transition_potentials.append(transition_potential[:])
            self.transition_beliefs.append(transition_potentials)

        # Store the previous message (Not GPTed, my own comments)
        self.previous_messages_from_variables_to_factors = copy.deepcopy(self.messages_from_variables_to_factors)
        self.previous_messages_from_factors_to_variables = copy.deepcopy(self.messages_from_factors_to_variables)
        self.previous_messages_from_variables_to_transitions = copy.deepcopy(self.messages_from_variables_to_transitions)
        self.previous_messages_from_transitions_to_variables = copy.deepcopy(self.messages_from_transitions_to_variables)

    def assignmentToIndex(self, assignment):
        return sum(a * (self.states_count ** i) for i, a in enumerate(reversed(assignment)))

    def updateFactorNodeBeliefs(self):
        for i_ob in range(self.num_observations):
            for assignment in itertools.product(range(self.states_count), repeat=self.factors_count):
                index = self.assignmentToIndex(assignment)
                for i_fact in range(self.factors_count):
                    self.factor_beliefs[i_ob][index] *= self.messages_from_variables_to_factors[i_ob][i_fact][assignment[i_fact]]
                    self.factor_beliefs[i_ob][index] /= max(1e-12, self.previous_messages_from_variables_to_factors[i_ob][i_fact][assignment[i_fact]])

            total = sum(self.factor_beliefs[i_ob])
            if total > 0:
                self.factor_beliefs[i_ob] = [val / total for val in self.factor_beliefs[i_ob]]

    def updateTransitionNodeBeliefs(self):
        
        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):

                for assignment in itertools.product(range(self.states_count), repeat=2):
                    index = self.assignmentToIndex(assignment)

                    self.transition_beliefs[i_ob][i_fact][index] *= self.messages_from_variables_to_transitions[i_ob][i_fact][0][assignment[0]]
                    self.transition_beliefs[i_ob][i_fact][index] *= self.messages_from_variables_to_transitions[i_ob][i_fact][1][assignment[1]]

                    self.transition_beliefs[i_ob][i_fact][index] /= max(1e-12, self.previous_messages_from_variables_to_transitions[i_ob][i_fact][0][assignment[0]])
                    self.transition_beliefs[i_ob][i_fact][index] /= max(1e-12, self.previous_messages_from_variables_to_transitions[i_ob][i_fact][1][assignment[1]])

                total = sum(self.transition_beliefs[i_ob][i_fact])
                if total > 0:
                    self.transition_beliefs[i_ob][i_fact] = [val / total for val in self.transition_beliefs[i_ob][i_fact]]
        
    def updateVariableBeliefs(self):
        K = self.states_count

        for i_ob in range(self.num_observations):
            for i_fact in range(self.factors_count):
                curr_var = i_ob * self.factors_count + i_fact
                # print("MESSAGE SENT: ", self.messages_from_factors_to_variables[i_ob][i_fact])
                # print("PREVIOUS MESSAGE SENT: ", self.previous_messages_from_factors_to_variables[i_ob][i_fact])
                for s in range(self.states_count):
                    
                    self.variable_beliefs[curr_var][s] *= self.messages_from_factors_to_variables[i_ob][i_fact][s]
                    self.variable_beliefs[curr_var][s] /= max(self.previous_messages_from_factors_to_variables[i_ob][i_fact][s], 1e-12)
        # print(self.variable_beliefs)
        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):
                curr_var_left = i_ob * self.factors_count + i_fact
                curr_var_right = (i_ob + 1) * self.factors_count + i_fact
                for s in range(self.states_count):
                    self.variable_beliefs[curr_var_left][s] *= self.messages_from_transitions_to_variables[i_ob][i_fact][0][s]
                    self.variable_beliefs[curr_var_right][s] *= self.messages_from_transitions_to_variables[i_ob][i_fact][1][s]
                    self.variable_beliefs[curr_var_left][s] /= max(self.previous_messages_from_transitions_to_variables[i_ob][i_fact][0][s], 1e-12)
                    self.variable_beliefs[curr_var_right][s] /= max(self.previous_messages_from_transitions_to_variables[i_ob][i_fact][1][s], 1e-12)

        for v in range(len(self.variable_beliefs)):
            total = sum(self.variable_beliefs[v])
            if total > 0:
                self.variable_beliefs[v] = [x/total for x in self.variable_beliefs[v]]
            else:
                self.variable_beliefs[v] = [1.0/self.states_count] * self.states_count

    def messageToSendFromFactor(self, factor_node_belief, i_fact, i_ob):

        message_to_send = [0] * self.states_count
        for assignment in itertools.product(range(self.states_count), repeat=self.factors_count):
            individual_val = factor_node_belief[self.assignmentToIndex(assignment)] 
            for other_vbles in range(self.factors_count):
                if (other_vbles != i_fact): 
                    individual_val *= self.messages_from_variables_to_factors[i_ob][other_vbles][assignment[other_vbles]]
            message_to_send[assignment[i_fact]] += individual_val

        return normalise(message_to_send, self.states_count)

    def messageToSendFromTransition(self, i_fact, i_ob, i_assignment):

        message_to_send = [0] * self.states_count

        for assignment in itertools.product(range(self.states_count), repeat=2):
            
            # Assuming assignment[0] is for the first variable and assignment[1] is for the second variable
            temp_val = self.transition_beliefs[i_ob][i_fact][self.assignmentToIndex(assignment)]

            if (i_assignment == 0):
                # Let 0 indicate message that came from the right and 1 came from the left to the transition node (from the perspective of the node, it would've sent the message to the left and right)
                temp_val *= self.messages_from_variables_to_transitions[i_ob][i_fact][1][assignment[1]]
            elif (i_assignment == 1):
                temp_val *= self.messages_from_variables_to_transitions[i_ob][i_fact][0][assignment[0]]
            else:
                raise ValueError("i_assignment should be either 0 or 1")
            
            message_to_send[assignment[i_assignment]] += temp_val

        return normalise(message_to_send, self.states_count)

    def sendMessagesToVariables(self):
        for i_ob in range(self.num_observations):
            factor_node_belief = self.factor_beliefs[i_ob]
            for i_fact in range(self.factors_count):
                self.messages_from_factors_to_variables[i_ob][i_fact] = self.messageToSendFromFactor(factor_node_belief, i_fact, i_ob)


        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):
                self.messages_from_transitions_to_variables[i_ob][i_fact][0] = self.messageToSendFromTransition(i_fact, i_ob, 0)
                self.messages_from_transitions_to_variables[i_ob][i_fact][1] = self.messageToSendFromTransition(i_fact, i_ob, 1)


    def sendMessagesToFactorsNodes(self):
        for i_ob in range(self.num_observations):
            for i_fact in range(self.factors_count):
                
                # Have to take the messages from the left and right transition nodes
                a = [1.0] * self.states_count
                b = [1.0] * self.states_count

                if (i_ob > 0):
                    # This node has a left transition node, but it is sending a message to the right wrt to itself
                    a = self.messages_from_transitions_to_variables[i_ob - 1][i_fact][1]
                if (i_ob < self.num_observations - 1):
                    b = self.messages_from_transitions_to_variables[i_ob][i_fact][0]

                prod = [a[i]*b[i] for i in range(self.states_count)]
                self.messages_from_variables_to_factors[i_ob][i_fact] = normalise(prod, self.states_count)

    
    def sendMessagesToTransNodes(self):
        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):
                x = [1.0] * self.states_count
                y = [1.0] * self.states_count

                a = self.messages_from_factors_to_variables[i_ob][i_fact]
                b = self.messages_from_factors_to_variables[i_ob + 1][i_fact]

                if (i_ob > 0):
                    x = self.messages_from_transitions_to_variables[i_ob - 1][i_fact][1]
                if (i_ob < self.num_observations - 2):
                    y = self.messages_from_transitions_to_variables[i_ob + 1][i_fact][0]

                K = self.states_count
                prod_left  = [a[i] * (x[i] if i_ob > 0 else 1.0) for i in range(K)]
                prod_right = [b[i] * (y[i] if i_ob < self.num_observations-2 else 1.0) for i in range(K)]

                self.messages_from_variables_to_transitions[i_ob][i_fact][0] = normalise(prod_left, K)
                self.messages_from_variables_to_transitions[i_ob][i_fact][1] = normalise(prod_right, K)


    def compute_marginals(self):

        max_iterations = 200
        tolerance = 1e-6
        for _ in range(max_iterations):
            
            old_beliefs = copy.deepcopy(self.variable_beliefs)

            # Updating factor beliefs and sending messages to variables
            self.updateFactorNodeBeliefs()
            self.updateTransitionNodeBeliefs()
            self.sendMessagesToVariables()

            self.updateVariableBeliefs()
            self.sendMessagesToFactorsNodes()
            self.sendMessagesToTransNodes()

            self.previous_messages_from_factors_to_variables = copy.deepcopy(self.messages_from_factors_to_variables)
            self.previous_messages_from_transitions_to_variables = copy.deepcopy(self.messages_from_transitions_to_variables)
            self.previous_messages_from_variables_to_factors = copy.deepcopy(self.messages_from_variables_to_factors)
            self.previous_messages_from_variables_to_transitions = copy.deepcopy(self.messages_from_variables_to_transitions)

            max_diff = 0.0
            for v in range(self.variables_count):
                for s in range(self.states_count):
                    diff = abs(self.variable_beliefs[v][s] - old_beliefs[v][s])
                    max_diff = max(max_diff, diff)
            if max_diff < tolerance:
                break

        return self.variable_beliefs

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
        for i in range(5):
            inference = Inference(self.data[i]['Input'])
            marginals = inference.compute_marginals()
            output.append({
                'Marginals': marginals,
            })
        self.output = output

    def write_output(self, file_name):
        with open(file_name, 'w') as file:
            json.dump(self.output, file, indent=4)


if __name__ == '__main__':
    evaluator = Get_Input_and_Check_Output('TestCases.json')
    evaluator.get_output()
    evaluator.write_output('Sample_Testcase_Output.json')