import string
import random

clave_secreta = ''.join(random.SystemRandom().choice(string.digits + string.ascii_letters) for _ in range(50))

print(f"Tu nueva SECRET_KEY: {clave_secreta}")

