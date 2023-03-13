import random
import string


def generate_random_string(length):
    characters = string.ascii_letters + string.digits

    result = ""

    for i in range(length):
        result += random.choice(characters)

    return result
