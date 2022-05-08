# def random_based_on_sieve_of_eratosthenes(key_length, prime_min, prime_max):
    #     middle_range_start = 2 ** (math.floor(key_length / 2) - 2)
    #     middle_range_end = (2 ** (math.ceil(key_length / 2) + 1)) - 1
    #     middle_sample_size = min(1791, (middle_range_end-middle_range_start+1))
    #     first_and_third_sample_size = min(248, (middle_range_start-prime_min))

    #     if(middle_range_end > prime_max):
    #         # important for choosing value for q as p might be large enough to rule out all random choices of q
    #         first_sample = np.random.randint(prime_min, prime_max+1, (prime_max-prime_min+1), dtype=np.uint64)
    #         middle_sample = third_sample = np.asarray([], dtype=np.uint64)
    #     else:
    #         first_sample = np.random.randint(prime_min, middle_range_start, first_and_third_sample_size, dtype=np.uint64)
    #         middle_sample = np.random.randint(middle_range_start, middle_range_end+1, middle_sample_size, dtype=np.uint64)
    #         third_sample = np.random.randint(middle_range_end+1, prime_max+1, first_and_third_sample_size, dtype=np.uint64)
        
    #     prime_candidates = np.concatenate((np.array([i for i in range(2, prime_min)], dtype=np.uint64), first_sample, middle_sample, third_sample))

    #     print(prime_candidates.size)
    #     number = 2
    #     while (number ** 2 <= prime_max):
    #         if(number in prime_candidates): 
    #             prime_candidates = prime_candidates[(prime_candidates % number != 0) | (prime_candidates == number)]
    #         if(number <= prime_min): number += 1
    #         else: number = prime_candidates[np.argmax(prime_candidates > number)]
    #     return np.asarray(prime_candidates)