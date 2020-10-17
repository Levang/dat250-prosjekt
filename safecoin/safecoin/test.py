from safecoin.accounts_db import accList_to_accStr, accStr_to_accList

if __name__ == '__main__':
    a = accList_to_accStr([["b'asdf", 41036948399, ('200.00')], ["'asad", 41166950088, ('10000.00')], ['olebrum', 41986922455, ('100.00')],
          ['nice', 42856961288, ('0.00')], ['dfsa', 42916946666, ('100.00')], ['a', 41536996844, ('100.00')],
          ['A1', 42726911000, ('100.00')], ['sadg', 41096966177, ('100.00')]])
    print(a)
