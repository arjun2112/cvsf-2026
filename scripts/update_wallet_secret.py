"""
Update .env file with a properly formatted CDP_WALLET_SECRET
CDP SDK expects: base64-encoded DER format EC private key
"""
import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Generate new EC private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Get DER format (NOT PEM!)
der_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Base64 encode the DER bytes
wallet_secret = base64.b64encode(der_bytes).decode('utf-8')

print("Generated CDP_WALLET_SECRET (base64-encoded DER format):")
print(wallet_secret)
print("\n" + "="*70)

print("\nAdd this to your .env file:")
print(f"CDP_WALLET_SECRET={wallet_secret}")

# Read current .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
with open(env_path, 'r') as f:
    lines = f.readlines()

# Update or add CDP_WALLET_SECRET
updated = False
for i, line in enumerate(lines):
    if line.startswith('CDP_WALLET_SECRET='):
        lines[i] = f'CDP_WALLET_SECRET={wallet_secret}\n'
        updated = True
        break

if not updated:
    lines.append(f'CDP_WALLET_SECRET={wallet_secret}\n')

# Write back
with open(env_path, 'w') as f:
    f.writelines(lines)

print("\n.env file updated successfully!")
print("="*70)
