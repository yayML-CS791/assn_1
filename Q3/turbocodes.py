import json
import random
########################################################################

# Do not modify the lines above

########################################################################

# You can add any import statements from inbuilt libraries here
from math import log, exp

########################################################################

# Do not install any more external packages. You can only use Python's default libraries such as:
# json, math, itertools, collections, functools, random, heapq, etc.

########################################################################

def normalize(array):
    total = sum(array)
    return [x / total for x in array] if total > 0 else array

generator1=0o5
generator2=0o7

def generate_trellis(generator1, generator2, history_length=3):
    binary_generator_feedforward = [int(b) for b in bin(generator1)[2:][::-1].zfill(history_length)] 
    binary_generator_feedback = [int(b) for b in bin(generator2)[2:][::-1].zfill(history_length)]

    total_states = 2 ** (history_length - 1)
    trellis = [[None for _ in range(2)] for _ in range(total_states)]

    for state in range(total_states):
        current = [int(b) for b in bin(state)[2:].zfill(history_length - 1)]
        for input in range(2):
            history = current.copy()
            history.append(input)
            feedback_val=sum(bit * g for bit, g in zip(history, binary_generator_feedback)) % 2
            history.pop()
            history.append(feedback_val)
            parity = sum(bit * g for bit, g in zip(history, binary_generator_feedforward)) % 2
            next_state = int("".join(str(b) for b in history[1:]), 2)
            trellis[state][input] = (next_state, parity)
    return trellis

def viterbi(noisy_output, probability_matrix, trellis):
    steps = len(noisy_output) // 3
    states = len(trellis)

    dp = [[float("inf")] * states for _ in range(steps + 1)]
    backpointer = [[None] * states for _ in range(steps + 1)]
    dp[0][0] = 0.0

    for step in range(steps):
        systematic = noisy_output[step * 3]
        parity1 = noisy_output[step * 3 + 1]

        for state in range(states):
            if dp[step][state] == float("inf"):
                continue

            for input in range(2):
                next_state, parity = trellis[state][input]
                ll_sys = -log(probability_matrix[input][systematic])
                ll_par = -log(probability_matrix[parity][parity1])
                transition_cost = ll_sys + ll_par

                new_cost = dp[step][state] + transition_cost
                if dp[step + 1][next_state] > new_cost:
                    dp[step + 1][next_state] = new_cost
                    backpointer[step + 1][next_state] = (state, input)

    final_state = min(range(states), key=lambda s: dp[steps][s])
    decoded_bits = []

    state = final_state
    for t in range(steps, 0, -1):
        prev_state, input = backpointer[t][state]
        decoded_bits.append(str(input))
        state = prev_state

    decoded_bits.reverse()
    return decoded_bits

def bcjr(noisy_output, probability_matrix, app_probability, trellis):
    eps = 1e-12
    steps = len(noisy_output) // 2
    states = len(trellis)

    alpha = [[0.0 for _ in range(states)] for _ in range(steps + 1)]
    beta = [[0.0 for _ in range(states)] for _ in range(steps + 1)]
    gamma = [[[0.0 for _ in range(2)] for _ in range(states)] for _ in range(steps + 1)]

    for step in range(steps):
        systematic = noisy_output[2 * step]
        parity1 = noisy_output[2 * step + 1]

        for state in range(states):
            for inp in range(2):
                next_state, parity = trellis[state][inp]
                p_sys = probability_matrix[inp][systematic]
                p_par = probability_matrix[parity][parity1]
                prior = app_probability[inp][step]
                gamma[step][state][inp] = max(p_sys * p_par * prior, eps)

    alpha[0][0] = 1.0
    for step in range(steps):
        for state in range(states):
            if alpha[step][state] == 0.0:
                continue
            for inp in range(2):
                next_state, _ = trellis[state][inp]
                alpha[step + 1][next_state] += alpha[step][state] * gamma[step][state][inp]

        norm = sum(alpha[step + 1])
        if norm < eps:
            norm = eps
        alpha[step + 1] = [x / norm for x in alpha[step + 1]]

    for state in range(states):
        beta[steps][state] = 1.0
    for step in range(steps - 1, -1, -1):
        for state in range(states):
            total = 0.0
            for input in range(2):
                next_state, _ = trellis[state][input]
                total += gamma[step][state][input] * beta[step + 1][next_state]
            beta[step][state] = total

        norm = sum(beta[step])
        if norm < eps:
            norm = eps
        beta[step] = [x / norm for x in beta[step]]

    LLR = []
    for step in range(steps):
        p0, p1 = eps, eps
        for state in range(states):
            for inp in range(2):
                next_state, _ = trellis[state][inp]
                prob = alpha[step][state] * gamma[step][state][inp] * beta[step + 1][next_state]
                if inp == 0:
                    p0 += prob
                else:
                    p1 += prob
        LLR.append(log(p1) - log(p0))

    return LLR
    
