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
        self.transition_potentials = [[potential/self.transition_potentials_sum[i][j//self.states_count] for j, potential in enumerate(self.transition_potentials[i])] for i in range(len(self.transition_potentials))]
        self.state_factor_potentials = data['State_Factor_Potentials']
        self.state_factor_potentials_sum = [sum(self.state_factor_potentials[i:i+self.states_count]) for i in range(0, len(self.state_factor_potentials), self.states_count)]
        self.state_factor_potentials = [potential/self.state_factor_potentials_sum[i//self.states_count] for i, potential in enumerate(self.state_factor_potentials)]
        self.index_lookup = {}
        index = 0
        for assignment in itertools.product(range(self.states_count), repeat=self.factors_count):
            self.index_lookup[assignment] = index
            index += 1
        self.variables_count = self.factors_count * self.num_observations
        self.messages_from_factors_to_variables = [[[1]*self.states_count for _ in range(self.factors_count)] for _ in range(self.num_observations)]
        self.messages_from_transitions_to_variables = [[[[1]*self.states_count]*2 for factor_num in range(self.factors_count)] for n in range(self.num_observations-1)]
        self.messages_from_variables_to_factors = [[[1]*self.states_count for _ in range(self.factors_count)] for _ in range(self.num_observations)]
        self.messages_from_variables_to_transitions = [[[[1]*self.states_count]*2 for factor_num in range(self.factors_count)] for n in range(self.num_observations-1)]
        
    def compute_marginals(self):

        num_assignments = self.states_count ** self.factors_count
        self.alpha_messages = [[0.0 for _ in range(num_assignments)]
                            for _ in range(self.num_observations)]
        self.lambda_messages = [[1.0 for _ in range(num_assignments)]
                                for _ in range(self.num_observations)]


        observation = self.observation_sequence[0]
        for assignment in self.index_lookup.keys():
            idx = self.index_lookup[assignment]
            obs_prob = self.state_factor_potentials[idx * self.states_count + observation]
            self.alpha_messages[0][idx] = obs_prob

        total = sum(self.alpha_messages[0])
        if total > 0:
            self.alpha_messages[0] = [x / total for x in self.alpha_messages[0]]

        for obs_no in range(1, self.num_observations):
            observation = self.observation_sequence[obs_no]
            for assignment in self.index_lookup.keys():
                idx = self.index_lookup[assignment]

                sum_prev = 0.0
                for prev_assignment in self.index_lookup.keys():
                    prev_idx = self.index_lookup[prev_assignment]
                    trans_prob = 1.0

                    for f in range(self.factors_count):
                        trans_prob *= self.transition_potentials[f][
                            prev_assignment[f]*self.states_count + assignment[f]
                        ]
                    sum_prev += self.alpha_messages[obs_no-1][prev_idx] * trans_prob

                obs_prob = self.state_factor_potentials[idx * self.states_count + observation]
                self.alpha_messages[obs_no][idx] = sum_prev * obs_prob

            total = sum(self.alpha_messages[obs_no])
            if total > 0:
                self.alpha_messages[obs_no] = [x / total for x in self.alpha_messages[obs_no]]

        for obs_no in reversed(range(self.num_observations-1)):
            for assignment in self.index_lookup.keys():
                idx = self.index_lookup[assignment]
                total = 0.0
                for next_assignment in self.index_lookup.keys():
                    next_idx = self.index_lookup[next_assignment]
                    trans_prob = 1.0
                    for f in range(self.factors_count):
                        trans_prob *= self.transition_potentials[f][
                            assignment[f]*self.states_count + next_assignment[f]
                        ]
                    obs_prob = self.state_factor_potentials[
                        next_idx * self.states_count + self.observation_sequence[obs_no+1]
                    ]
                    total += trans_prob * obs_prob * self.lambda_messages[obs_no+1][next_idx]
                self.lambda_messages[obs_no][idx] = total

            norm = sum(self.lambda_messages[obs_no])
            if norm > 0:
                self.lambda_messages[obs_no] = [x / norm for x in self.lambda_messages[obs_no]]

        self.variable_beliefs = [[[0.0 for _ in range(self.states_count)]
                                for _ in range(self.factors_count)]
                                for _ in range(self.num_observations)]

        for obs_no in range(self.num_observations):

            joint_post = [self.alpha_messages[obs_no][i] *
                        self.lambda_messages[obs_no][i]
                        for i in range(num_assignments)]
            norm = sum(joint_post)
            if norm > 0:
                joint_post = [x / norm for x in joint_post]

            for f in range(self.factors_count):
                for state in range(self.states_count):
                    prob = 0.0
                    for assignment in self.index_lookup.keys():
                        if assignment[f] == state:
                            prob += joint_post[self.index_lookup[assignment]]
                    self.variable_beliefs[obs_no][f][state] = prob

        return self.variable_beliefs

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
        for i in range(n):
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