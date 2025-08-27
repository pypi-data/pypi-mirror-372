def somefunc() -> None:
    return None

class someclass():
    def __init__(self):
        pass

for elem in [
    None,
    1,-1,0,
    3.14,-3.14,0.00,
    True,False,
    '','MyName','13&amp;15',
    [],[1,2,3],
    {},{'key':'val'},
    {1,2,3},
    somefunc,
    someclass,
    (), (1,2,3), (1,'str',False),
    3+4j,5.03+4.09j,
]:
    print(f'type:{type(elem)}, ==None:{elem==None}, isNone:{elem is None}, value:{elem}')