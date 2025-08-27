def encode(text,key):
    result = ""
    key_len = len(key)
    for i,char in enumerate(text):
        result += chr(ord(char)^ord(key[i % key_len]))
    return result