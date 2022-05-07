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
        prime_candidates = RSAUtils.get_prime_candidates(p_max)
        method = UserInputUtils.get_prime_selection_mode(prime_candidates)
        if method == "Randomly":
            p, q = RSAUtils.get_random_p_q(self.key_length, prime_candidates)          
        else:    
            p, q = RSAUtils.get_p_q_from_user(self.key_length, smallest_prime, prime_candidates)
        n = p * q
        print(p, q, n)
