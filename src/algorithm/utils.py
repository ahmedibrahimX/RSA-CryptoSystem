import inquirer
import math
import numpy as np

class UserInputUtils:
    def get_prime_selection_mode(prime_candidates):
        question = [
            inquirer.List('mode',
                        message="There are " + str(prime_candidates.size) + " prime candidates for, how do you want p & q to be choosen?",
                        choices=['Manually by you', 'Randomly'],
                    ),
        ]
        return inquirer.prompt(question)["mode"]

    def get_value_from_user(parameter, parameter_space):
        options = [
                inquirer.List("parameter",
                                message="Select an option for " + parameter + " :",
                                choices=parameter_space,
                    ),
            ]
        return inquirer.prompt(options)["parameter"]

class RSAUtils:
    def get_prime_candidates(prime_max):
        prime_candidates = np.asarray([i for i in range(2, prime_max + 1)])
        number = 2
        while (number ** 2 <= prime_max):
            prime_candidates = prime_candidates[(prime_candidates % number != 0) | (prime_candidates == number)]
            number += 1
        return np.asarray(prime_candidates)
    
    def get_p_q_from_user(key_length, smallest_prime, prime_candidates):
        p =  UserInputUtils.get_value_from_user("p", prime_candidates[prime_candidates >= smallest_prime].tolist())
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        q =  UserInputUtils.get_value_from_user("q", prime_candidates[(prime_candidates >= smallest_prime) & (prime_candidates <= q_max)].tolist())
        return p,q
    
    def get_2nd_prime_max(key_length, prime_candidates, p):
        q_max = (2 ** (key_length - p.bit_length())) - 1
        for max_candidate in prime_candidates[prime_candidates > q_max]:
            if (max_candidate * p).item().bit_length() <= key_length:
                q_max = max_candidate
            else:
                break
        return q_max

    def get_random_p_q(key_length, prime_candidates):
        p_min = 2 ** (math.floor(key_length / 2))
        p_max = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        p = np.random.choice(prime_candidates[(prime_candidates >= p_min) & (prime_candidates <= p_max)], 1, replace=False).item()
        q_min = 2 ** (math.floor(key_length / 2) - 1)
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        q = np.random.choice(prime_candidates[(prime_candidates >= q_min) & (prime_candidates <= q_max)], 1, replace=False).item()
        return p,q