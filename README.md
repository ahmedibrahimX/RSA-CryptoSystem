# RSA Cryptographic System

> This is the project of the Computer Systems Security (CPMN426) course at Communication and Computer Engineering major, Credit-Hour System, faculty of Engineering, Cairo University.
>
> The project is focused on implementing [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) and its possible attacks

**Used Language:** ![Python](https://img.shields.io/badge/python-%2314354C.svg?style=for-the-badge&logo=python&logoColor=white)

***

## How to run

1. Install the required packages using the following command: `pip install -r .\requirements.txt`

2. Inside `src\scripts` directory, you have 4 scripts that you can run

   - Interactive demo:

     > A demo of the normal usage of RSA where there are 2 parties using an encrypted communication, where one party acts as the sender (sending messages encrypted with the public key "e") and the other party acts as the receiver (decrypting received messages with the private key "d")

     1. Inside `src` directory there is a `configurations.yaml` file where you can configure the key length (i.e. length of n) and the min length of the prime factors (to ensure a certain level of security). There are other configurations in this file that will change how the algorithm operates but you can leave them with the default values.

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

