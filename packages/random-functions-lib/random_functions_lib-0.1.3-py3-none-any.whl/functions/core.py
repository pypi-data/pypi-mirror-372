def encode(text,key):
    result = ""
    for i,char in enumerate(text):
        result += format(ord(char) ^ ord(key[i % len(key)]), "02x")
    return result


def decode(encoded, key):
    key_len = len(key)
    decoded = ""
    for i in range(0, len(encoded), 2):
        byte = int(encoded[i:i + 2], 16)
        decoded += chr(byte ^ ord(key[(i // 2) % key_len]))
    return decoded
