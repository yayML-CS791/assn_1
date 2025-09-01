import json
import heapq


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
        self.transition_potentials = [[potential/self.transition_potentials_sum[i][j//self.states_count] for j, potential in enumerate(self.transition_potentials[i])] for i in range(len(self.transition_potentials))]
        self.state_factor_potentials = data['State_Factor_Potentials']
        self.state_factor_potentials_sum = [sum(self.state_factor_potentials[i:i+self.states_count]) for i in range(0, len(self.state_factor_potentials), self.states_count)]
        self.state_factor_potentials = [potential/self.state_factor_potentials_sum[i//self.states_count] for i, potential in enumerate(self.state_factor_potentials)]

        self.variables_count = self.factors_count * self.num_observations
        self.messages_from_factors_to_variables = [[1]*self.states_count for _ in range(self.factors_count * self.num_observations)]
        self.messages_from_transitions_to_variables = [[1]*self.states_count for _ in range(self.factors_count*(self.num_observations - 1))]
        self.messages_from_variables_to_factors = [[1]*self.states_count for _ in range(self.factors_count * self.num_observations)]
        self.messages_from_variables_to_transitions = [[1]*self.states_count for _ in range(self.factors_count*(self.num_observations - 1))]

        self.variable_beliefs = [[1/self.states_count]*self.states_count for _ in range(self.variables_count)]
        self.factor_beliefs = [[1]*self.states_count for _ in range(self.factor_count * self.observation_sequence)]
        self.transition_beliefs = [[1]*self.states_count for _ in range(self.factor_count * (self.num_observations - 1) * 2)]

    def compute_marginals(self):
        self.variable_beliefs = [[1/self.states_count]*self.states_count for _ in range(self.variables_count)]
        return self.variable_beliefs

    def loopy_belief_propagate_to_variable(self, prev_beliefs, prev_messages, prev_messages_from_variables, clique_members, composition_func, marginalization_func, inverse_composition_func):
        new_messages_from_factors_to_variables = [[1]*self.states_count for _ in range(self.factors_count * self.num_observations)]
        new_messages_from_transitions_to_variables = [[1]*self.states_count for _ in range(self.factors_count*(self.num_observations - 1))]
        new_messages_from_variables_to_factors = [[1]*self.states_count for _ in range(self.factors_count)]
        new_messages_from_variables_to_transitions = [[1]*self.states_count for _ in range(self.factors_count*2)]

        new_variable_beliefs = [1/self.states_count]*self.states_count
        new_factor_beliefs = [[1]*self.states_count for _ in range(self.factors_count)]
        new_transition_beliefs = [[[1]*self.states_count]*2 for _ in range(self.factors_count)]

        for i in 

    def loopy_belief_propagate_to_factor(self, prev_beliefs, factor_beliefs, prev_messages, prev_messages_from_factor, size_of_clique, composition_func, inverse_composition_func):
        raise NotImplementedError()

    def factor_in_fhmm(self, prev_beliefs, prev_messages, step_size, new_messages, composition_func, inverse_composition_func):
        raise NotImplementedError()
    
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