import json
import heapq
import itertools

########################################################################

# Do not install any external packages. You can only use Python's default libraries such as:
# json, math, itertools, collections, functools, random, heapq, etc.

########################################################################

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
        self.messages_from_transitions_to_variables = [[[[1]*self.states_count]*2 for factor_num in range(self.factors_count)] for n in range(self.num_observations-1)]
        self.messages_from_variables_to_factors = [[[1]*self.states_count for _ in range(self.factors_count)] for _ in range(self.num_observations)]
        self.messages_from_variables_to_transitions = [[[[1]*self.states_count]*2 for factor_num in range(self.factors_count)] for n in range(self.num_observations-1)]

        self.state_potentials_given_observation = []

        for observation in range(self.num_observations):
            self.state_potentials_given_observation.append(self.state_factor_potentials[observation::self.states_count])
        
        self.factor_beliefs = []
        for i_ob in range(self.num_observations):
            observation = self.observation_sequence[i_ob]
            self.factor_beliefs.append(self.state_potentials_given_observation[observation])

        self.transition_beliefs = []
        for i_ob in range(self.num_observations-1):
            transition_potentials = []
            for i_fact in range(self.factors_count):
                transition_potential = self.transition_potentials[i_fact]
                transition_potentials.append(transition_potential)
            self.transition_beliefs.append(transition_potentials)

        # Store the previous message (Not GPTed, my own comments)
        self.previous_messages_from_variables_to_factors = self.messages_from_variables_to_factors.copy()
        self.previous_messages_from_factors_to_variables = self.messages_from_factors_to_variables.copy()
        self.previous_messages_from_variables_to_transitions = self.messages_from_variables_to_transitions.copy()
        self.previous_messages_from_transitions_to_variables = self.messages_from_transitions_to_variables.copy()

    def assignmentToIndex(self, assignment):
        return sum(a * (self.states_count ** i) for i, a in enumerate(reversed(assignment)))

    def updateFactorNodeBeliefs(self):
        for i_ob in range(self.num_observations):

            for assignment in itertools.product(range(self.states_count), repeat=self.factors_count):

                for i_fact in range(self.factors_count):
                    index = self.assignmentToIndex(assignment)
                    self.factor_beliefs[i_ob][index] *= self.messages_from_variables_to_factors[i_ob][i_fact][assignment[i_fact]]
                    self.factor_beliefs[i_ob][index] /= self.previous_messages_from_variables_to_factors[i_ob][i_fact][assignment[i_fact]]

    def updateTransitionNodeBeliefs(self):
        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):    

                # Here since the transitions can only involve two nodes, repeat has been set to 2 

                for assignment in itertools.product(range(self.states_count), repeat=2):
                    index = self.assignmentToIndex(assignment)

                    # The indicies have been hardcoded, check if this is correct
                    self.transition_beliefs[i_ob][i_fact][index] *= self.messages_from_variables_to_transitions[i_ob][i_fact][assignment[0]][assignment[1]]
                    self.transition_beliefs[i_ob][i_fact][index] /= self.previous_messages_from_variables_to_transitions[i_ob][i_fact][assignment[0]][assignment[1]]

    def messageToSendFromFactor(self, factor_node_belief, i_fact, i_ob):
        message_to_send = [1, 1]
        for assignment in itertools.product(range(self.states_count), repeat=self.factors_count):
            message_to_send[assignment[i_fact]] *= factor_node_belief[i_ob][self.assignmentToIndex(assignment)] 
            for other_vbles in range(self.factors_count):
                if (other_vbles != i_fact): 
                    message_to_send[assignment[i_fact]] *= self.messages_from_variables_to_factors[i_ob][other_vbles][assignment[other_vbles]]

        return message_to_send
    
    def messageToSendFromTransition(self, i_fact, i_ob, i_assignment):
        message_to_send = [1, 1]
        for assignment in itertools.product(range(self.states_count), repeat=2):
            # assuming assignment[0] is for the first variable and assignment[1] is for the second variable
            message_to_send[assignment[i_assignment]] *= self.transition_beliefs[i_ob][i_fact][self.assignmentToIndex(assignment)]

            if (i_assignment == 0):
                # Let 0 indicate message that came from the right and 1 came from the left to the transition node (from the perspective of the node, it would've sent the message to the left and right)
                message_to_send[assignment[0]] *= self.messages_from_variables_to_transitions[i_ob + 1][i_fact][0][assignment[1]]
            elif (i_assignment == 1):
                message_to_send[assignment[1]] *= self.messages_from_variables_to_transitions[i_ob - 1][i_fact][1][assignment[0]]
            else:
                raise ValueError("i_assignment should be either 0 or 1")
        return message_to_send
    
    def sendMessagesToVariables(self):
        for i_ob in range(self.num_observations):
            factor_node_belief = self.factor_beliefs[i_ob]
            for i_fact in range(self.factors_count):
                curr_var = i_ob * self.factors_count + i_fact
                self.messages_from_factors_to_variables[curr_var] = self.messageToSendFromFactor(factor_node_belief, i_fact, i_ob)


        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):
                self.messages_from_transitions_to_variables[i_ob][i_fact][0] = self.messageToSendFromTransition(i_fact, i_ob, 0)
                self.messages_from_transitions_to_variables[i_ob + 1][i_fact][1] = self.messageToSendFromTransition(i_fact, i_ob + 1, 1)


    def updateVariableBeliefs(self):
        for i_ob in range(self.num_observations):
            for i_fact in range(self.factors_count):
                curr_var = i_ob * self.factors_count + i_fact

                self.variable_beliefs[curr_var] *= self.messages_from_factors_to_variables[curr_var]
                self.variable_beliefs[curr_var] /= self.previous_messages_from_factors_to_variables[curr_var]
                self.variable_beliefs[curr_var] = self.messages_from_transitions_to_variables[curr_var]
                self.variable_beliefs[curr_var] /= self.previous_messages_from_transitions_to_variables[curr_var]

        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):
                curr_var_left = i_ob * self.factors_count + i_fact
                curr_var_right = (i_ob + 1) * self.factors_count + i_fact
                self.variable_beliefs[curr_var_left] *= self.messages_from_transitions_to_variables[i_ob][i_fact][0]
                self.variable_beliefs[curr_var_right] *= self.messages_from_transitions_to_variables[i_ob + 1][i_fact][1]
                self.variable_beliefs[curr_var_left] /= self.previous_messages_from_transitions_to_variables[i_ob][i_fact][0]
                self.variable_beliefs[curr_var_right] /= self.previous_messages_from_transitions_to_variables[i_ob + 1][i_fact][1]
        

    def sendMessagesToFactorsNodes(self):
        for i_ob in range(self.num_observations):
            for i_fact in range(self.factors_count):
                curr_var = i_ob * self.factors_count + i_fact
                # self.messages_from_variables_to_factors[i_ob][i_fact] = self.variable_beliefs[curr_var]
                self.messages_from_variables_to_factors[i_ob][i_fact] = self.messages_from_factors_to_variables[curr_var]

    # check this once
    def sendMessagesToTransNodes(self):
        for i_ob in range(self.num_observations - 1):
            for i_fact in range(self.factors_count):
                self.messages_from_variables_to_transitions[i_ob][i_fact][0] = self.messages_from_transitions_to_variables[i_ob][i_fact][0]
                self.messages_from_variables_to_transitions[i_ob + 1][i_fact][1] = self.messages_from_transitions_to_variables[i_ob + 1][i_fact][1]

    def compute_marginals(self):
        self.variable_beliefs = [[1/self.states_count]*self.states_count for _ in range(self.variables_count)]

        max_iterations = 10
        for _ in range(max_iterations):

            # Updating factor beliefs and sending messages to variables
            self.updateFactorNodeBeliefs()
            self.updateTransitionNodeBeliefs()
            self.sendMessagesToVariables()
            self.previous_messages_from_factors_to_variables = self.messages_from_factors_to_variables.copy()

            self.updateVariableBeliefs()
            self.sendMessagesToFactorsNodes()
            self.sendMessagesToTransNodes()
            self.previous_messages_from_variables_to_factors = self.messages_from_variables_to_factors.copy()

            # Updating variable beliefs and sending messages to factors
        return self.variable_beliefs

    def loopy_belief_propagate_to_variable(self, prev_beliefs, prev_messages, prev_messages_from_variables, clique_members, composition_func, marginalization_func, inverse_composition_func):
        pass

    def loopy_belief_propagate_to_factor(self, prev_beliefs, factor_beliefs, prev_messages, prev_messages_from_factor, size_of_clique, composition_func, inverse_composition_func):
        pass

    def factor_in_fhmm(self, prev_beliefs, prev_messages, step_size, new_messages, composition_func, inverse_composition_func):
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
        for i in range(3, 5):
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