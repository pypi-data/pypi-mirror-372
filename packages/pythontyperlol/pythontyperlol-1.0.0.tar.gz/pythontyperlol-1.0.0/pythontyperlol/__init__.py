import os
import time

def typewriter(text, delay: float = 0.5):
    """
    Prints text like a typewriter, clearing the screen each step.

    Args:
        text (str): Text to display.
        delay (float): Delay between characters in seconds.
    """
    typed = ""
    for char in str(text):
        typed += char
        
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        print(typed)
        time.sleep(delay)
