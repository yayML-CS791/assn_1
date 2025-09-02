import json
import random
import uuid

def generate_fhmm_testcase(factors_count_range=(1, 5), state_count_range=(2, 5), 
                         obs_count_range=(1, 10), k_range=(2, 5)):
    """
    Generate a random FHMM test case with the specified parameter ranges.
    
    Args:
        factors_count_range (tuple): Range for number of factors (min, max)
        state_count_range (tuple): Range for number of states (min, max)
        obs_count_range (tuple): Range for number of observations (min, max)
        k_range (tuple): Range for K parameter (min, max)
    
    Returns:
        dict: A test case dictionary in the required FHMM format
    """
    # Generate random values for basic parameters
    factors_count = random.randint(*factors_count_range)
    state_count = random.randint(*state_count_range)
    obs_count = random.randint(*obs_count_range)
    k = random.randint(*k_range)
    
    # Generate observation sequence (values between 0 and state_count-1)
    obs_sequence = [random.randint(0, state_count-1) for _ in range(obs_count)]
    
    # Generate transition potentials for each factor
    transition_potentials = {}
    for factor in range(factors_count):
        # Each factor has state_count^2 potentials
        transition_potentials[str(factor)] = [
            random.randint(0, 5) for _ in range(state_count * state_count)
        ]
    
    # Generate state factor potentials
    # Size: factors_count * state_count * k
    state_factor_potentials = [
        random.randint(0, 5) 
        for _ in range(factors_count * state_count * k)
    ]
    
    # Construct the test case
    testcase = {
        "TestCaseNumber": random.randint(1, 1000),
        "Input": {
            "Factors_Count": factors_count,
            "State_Count": state_count,
            "Number of Observations": obs_count,
            "Observation Sequence": obs_sequence,
            "K": k,
            "Transition Potentials": transition_potentials,
            "State_Factor_Potentials": state_factor_potentials
        }
    }
    
    return testcase

def save_testcase(testcase, filename="fhmm_testcase.json"):
    """
    Save the test case to a JSON file.
    
    Args:
        testcase (dict): The test case to save
        filename (str): Name of the output file
    """
    with open(filename, 'w') as f:
        json.dump(testcase, f, indent=4)

# Example usage
if __name__ == "__main__":
    # Generate a test case
    testcase = generate_fhmm_testcase()
    
    # Print the test case
    print(json.dumps(testcase, indent=4))
    
    # Save to file
    save_testcase(testcase, f"fhmm_testcase_{uuid.uuid4()}.json")