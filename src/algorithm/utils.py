import inquirer
import math
import numpy as np
import random
from progressbar import *

class UserInputUtils:
    def get_prime_selection_mode(candidates, parameters):
        question = [
            inquirer.List('mode',
                        message="There are " + str(np.asarray(candidates).size) + " candidates for " + parameters + " how do you want it/them to be choosen?",
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
        middle_range_start = 2 ** (math.floor(key_length / 2) - 2)
        middle_range_end = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        middle_sample_size = min(20, (middle_range_end-middle_range_start+1))
        first_and_third_sample_size = min(5, (middle_range_start-prime_min))
        
        print(middle_range_end, prime_max)

        if(middle_range_end > prime_max):
            # important for choosing value for q as p might be large enough to rule out all random choices of q
            print(prime_max-prime_min+1)
            prime_candidates = RSAUtils.get_n_primes(prime_min, prime_max+1, min(20, (prime_max-prime_min+1)))
        else:
            first_sample = RSAUtils.get_n_primes(prime_min, middle_range_start-1, first_and_third_sample_size)
            middle_sample = RSAUtils.get_n_primes(middle_range_start, middle_range_end, middle_sample_size)
            third_sample = RSAUtils.get_n_primes(middle_range_end, prime_max, first_and_third_sample_size)
            prime_candidates = first_sample + middle_sample + third_sample

        return prime_candidates

    def get_n_primes(range_start, range_end, count):
        
        widgets = ['Generating primes: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
           ' ', ETA(), ' ', FileTransferSpeed(unit="prime")]
        pbar = ProgressBar(widgets=widgets, maxval=count)
        pbar.start()

        first_primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
            31, 37, 41, 43, 47, 53, 59, 61, 67,
            71, 73, 79, 83, 89, 97, 101, 103,
            107, 109, 113, 127, 131, 137, 139,
            149, 151, 157, 163, 167, 173, 179,
            181, 191, 193, 197, 199, 211, 223,
            227, 229, 233, 239, 241, 251, 257,
            263, 269, 271, 277, 281, 283, 293,
            307, 311, 313, 317, 331, 337, 347, 349]
        primes = set()
        for prime in reversed(first_primes_list):
            if prime > range_end or len(primes) >= count:
                break
            elif prime >= range_start:
                primes.add(prime)

        while len(primes) < count:
            prime_candidate = random.randrange(range_start, range_end+1)
            is_probable_prime = RSAUtils.is_probable_prime(range_start, first_primes_list, prime_candidate)
            if is_probable_prime and RSAUtils.is_miller_rabin_strong_prime(prime_candidate): 
                primes.add(prime_candidate)
                pbar.update(len(primes))
        pbar.finish()
        return list(primes)

    def is_probable_prime(range_start, first_primes_list, prime_candidate):
        for divisor in first_primes_list: 
            if prime_candidate % divisor == 0 and divisor**2 <= prime_candidate:
                return False
        return True


    def is_miller_rabin_strong_prime(prime_candidate):
        num_factorization_trials = 0
        factor = prime_candidate-1

        while factor % 2 == 0:
            factor >>= 1
            num_factorization_trials += 1

        num_miller_tests = 20
        for _ in range(num_miller_tests):
            base = random.randrange(2,
                        prime_candidate)
            if RSAUtils.isFactorized(prime_candidate, base, factor, num_factorization_trials):
                return False
        return True
    
    def isFactorized(prime_candidate, base, factor, num_factorization_trials):
            if pow(base, factor,
                prime_candidate) == 1:
                return False
            for i in range(num_factorization_trials):
                # check if base ^ (factor * (2^i)) = -1 mode prime_candidate
                if pow(base, 2**i * factor, prime_candidate) == prime_candidate-1:
                    return False
            return True


    def get_p_q_from_user(key_length, smallest_prime, prime_candidates):
        p =  UserInputUtils.get_value_from_user("p", prime_candidates[prime_candidates >= smallest_prime].tolist())
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        if (prime_candidates[(prime_candidates >= smallest_prime) & (prime_candidates <= q_max)].size == 0):
            print("regenerating")
            prime_candidates = RSAUtils.get_prime_candidates(key_length, smallest_prime, q_max)
        q =  UserInputUtils.get_value_from_user("q", prime_candidates[(prime_candidates >= smallest_prime) & (prime_candidates <= q_max)].tolist())
        return p,q
    
    def get_2nd_prime_max(key_length, prime_candidates, p):
        assert(isinstance(key_length, int))
        assert(isinstance(p, int))
        q_max = (2 ** (key_length - p)) - 1
        for max_candidate in prime_candidates:
            if max_candidate > q_max and (max_candidate * p) <= (2**key_length)-1:
                q_max = max_candidate
            else:
                break
        return q_max

    def get_random_p_q(key_length, smallest_prime, prime_candidates):
        p_min = 2 ** (math.ceil(key_length / 2))
        p_max = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        rand_idx=0
        while prime_candidates[rand_idx] < p_min or  prime_candidates[rand_idx] > p_max: rand_idx = int(random.random() * len(prime_candidates))
        p = prime_candidates[rand_idx]
        q_min = 2 ** (math.floor(key_length / 2) - 2)
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        q_candidates = []
        for candidate in prime_candidates:
            if (candidate >= q_min) and (candidate <= q_max):
                q_candidates.append(candidate)
        if len(q_candidates) == 0 :
            q_candidates = RSAUtils.get_prime_candidates(key_length, smallest_prime, q_max)
        rand_idx=int(random.random() * len(q_candidates))
        q = q_candidates[rand_idx]
        return p,q
    
    def get_coprime_candidates(phi):
        assert(isinstance(phi, int))
        coprimes = set()
        while len(coprimes) < 20:
            candidate = int(random.randrange(2, min(18446744073709551616, phi)))
            if RSAUtils.get_gcd(phi, candidate) == 1:
                print("candidate: ", candidate)
                coprimes.add(candidate)
        return list(coprimes)
    
    def get_gcd(n1, n2):
        n = n1 | n2
        if n == n1 or n == n2:
            return n
        
        x = n1
        y = n2
        while 1:
            r = x % y
            if r < 2:
                return 1 if r == 1 else 0
            x = y
            y = r
    
    def get_random_e(coprime_candidates):
        rand_idx = int(random.random() * len(coprime_candidates))
        choice = coprime_candidates[rand_idx]
        return choice