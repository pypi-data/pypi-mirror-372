from conv.parse import json2md
from json import loads

if __name__=='__main__':
    for filename in ['full_test','gin-README']:
        with open(f'data/json/{filename}.json') as ginj:
            with open(f'data/md/{filename}-gen.md', 'w+') as ginmd:
                texts = json2md(loads(ginj.read()))
                ginmd.write('\n\n'.join(texts))
                ginmd.close()
                ginj.close()