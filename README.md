# RSA Cryptographic System

> This is the project of the Computer Systems Security (CPMN426) course at Communication and Computer Engineering major, Credit-Hour System, faculty of Engineering, Cairo University.
>
> The project is focused on implementing [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) and its possible attacks

***

**Used Language:**

<img align="left" alt="Python" src="https://img.shields.io/badge/python-%2314354C.svg?style=for-the-badge&logo=python&logoColor=white"/> <br/>

***

## How to Run

> *****
>
> **DISCLAIMER:**
>
> - I run my scripts from the powershell terminal in VSCode, please use the same terminal (or you can also use the system terminal if you're on Ubuntu OS) to replicate my results as the CLI library (called "inquirer") that I used might have some glitches with other terminals
> - When entering messages in the sender terminal please don't press other buttons other than the `letters`, `numbers`, `backspace`, `shift`, `caps` and `enter` buttons because the library gives an exception if another letter is pressed. However, this doesn't affect your interactive experience since the messages are expected to be alphanumeric
>
> 

***

1. Install the required packages using the following command: `pip install -r .\requirements.txt`

2. Inside `src\scripts` directory, you have 4 scripts that you can run

   - Interactive demo:

     > A demo of the normal usage of RSA where there are 2 parties using an encrypted communication, where one party acts as the sender (sending messages encrypted with the public key "e") and the other party acts as the receiver (decrypting received messages with the private key "d")

     1. Inside `src` directory there is a `configurations.yaml` file where you can configure the key length (i.e. length of n) and the min length of the prime factors (to ensure a certain level of security). There are other configurations in this file that will change how the algorithm operates but you can leave them with the default values.

        - *Make sure that the min prime length is a value less that half the key length you specified*

     2. Inside `src\scripts` and run the command: `python .\interactive_demo.py -h` This will show you how to run the script to act as "receiver" or as a "sender". Run each one of them in a different terminal.

        - *Please run the "receiver" first as it is the party that generates the RSA key-pair and sends the public one to the "sender" to start the encrypted communication, so it uses the socket that needs to be created first so that the sender socket can connect to it*

     3. In the receiver terminal, you will be prompted by a question to choose if you want to choose `p` and `q` (RSA prime factors) manually from a list of generated valid options, or let the code generate them automatically for you in a randomized way.

        - This is how the prompt looks

          <img src=".\docs\prompt.png"/>

        - This is how the selection from the list of options looks

          <img src=".\docs\p_values.png"/>

     4. After RSA prime factors are chosen/randomly generated, the algorithm has already generated the public value `n` and is ready to choose the public value of the encryption key `e`. So you will be prompted by a question if you want to choose it manually or randomly just like what happened with `p` and `q`

     5. The receiver will share the public key values (`e` and `n`) with the sender and you can start sending messages from the sender terminal, they will be encrypted and sent to the receiver socket where they will be decrypted and displayed on the receiver terminal

        - This is how it looks like at the sender

          <img src=".\docs\sender.png"/>

        - This is how it looks like at the receiver

          <img src=".\docs\receiver.png"/>

     6. To end the communication, send an empty message from the sender terminal (just press Enter)

   - Performance statistics:
     - This script is not interactive and you don't need to do any configurations since the script tries different key lengths to show meaningful statistics for the speed of key generation and encryption.
     - You only need to run the command `python .\performance_stats.py`
     - The output will be graphs showing statistics and they will be saved in `src\stats\rsa_stats` directory

   - Chosen ciphertext attack demo:

     - This demo is not interactive so all you need to do is do the key length and min prime length in the `configurations.yaml` file just like what is explained in the interactive demo and then run the command `python .\chosen_cipher_text_attack_demo.py`

       1. Two sockets will be opened (each one opened by a different thread), one for the legitimate user "Bob", and one for the attacker "Eve" and the attack will be simulated where the attacker manages to use a chosen ciphertext attack to crack a randomly generated message sent by the legitimate user.

       2. The output in the terminal will be the original message printed from the thread simulating legitimate user behavior and the cracked message printed from the thread simulating the attacker behavior. Both messages are expected to match since this script is simulating a successful CCA attack on RSA.

          <img src=".\docs\CCA.png"/>

   - Brute force attack demo and statistics:

     - This demo is not interactive and you don't need to do any configurations since the script tries different key lengths to show meaningful statistics for the speed of bruteforce attack (factorizing `n` using bruteforce over the value of `p`).
     - You only need to run the command `python .\bruteforce_demo.py`
     - The output will be graphs showing statistics and they will be saved in `src\stats\bruteforce_stats` directory

***

## RSA Implementation

### Key Generation

- Configurable parameters (all in `src\configurations.yaml` ):

  - key length (`n`) in bits
  - min prime length in bits (lower limit for `p` and `q`)
  - `e` max length in bits
  - `e` max options count (to choose from in manual choice mode for `e` value in interactive demo)
  - first/second/third sample size (to choose from in manual choice mode for `p` and `q` prime values in interactive demo)

- Generating prime numbers

  - First trial

    - I first tried a method called [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes)
    - This method is used to generate all primes up to a certain number, it is a deterministic method but it's an O(n log(log n)) algorithm and the best complexity it can reach is O(n) with some modifications of the classical algorithm which is still not desirable for large values as in our case

  - Second trial (the currently used one)

    - I tried a randomized method inspired by Monte-Carlo. Which is to randomly choose a number of values from a certain range

    - I adapted it to be suitable for generating our `p` and `q`, so instead of just choosing a number of values from a certain range, I made sure that the chosen values are primes as follows

      - To speed up the process I stored the prime values between 2-349 so if the range I want overlaps with these values I directly add these values to my prime set to avoid unnecessary computations

      - Then I start to randomly choose values within the required range and for each value I run 2 checks before I accept it as a prime and add it to my set. The 2 checks are

        - A simple check: *make sure that this candidate is not divisible by any of the set of the primes between 2-349*

        - A Miller-Rabin check: *make sure that there is no factor (< this candidate) where the following formula holds:*

          <img src="https://latex.codecogs.com/svg.image?base^{\&space;factor\&space;*\&space;2^i}=-1\&space;mod\&space;prime\&space;candidate">

          *`i` takes values between 0 and the number of factorization trials which is determined by the number of required shifts to make the prime candidate an even number, and `base` is a random number between 2 and the prime candidate*

          * *Note that miller-rabin is also a Monte-Carlo algorithm*

    - Then I choose a value for the `p` and a value for `q` where the length their product is within the key length

  * Differences between modes
    * In random generation mode, I generate my prime candidates from the range with length around the half the max key length to ensure that `p` and `q` will be large yet will differ in length by only a few number of bits to make it difficult to bruteforce
    * In manual choice mode, I generate prime candidates from the whole range, but I sample a number of prime numbers from each range with the upper limit configured for each range in the `src\configurations.yaml` file. And I provide the user with these sampled prime candidates as a list of valid options to choose from

- `n` (public key) is calculated as the product of `p` and `q` as instructed by the RSA algorithm

- `phi` is calculated as the product of `p-1` and `q-1` as instructed by the RSA algorithm

- Choosing `e` (public key)

  - To get valid values for `e` I generate random values (modified approach inspired by Monte-Carlo) between 2 and phi (or the upper limit for `e` determined from the max length of `e` configured in the `src\configurations.yaml` file), then I run the Euclidean algorithm on each candidate value to ensure that it is coprime with `phi`
  - Difference between modes
    - In random generation mode, I generate one valid value for `e` and accept it as my public key value for `e`
    - In manual choice mode, I generate different candidates for `e` until I reach the number of choices configured by the user for `e` in the `src\configurations.yaml` file

- `d` is calculated as the inverse of `e` mod `phi`, this is calculated using the extended Euclidean algorithm

### Encrypted Communication

1. The receiver generates the key-pair and sends the public key (`e` and `n`) to the sender
2. The sender divides the message into blocks < size of key
3. The sender encrypts each block by raising the numeric value representing the plaintext block to the power of `e` mod `n`
4. The sender concatenates the encrypted block with its size and sends over socket communication
5. The receiver does the decryption by raising the numeric value representing the encrypted block to the power of `d` mod `n`
6. This operation is done until all blocks are encrypted and sent by the sender party and all are received, decrypted and put again in the original form at the receiver

### Test Cases

> My implementation allows sending any alphanumeric (not only numbers) text of any size over an RSA-encrypted socket communication

To test my implementation of RSA:

1. Run the interactive demo as instructed [above](#How-to-Run) with any key length of your choice
2. Send messages with the following criteria from the sender terminal and ensure that they are received and decrypted correctly at the receiver and the original messages are displayed at the receiver terminal
   - A message consisting of numbers only: `2352022`
   - A message consisting of letters only: `Ahmed Ibrahim`
   - A message consisting of numbers and letters but starts with a letter: `CMPN426`
   - A message consisting of numbers and letters but starts with a number: `23 of May`
   - A message consisting of a single letter: `a`
   - A message consisting of a single number: `0`
   - An empty message to close the communication successfully

***

## Bruteforce Attack

### Factorizing `n`:

- Since `n` is a product of 2 prime numbers, so according to the prime factorization theorem, `n` will not have other factors other than these 2 primes in addition to `n` itself and `1`
- So a bruteforce search for a factor of `n` (i.e. a number that divides `n`) will give me one of the prime factors, let it be `p` and thus `q` is calculated by dividing `n` by `p`

### Multiprocessing:

- Since one of the prime factors must be smaller than the root of `n` thus I will bruteforce the values within this limit
- And I improved this search by exploiting the fact that `p` and `q` are randomly chosen, thus dividing the search space into ranges and running a bruteforce process on each range in parallel will increase the probability that I will hit one of the factors of `n`
- When one process finds a factor, I set an event to kill the rest of the processes and use the found value to calculate the other factor just as mentioned above

### Deriving `d`:

- After finding both `p` and `q` , I calculate `phi`
- Then `d` is the inverse of `e` mod `phi` calculated using extended Euclidean algorithm
- `d` can be used to crack the encrypted message I have

***

## Chosen Ciphertext Attack

> I implemented a chosen ciphertext attack where the attacker can decrypt any message without learning the key regardless its size.

### Scenario

- A legitimate user "Bob" sends a message that is intercepted by an attacker "Eve"
- Eve manipulates the message by multiplying it by a random number `r` raised to the power of `e` mod `n` (these are public values that are within the access of anybody including the attacker)
- Now Eve can use this manipulated message as a chosen ciphertext and send it to Bob
- Bob decrypts the message, but from Bob's perspective the message is corrupt (the multiplication that Eve performed has changed the message and made it unintelligible), let that Bob uses a protocol that returns back corrupt messages (without encrypting it again, as it's no use to encrypt a corrupt message) to the one who sent it (to request re-transmission for example)
- Eve will calculate the inverse of `r` mod `n` using extended Euclidean algorithm and multiply the message returned from Bob with the inverse of `r` to retrieve the original message without the need of learning the key and regardless its size

### Note

* In a real situation, the encrypted messages (ciphertexts) will be sent by another user, and they get intercepted by Eve to be manipulated before it sends it to Bob. However in the scope of this project, it was declared by the TAs to be sufficient just to make Bob generate the ciphertext and send it to Eve instead of creating another socket and simulating the message interception. The focus in the project was to explore the mathematical attack and not to simulate the interception of messages on the network.

### Mathematical Reason

- The manipulation Eve has performed by multiplying the encrypted message it intercepted by a random number `r` raised to the power of `e` mod `n`, is equivalent to multiplying the original message with `r` before encryption, since both are raised to the power of `e`

  <img src="https://latex.codecogs.com/svg.image?(m^{e}\&space;mod(n))\&space;*\&space;(r^{e}\&space;mod(n))=({(m*r)}^{e}\&space;mod(n))">
  
  - That's why multiplying the decryption of the manipulated message with the inverse of `r` will give you the original message in plaintext form

***

## Statistics and Conclusions

### Performance

> The following results represent the execution time of key generation, encryption and (key generation + encryption together) averaged over 100 iterations.

- Graphs for message size that doesn't exceed one block (relative to the key size)

  <img src=".\docs\rsa_stats\different_message_sizes\key_generation_stats.png"/>

  <img src=".\docs\rsa_stats\different_message_sizes\encryption_stats.png"/>

  <img src=".\docs\rsa_stats\different_message_sizes\total_rsa_stats.png"/>

* Graphs for a constant message size that exceeds one block

  <img src=".\docs\rsa_stats\large_message\key_generation_stats.png"/>

  <img src=".\docs\rsa_stats\large_message\encryption_stats.png"/>

  <img src=".\docs\rsa_stats\large_message\total_rsa_stats.png"/>

#### Conclusion

- The increase in the time of key generation with the increase in the key size is expected to happen, however the random approaches I used in my implementation inspired by Monte-Carlo increased the average speed of Key Generation for all key sizes even large ones
  - For example generating an RSA key with a length of 1024 bit (which is considered a secure key length that would require years to be cracked) is generated in less than a second
  - Even generating an RSA key with a length of 2048 bit would be done within 2 seconds
  - This is the average case, there are at least 50% percent that you get your key in a time less than that
- Implementing my encryption in the form of blocks with the key size as the upper limit, and creating each block in an efficient way makes encrypting any message regardless its size, I tried a message size equivalent to the size of a paragraph from Wikipedia (11576 bits) and it was encrypted in a time less than hundredth of a second for key sizes up to 1024 bits and within a tenth of a second for a key size of 2048 bits
- Practically this makes the communication very fast as the third graph shown above represents both the encryption + the overhead of the key generation (which is still fast), but in practice, key generation is done once at the beginning of communication, then we communicate using this key, so practically the speed of the communication will be that of the encryption which is on average less than a tenth of a second

### Bruteforce (Searching for prime factors of `n`)

> The following results represent the execution time vs key size and vs value of `n` , averaged over 10 iterations

<img src=".\docs\bruteforce_stats\bruteforce_time_vs_keysize_stats.png"/>

<img src=".\docs\bruteforce_stats\bruteforce_time_vs_nvalue_stats.png"/>

#### Conclusion

- Bruteforce is expected to increase dramatically with the increase in the key size, however the multiprocessing approach I used increases the probability of finding one of the factors early and this speeds up the bruteforce search
  - This optimization is very clear in finding the factor of this `n` with the value of 1000961693933 (in decimal) faster than ones smaller than it, so there's a good probability that my implementation will find one of the prime factors in a relatively short time even if the n is large
- But I do *not* consider bruteforce as an effective way against RSA especially in large (realistic) key sizes.
  - For example, 56-bit key was estimated by my code to take a couple of hours to be cracked. It is a feasible to be cracked by an attacker but wouldn't be practical for my project statistics as I run the script that calculates the statistics for 10 iterations so it is not included in the graph.
  - 64-bit key was estimated by my code to take 2 days and a half to be cracked which is feasible to be cracked by an attacker, but it is not included in the graph for the same reason mentioned above
  - But larger keys such as 1024 bit and 2048 bit keys would require years to be cracked, so it is computationally infeasible to crack the key before the lifetime of the information and even if we want to speed up the process it would require renting computers with multiple cores over the cloud to crack a single RSA key which might cost more than the value of the information and still would exceed the lifetime of the information.
    - Thus we can consider RSA computationally secure against bruteforce attack

### Chosen Ciphertext Attack

* In my opinion this attack is a creative attack that uses the mathematical properties of the modular arithmetic to find a smart work-around to decrypt the message without learning the private key.
* So this attack can be considered a possible *Directed Chosen Message Attack* against RSA
* But it requires a protocol that resends the corrupt (manipulated) messages back to the attacker which I doubt that it is not prevented by practical network protocols used in reality

### General Comments

> I believe that RSA is a strong algorithm that if implemented properly it can achieve high security and performance
> Randomized algorithms and multithreading can help a lot in optimizing the execution time and speeding up the required operations to generate the keys.
> Also the computations required to encrypt and decrypt the message are not time consuming so by representing your messages in an efficient form would speed up the encryption and decryption operations a lot.

***

