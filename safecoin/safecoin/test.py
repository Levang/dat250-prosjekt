# from safecoin.register import isCommonPassword
# print(isCommonPassword("sonyericsson"))

longest = ""

with open("commonPasswords.txt", "r") as f:
    for w in f:
        if len(w) > len(longest):
            longest = w

print(longest)

def getAccountNumber():
    from random import randint
    return randint(0, 100000000000000000000000000000000000**100000000000000000000000000000**1000000000000000000)

print(getAccountNumber())