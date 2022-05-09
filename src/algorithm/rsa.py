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
        assert self.prime_max_length > self.prime_min_length, "min length must be less than half the key length"
        self.first_sample_size = math.floor(config["KEY_GENERATION"]["FIRST_SAMPLE_SIZE"])
        self.middle_sample_size = math.floor(config["KEY_GENERATION"]["MIDDLE_SAMPLE_SIZE"])
        self.third_sample_size = math.floor(config["KEY_GENERATION"]["THIRD_SAMPLE_SIZE"])
        self.e_max_length = math.floor(config["KEY_GENERATION"]["E_MAX_LENGTH"])
        print("="*50 + "\nGenerating RSA keys for n with length of: " + str(self.key_length) + "\n" + "="*50)
    
    def generate_key(self):
        smallest_prime = 2 ** (self.prime_min_length - 1)
        p_max = (2 ** self.prime_max_length) - 1
        method = UserInputUtils.get_selection_mode("p & q")
        if method == "Randomly":
            p, q = RSAUtils.get_random_p_q(self.key_length)
        else:
            prime_candidates = RSAUtils.get_prime_candidates(self.key_length, smallest_prime, p_max, self.first_sample_size, self.middle_sample_size, self.third_sample_size)
            p, q = RSAUtils.get_p_q_from_user(self.key_length, smallest_prime, prime_candidates, self.first_sample_size, self.middle_sample_size, self.third_sample_size)
        assert(p != q)
        n = p * q
        phi = (p - 1) * (q - 1)
        print("="*50)
        method = UserInputUtils.get_selection_mode("e")
        if method == "Randomly":
            e = RSAUtils.get_random_e(self.e_max_length, phi)
        else:    
            e = RSAUtils.get_e_from_user()
        assert(math.gcd(phi, e) == 1)
        print("="*50)
        print("p: ", p, "\n")
        print("q: ", q, "\n")
        print("n: ", n, "\n")
        print("e: ", e)
        print("="*50)