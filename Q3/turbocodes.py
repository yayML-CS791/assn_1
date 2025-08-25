import json
import random
########################################################################

# Do not modify the lines above

########################################################################

# You can add any import statements from inbuilt libraries here




########################################################################

# Do not install any more external packages. You can only use Python's default libraries such as:
# json, math, itertools, collections, functools, random, heapq, etc.

########################################################################

generator1=0o5
generator2=0o7

def generate_trellis(generator1, generator2, history_length=3):
    raise NotImplementedError()

def viterbi(noisy_output, probability_matrix):
    '''
        Feel free to add more parameters or delete existing ones. For instance, the generated trellis, etc. 
    '''
    raise NotImplementedError()

def bcjr(noisy_output, probability_matrix, app_probability):
    '''
        Feel free to add more parameters or delete existing ones. For instance, the transmission error probability matrix, any generated trellis, etc. 
        Here, app_probability refers to the a posteriori probabilities of the bits in the original data, which is estimated by other means.
        app_probability can be of shape (2, T), for instance, where T is the length of the original data.        
    '''
    raise NotImplementedError()
    
class Inference:
    def __init__(self, testcase):
        ### NOTE that you will not have access to the original bitstring in the actual evaluation
        self.noisy_output = testcase["noisy_output"]
        self.length = len(self.noisy_output)//3
        self.probability_matrix = testcase["probability_matrix"]
        self.permutation = testcase["permutation"]
        
    def get_viterbi_output(self):
        return ''.join(random.choice('01') for _ in range(self.length))

    def get_bcjr_output(self):
        return ''.join(random.choice('01') for _ in range(self.length))

    def get_turbocode_output(self):
        return ''.join(random.choice('01') for _ in range(self.length))


if __name__ == "__main__":
    with open("turbocodes_testcases.json", "r") as f:
        data = json.load(f)

    testcases = data["testcases"]

    results = []

    for i, testcase in enumerate(testcases, start=1):
        infer = Inference(testcase)

        viterbi_out = infer.get_viterbi_output()
        bcjr_out = infer.get_bcjr_output()
        turbo_out = infer.get_turbocode_output()
        results.append({
            "testcase": i,
            "viterbi_errors": len([j for j in range(len(viterbi_out)) if viterbi_out[j] != testcase["bitstring"][j]]),
            "bcjr_errors": len([j for j in range(len(bcjr_out)) if bcjr_out[j] != testcase["bitstring"][j]]),
            "turbo_errors": len([j for j in range(len(turbo_out)) if turbo_out[j] != testcase["bitstring"][j]]),
        })

    with open("turbocodes_results.json", "w") as f:
        json.dump(results, f, indent=4)