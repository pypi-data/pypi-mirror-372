import random
import os
from onefinity import random_words


def main():
    print("Welcome to OneFinity - A number guessing game!")
    print("1. Number Guesser")
    print("2. Word Guesser")
    choice = int(input("Enter choice: "))

    if choice == 1:
        os.system('clear')
        number_guesser()
    elif choice == 2:
        os.system('clear')
        word_guesser()
    else:
        print("Incorrect option entered!")
        exit

def number_guesser():
    print("The computer will choose a number between 1 - 10")
    print("You have to guess it")

    user_guess = int(input("Enter your guess: "))
    computer_choice = random.randrange(1, 10)
    attempt = 0

    while(user_guess != computer_choice):    
        if(user_guess > computer_choice):
            attempt += 1
            print("Guessed too high!")
            user_guess = int(input("Guess again: "))
        elif(user_guess < computer_choice):
            attempt += 1
            print("Guessed too low!")
            user_guess = int(input("Guess again: "))
        else:
            break
        
    print("Congratulations, you got it right.")
    print(f"You got {(5 - attempt) * 2} points!")
    
  
def word_guesser():
    print("The computer will choose a word and give you hints.")
    print("You have to guess it.\n")
    
    print("1. Random words")
    print("2. Animals")
    print("3. Cities")
    choice = int(input("Enter: "))
    
    if choice == 1:
        chosen_word = random.choice(random_words.random_words)
    elif choice == 2:
        chosen_word = random.choice(random_words.animals)
    elif choice == 3:
        chosen_word = random.choice(random_words.cities)
    else:
        print("Invalid choice!")
        exit
    
    print(f"The word starts with {chosen_word[0]} and ends with {chosen_word[-1]}. The word also has {len(chosen_word)} letters.")
    guessed_word = input("Enter guess: ")
    
    if guessed_word == chosen_word:
        print("Right, you won!")
    else:
        print("That is not right.")
    