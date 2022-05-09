import inquirer
import math
import numpy as np
import random
from progressbar import *
import timeit

class UserInterfaceUtils:
    def get_selection_mode(parameters):
        question = [
            inquirer.List('mode',
                        message="There are candidates for " + parameters + " how do you want it/them to be choosen?",
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
    
    def display_starting_message(key_length):
        print("="*50 + "\nGenerating RSA keys for n with length of: " + str(key_length) + "\n" + "="*50)
    
    def display_generated_parameters(p,q,n,e, d):
        UserInterfaceUtils.display_horizontal_line()
        print("p: ", p, "\n")
        print("q: ", q, "\n")
        print("n: ", n, "\n")
        print("e: ", e, "\n")
        print("d: ", d)
        UserInterfaceUtils.display_horizontal_line()


    def display_horizontal_line():
        print("="*50)

class RSAUtils:
    def get_random_p_q(key_length):
        start = 2 ** (math.floor(key_length / 2) - 2)
        end = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        prime_candidates = RSAUtils.get_n_primes(start, end+1, 2)
        while (len(prime_candidates) == 1 or (not((prime_candidates[0] != prime_candidates[1]) and ((prime_candidates[0]*prime_candidates[1]).bit_length() <= key_length)))):
            second_candidates = RSAUtils.get_n_primes(start, end+1, 5)
            for candidate in second_candidates:
                if((prime_candidates[0] != candidate) and ((prime_candidates[0]*candidate).bit_length() <= key_length)):
                    prime_candidates[1] = candidate
        return prime_candidates[0], prime_candidates[1]
    
    def get_n_primes(range_start, range_end, count):
        
        widgets = ['Generating primes: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
           ' ', ETA(), ' ', FileTransferSpeed(unit="prime")]
        pbar = ProgressBar(widgets=widgets, maxval=count)
        pbar.start()
        primes = set()
        for prime in RSAUtils.first_primes_list[(RSAUtils.first_primes_list >= range_start) & (RSAUtils.first_primes_list <= range_end)]:
            primes.add(int(prime))
        start = timeit.default_timer()
        while len(primes) < count:
            prime_candidate = random.randrange((range_start|1), range_end+1, 2)
            is_probably_a_prime = RSAUtils.is_probably_a_prime(range_start, prime_candidate)
            if is_probably_a_prime and RSAUtils.is_miller_rabin_strong_prime(prime_candidate): 
                primes.add(prime_candidate)
                if timeit.default_timer() - start > 5:
                    pbar.update(count)
                    break
                else:
                    pbar.update(len(primes))
        pbar.finish()
        return list(primes)

    def is_probably_a_prime(range_start, prime_candidate):
        if(RSAUtils.first_primes_list[(prime_candidate % RSAUtils.first_primes_list == 0) & (RSAUtils.first_primes_list**2 <= prime_candidate)].size > 0):
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
            if RSAUtils.is_factorized(prime_candidate, base, factor, num_factorization_trials):
                return False
        return True
    
    def is_factorized(prime_candidate, base, factor, num_factorization_trials):
            if pow(base, factor,
                prime_candidate) == 1:
                return False
            for i in range(num_factorization_trials):
                # check if base ^ (factor * (2^i)) = -1 mode prime_candidate
                if pow(base, 2**i * factor, prime_candidate) == prime_candidate-1:
                    return False
            return True

    def get_prime_candidates(key_length, prime_min, prime_max, default_first_sample_size, default_middle_sample_size, default_third_sample_size):
        middle_range_start = 2 ** (math.floor(key_length / 2) - 2)
        middle_range_end = (2 ** (math.ceil(key_length / 2) + 1)) - 1
        middle_sample_size = min(default_middle_sample_size, (middle_range_end-middle_range_start+1))
        if(middle_range_end > prime_max):
            # important for choosing value for q as p might be large enough to rule out all random choices of q
            prime_candidates = RSAUtils.get_n_primes(prime_min, prime_max+1, min(middle_sample_size, (prime_max-prime_min+1)))
        else:
            first_sample_size = min(default_first_sample_size, (middle_range_start-prime_min))
            third_sample_size = min(default_third_sample_size, (middle_range_start-prime_min))
            first_sample = RSAUtils.get_n_primes(prime_min, middle_range_start-1, first_sample_size)
            middle_sample = RSAUtils.get_n_primes(middle_range_start, middle_range_end, middle_sample_size)
            third_sample = RSAUtils.get_n_primes(middle_range_end, prime_max, third_sample_size)
            prime_candidates = first_sample + middle_sample + third_sample
        return prime_candidates

    def get_p_q_from_user(key_length, smallest_prime, prime_candidates, first_sample_size, middle_sample_size, third_sample_size):
        p =  UserInterfaceUtils.get_value_from_user("p", prime_candidates)
        q_max = RSAUtils.get_2nd_prime_max(key_length, prime_candidates, p)
        q_candidates = []
        q_candidates = np.asarray(prime_candidates, dtype=object)
        q_candidates = list(q_candidates[((q_candidates != p) & (q_candidates >= smallest_prime) & (q_candidates <= q_max))])
        assert(set(q_candidates).issubset(prime_candidates))
        if len(q_candidates) == 0 :
            print("regenerating")
            q_candidates = RSAUtils.get_prime_candidates(key_length, smallest_prime, q_max, first_sample_size, middle_sample_size, third_sample_size)
        q =  UserInterfaceUtils.get_value_from_user("q", q_candidates)
        return p,q
    
    def get_2nd_prime_max(key_length, prime_candidates, p):
        assert(isinstance(key_length, int))
        assert(isinstance(p, int))
        q_max = (2 ** (key_length - p.bit_length())) - 1
        in_list = q_max in prime_candidates
        max_output_length = key_length
        for max_candidate in prime_candidates:
            output_length = (max_candidate * p).bit_length()
            if (((max_candidate < q_max and (not in_list)) or (max_candidate > q_max)) and output_length <= max_output_length):
                q_max = max_candidate
                in_list = True
        return q_max
    
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
    
    def get_random_e(e_max_length, phi):
        return RSAUtils.get_coprime_candidates(int(e_max_length), int(phi), 1)[0]
    
    def get_coprime_candidates(e_max_length, phi, count):
        assert(isinstance(phi, int))
        widgets = ['Generating e candidates: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
           ' ', ETA(), ' ', FileTransferSpeed(unit="private key candidate")]
        pbar = ProgressBar(widgets=widgets, maxval=count)
        pbar.start()
        coprimes = set()
        range_max = (2**e_max_length)-1
        while len(coprimes) < count:
            candidate = int(random.randrange(2, min(range_max, phi)))
            if RSAUtils.get_gcd(phi, candidate) == 1:
                coprimes.add(candidate)
                pbar.update(len(coprimes))
        pbar.finish()
        return list(coprimes)
    
    def get_e_from_user(e_max_length, phi, e_options_max_count):
        candidates = RSAUtils.get_coprime_candidates(int(e_max_length), int(phi), e_options_max_count)
        return UserInterfaceUtils.get_value_from_user("e", candidates)

    def get_inverse(a, m):
        g, x, _ = RSAUtils.extended_euclidean(a, m)
        if g != 1:
           return None
        return x%m
    
    def extended_euclidean(a, b): 
        if a == 0:
            return (b, 0, 1)
        g, y, x = RSAUtils.extended_euclidean(b%a,a)
        return g, x - (b//a) * y, y

    first_primes_list = np.asarray([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
            71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179,
            181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257,263, 269, 271, 277, 281, 283, 293,
            307, 311, 313, 317, 331, 337, 347, 349])