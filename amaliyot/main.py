from utils import write_key, load_key, encrypt_message, decrypt_message



write_key()


key = load_key()


original_text = "Salom, bu maxfiy matn"


encrypted = encrypt_message(original_text, key)
print(f"🔐 Shifrlangan: {encrypted}")


decrypted = decrypt_message(encrypted, key)
print(f"🔓 Deshifrlangan: {decrypted}")

