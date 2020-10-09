# Temporary...
class TmpAcc:
    def __init__(self, nr, balance, name="New Account"):
        self.number = nr
        self.balance = balance
        self.name = name

    def delete(self):
        pass


account_list = [TmpAcc(1, 2000, "My Account"), TmpAcc(2, 0), TmpAcc(43, 50, "Soon Million Dollar"), TmpAcc(54, 2000), TmpAcc(7, 0), TmpAcc(12, 50)]
