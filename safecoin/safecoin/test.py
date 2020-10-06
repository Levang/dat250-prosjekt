# from safecoin.register import isCommonPassword
# print(isCommonPassword("sonyericsson"))

longest = ""

with open("commonPasswords.txt", "r") as f:
    for w in f:
        if len(w) > len(longest):
            longest = w

print(longest)
