from mdlang.syntax import Sheet

if __name__ == '__main__':
    with open('data/md/gen/pass_test.md', 'w+') as testmd:
        testmd.write(
            Sheet(
                sheet=[
                    ['0','1','2','3','4'],
                    ['0','1','2'],
                    ['0','1','2','3'],
                    ['0','1'],
                    [],
                ],
                rowhdr=['$1', '$2', '$3', '$4', '$5', '$6', '$7'],
                linehdr=['A','B','C'],
                align=['<','<','>','>'],
            ).__str__())
        testmd.close()