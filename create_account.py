from algosdk import account

private_key_a, public_key_a = account.generate_account()
private_key_b, public_key_b = account.generate_account()

print(f'public key a: {public_key_a}\n')
print(f'public key b: {public_key_b}\n')

print(f'private key a: {private_key_a}\n')
print(f'private key b: {private_key_b}\n')

with open(".env", "w") as f:
    f.write(f'ADDRESS_A="{public_key_a}"\n')
    f.write(f'SECRET_A="{private_key_a}"\n')
    f.write(f'ADDRESS_B="{public_key_b}"\n')
    f.write(f'SECRET_B="{private_key_b}"\n')
    f.write('PURESTAKE_KEY=""\n')