class Inference:
    def __init__(self, testcase):
        ### NOTE that you will not have access to the original bitstring in the actual evaluation
        self.noisy_output = testcase["noisy_output"]
        self.length = len(self.noisy_output)//3
        self.probability_matrix = testcase["probability_matrix"]
        self.probability_matrix = [normalize(self.probability_matrix), normalize(self.probability_matrix)[::-1]]
        self.permutation = testcase["permutation"]
        self.inv_perm = [0] * self.length
        for i, p in enumerate(self.permutation):
            self.inv_perm[p] = i

        sys_noisy = self.noisy_output[::3]
        sys_perm = [sys_noisy[i] for i in self.permutation]
        parity1_noisy = self.noisy_output[1::3]
        parity2_noisy = self.noisy_output[2::3]

        self.noisy_seq1 = [val for pair in zip(sys_noisy, parity1_noisy) for val in pair]
        self.noisy_seq2 = [val for pair in zip(sys_perm, parity2_noisy) for val in pair]
        self.trellis = generate_trellis(generator1, generator2, history_length=3)
        
    def get_viterbi_output(self):
        return viterbi(self.noisy_output, self.probability_matrix, self.trellis)

    def get_bcjr_output(self):
        app_probability = [[0.5 for _ in range(self.length)] for _ in range(2)]
        LLR = bcjr(self.noisy_seq1, self.probability_matrix, app_probability, self.trellis)
        decoded = ['1' if LLR[i] > 0 else '0' for i in range(len(LLR))]
        return decoded

    def get_turbocode_output(self, eps=1e-12, delta_thres=1e-2):
        eps = 1e-12
        steps = self.length
        app_probability1 = [[0.5 for _ in range(steps)] for _ in range(2)]
        app_probability2 = [[0.5 for _ in range(steps)] for _ in range(2)]
        prev_llr = [0 for _ in range(steps)]
        
        min_iterations = 3
        max_iterations = 10

        for iter in range(max_iterations):
            LLR1 = bcjr(self.noisy_seq1, self.probability_matrix, app_probability1, self.trellis)
            delta = max(abs(LLR1[i] - prev_llr[i]) for i in range(steps))
            prev_llr = LLR1.copy()
            prior_llr1 = []
            for i in range(steps):
                p0 = max(app_probability1[0][i], eps)
                p1 = max(app_probability1[1][i], eps)
                prior_llr1.append(log(p1) - log(p0))
            extrinsic1 = [LLR1[i] - prior_llr1[i] for i in range(steps)]
            interleaved_prior = [extrinsic1[i] for i in self.permutation]
            for i, llr in enumerate(interleaved_prior):
                if llr > 50:
                    p1 = 1.0
                elif llr < -50:
                    p1 = 0.0
                else:
                    p1 = 1.0 / (1.0 + exp(-llr))
                p0 = 1.0 - p1
                app_probability2[0][i] = max(p0, eps)
                app_probability2[1][i] = max(p1, eps)

            LLR2 = bcjr(self.noisy_seq2, self.probability_matrix, app_probability2, self.trellis)
            prior_llr2 = []
            for i in range(steps):
                p0 = max(app_probability2[0][i], eps)
                p1 = max(app_probability2[1][i], eps)
                prior_llr2.append(log(p1) - log(p0))
            extrinsic2 = [LLR2[i] - prior_llr2[i] for i in range(steps)]
            deinterleaved_prior = [extrinsic2[i] for i in self.inv_perm]
            for i, llr in enumerate(deinterleaved_prior):
                if llr > 50:
                    p1 = 1.0
                elif llr < -50:
                    p1 = 0.0
                else:
                    p1 = 1.0 / (1.0 + exp(-llr))
                p0 = 1.0 - p1
                app_probability1[0][i] = max(p0, eps)
                app_probability1[1][i] = max(p1, eps)

            if delta < delta_thres and iter >= min_iterations:
                break

        LLR = bcjr(self.noisy_seq1, self.probability_matrix, app_probability1, self.trellis)
        decoded = ['1' if llr > 0 else '0' for llr in LLR]
        return decoded

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