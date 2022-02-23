from algosdk import account, mnemonic

private_key_a, public_key_a = account.generate_account()
private_key_b, public_key_b = account.generate_account()
mnemonic_a = mnemonic.from_private_key(private_key_a)
mnemonic_b = mnemonic.from_private_key(private_key_b)

print(f'public key a: {public_key_a}\n')
print(f'public key b: {public_key_b}\n')

print(f'private key a: {private_key_a}\n')
print(f'private key b: {private_key_b}\n')

print(f'mnemonic a: {mnemonic_a}\n')
print(f'mnemonic b: {mnemonic_b}\n')

with open('.env', 'w') as f:
    f.write(f'ADDRESS_A="{public_key_a}"\n')
    f.write(f'SECRET_A="{private_key_a}"\n')
    f.write(f'MNEMONIC_A="{mnemonic_a}"\n')
    f.write(f'ADDRESS_B="{public_key_b}"\n')
    f.write(f'SECRET_B="{private_key_b}"\n')
    f.write(f'MNEMONIC_B="{mnemonic_b}"\n')
    f.write('PURESTAKE_KEY=""\n')
    f.flush()
