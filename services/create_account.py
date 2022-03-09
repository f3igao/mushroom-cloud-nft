from algosdk import account, mnemonic

private_key_a, public_key_a = account.generate_account()
private_key_b, public_key_b = account.generate_account()
private_key_c, public_key_c = account.generate_account()
mnemonic_a = mnemonic.from_private_key(private_key_a)
mnemonic_b = mnemonic.from_private_key(private_key_b)
mnemonic_c = mnemonic.from_private_key(private_key_c)

print(f'creator public key: {public_key_a}\n')
print(f'buyer 1 public key: {public_key_b}\n')
print(f'buyer 2 public key: {public_key_c}\n')

print(f'creator private key: {private_key_a}\n')
print(f'buyer 1 private key: {private_key_b}\n')
print(f'buyer 2 private key: {private_key_c}\n')

print(f'creator mnemonic: {mnemonic_a}\n')
print(f'buyer 1 mnemonic: {mnemonic_b}\n')
print(f'buyer 2 mnemonic: {mnemonic_c}\n')

# TODO: remove purestake key
# PURESTAKE_KEY="iPWSaEKVTn9eEibq2s4rj8cpyQz2zzt86ofYyus2"

with open('../.env', 'w') as f:
    f.write(f'CREATOR_ADDRESS="{public_key_a}"\n')
    f.write(f'CREATOR_SECRET="{private_key_a}"\n')
    f.write(f'CREATOR_MNEMONIC="{mnemonic_a}"\n')
    f.write(f'BUYER_1_ADDRESS="{public_key_b}"\n')
    f.write(f'BUYER_1_SECRET="{private_key_b}"\n')
    f.write(f'BUYER_1_MNEMONIC="{mnemonic_b}"\n')
    f.write(f'BUYER_2_ADDRESS="{public_key_c}"\n')
    f.write(f'BUYER_2_SECRET="{private_key_c}"\n')
    f.write(f'BUYER_2_MNEMONIC="{mnemonic_c}"\n')
    f.write('PURESTAKE_KEY=""\n')
    f.flush()
