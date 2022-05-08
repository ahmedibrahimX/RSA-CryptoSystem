import yaml
import numpy as np
import math
from algorithm.utils import RSAUtils, UserInputUtils

class RSA:
    def __init__(self):
        with open("src\configurations.yaml", "r") as f:
            config = yaml.safe_load(f)
        self.key_length = math.floor(config["KEY_GENERATION"]["KEY_LENGTH"])
        self.prime_min_length = math.floor(config["KEY_GENERATION"]["PRIME_MIN_LENGTH"])
        assert self.prime_min_length >= 2, "prime min length must be greater than or equal 2" 
        assert self.key_length > self.prime_min_length, "key length must be > prime min length" 
        self.prime_max_length = self.key_length - self.prime_min_length
        assert self.prime_max_length >= self.prime_min_length, "min length must be less than or equal to half the key length" 
    
    def generate_key(self):
        smallest_prime = 2 ** (self.prime_min_length - 1)
        p_max = (2 ** self.prime_max_length) - 1
        prime_candidates = RSAUtils.get_prime_candidates(self.key_length, smallest_prime, p_max)
        method = UserInputUtils.get_prime_selection_mode(prime_candidates, "p & q")
        if method == "Randomly":
            p, q = RSAUtils.get_random_p_q(self.key_length, prime_candidates)
        else:    
            p, q = RSAUtils.get_p_q_from_user(self.key_length, smallest_prime, prime_candidates)
        print(p, q)
        n = p * q
        phi = (p - 1) * (q - 1)
        coprime_candidates = RSAUtils.get_coprime_candidates(phi)
        method = UserInputUtils.get_prime_selection_mode(coprime_candidates, "e")
        if method == "Randomly":
            e = RSAUtils.get_random_e(coprime_candidates)
        else:    
            e = RSAUtils.get_e_from_user(coprime_candidates)
        print(p, q, n, e)
        print(RSAUtils.get_gcd(e, phi))
        assert(math.gcd(e, phi) == 1)
