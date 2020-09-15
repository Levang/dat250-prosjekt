def saveInDatabase():
    pass


def getPasswordViolations(errList, password):
    if type(password) != str:
        return "An error occured!"

    # Password params
    want_length = 8
    want_numbers = 3

    if len(password) < want_length:
        errList.append(f"Password should be at least {want_length} characters")

    numbers = 0
    for letter in password:
        try:
            int(letter)
            numbers += 1
        except ValueError:
            pass

    if numbers < want_numbers:
        errList.append(f"Password must have at least {want_numbers} numbers from 0-9")


def registerUser(email, password, repass):
    errList = []
    if password != repass:
        errList.append("Passwords doesn't match")
        return errList
    if not getPasswordViolations(errList, password):
        return errList
    return None
