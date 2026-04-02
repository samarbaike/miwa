import random
import string

def generate_room_code(length=6):
    pool = string.ascii_uppercase + string.digits
    return ''.join(random.choice(pool) for _ in range(length))

