import inquirer
import math
import numpy as np
import random

class UserInputUtils:
    def get_prime_selection_mode(candidates, parameters):
        question = [
            inquirer.List('mode',
                        message="There are " + str(candidates.size) + " candidates for " + parameters + " how do you want it/them to be choosen?",
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
    def get_prime_candidates(key_length, prime_min, prime_max):
        return RSAUtils.random_based_on_sieve_of_eratosthenes(key_length, prime_min, prime_max)

    def random_based_on_sieve_of_eratosthenes(key_length, prime_min, prime_max):
        middle_range_start = 2 ** (math.floor(key_length / 2) - 2)
        middle_range_end = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        middle_sample_size = min(1791, (middle_range_end-middle_range_start+1))
        first_and_third_sample_size = min(248, (middle_range_start-prime_min))

        if(middle_range_end > prime_max):
            # important for choosing value for q as p might be large enough to rule out all random choices of q
            first_sample = np.random.randint(prime_min, prime_max+1, (prime_max-prime_min+1), dtype=np.uint64)
            middle_sample = third_sample = np.asarray([], dtype=np.uint64)
        else:
            first_sample = np.random.randint(prime_min, middle_range_start, first_and_third_sample_size, dtype=np.uint64)
            middle_sample = np.random.randint(middle_range_start, middle_range_end+1, middle_sample_size, dtype=np.uint64)
            third_sample = np.random.randint(middle_range_end+1, prime_max+1, first_and_third_sample_size, dtype=np.uint64)
        
        prime_candidates = np.concatenate((np.array([i for i in range(2, prime_min)], dtype=np.uint64), first_sample, middle_sample, third_sample))

        print(prime_candidates.size)
        number = 2
        while (number ** 2 <= prime_max):
            if(number in prime_candidates): 
                prime_candidates = prime_candidates[(prime_candidates % number != 0) | (prime_candidates == number)]
            if(number <= prime_min): number += 1
            else: number = prime_candidates[np.argmax(prime_candidates > number)]
        return np.asarray(prime_candidates)


    def get_p_q_from_user(key_length, smallest_prime, prime_candidates):
        p =  UserInputUtils.get_value_from_user("p", prime_candidates[prime_candidates >= smallest_prime].tolist())
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        if (prime_candidates[(prime_candidates >= smallest_prime) & (prime_candidates <= q_max)].size == 0):
            print("regenerating")
            prime_candidates = RSAUtils.get_prime_candidates(key_length, smallest_prime, q_max)
        q =  UserInputUtils.get_value_from_user("q", prime_candidates[(prime_candidates >= smallest_prime) & (prime_candidates <= q_max)].tolist())
        return p,q
    
    def get_2nd_prime_max(key_length, prime_candidates, p):
        q_max = (2 ** (key_length - p.bit_length())) - 1
        for max_candidate in prime_candidates[prime_candidates > q_max]:
            if (max_candidate.item() * p).bit_length() <= key_length:
                q_max = max_candidate
            else:
                break
        return q_max

    def get_random_p_q(key_length, prime_candidates):
        p_min = 2 ** (math.ceil(key_length / 2))
        p_max = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        p = np.random.choice(prime_candidates[(prime_candidates >= p_min) & (prime_candidates <= p_max)], 1, replace=False).item()
        q_min = 2 ** (math.floor(key_length / 2) - 2)
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        q = np.random.choice(prime_candidates[(prime_candidates >= q_min) & (prime_candidates <= q_max)], 1, replace=False).item()
        return p,q
    
    def get_coprime_candidates(phi):
        coprime_candidates = np.random.randint(2, min(18446744073709551616, phi), 50, dtype=np.uint64)
        print(coprime_candidates)
        coprimes = []
        for candidate in coprime_candidates:
            if RSAUtils.get_gcd(candidate, phi) == 1:
                coprimes.append(candidate)
        return np.asarray(coprimes)
    
    def get_gcd(n1, n2):
        n = n1 | n2
        if n == n1 or n == n2:
            return n
        
        x = n1 if n1 > n2 else n2
        y = n1 if x == n2 else n2
        while 1:
            r = x % y
            if r < 2:
                return 1 if r == 1 else 0
            x = y
            y = r
    
    def get_random_e(coprime_candidates):
        return np.random.choice(coprime_candidates, 1, replace=False).item()