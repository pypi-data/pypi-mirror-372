from mdconv.parse import explain_json
from json import loads

if __name__=='__main__':
    for filename in ['fulltest', 'gin', 'tensorflow', 'frp', 'drawnix']:
        with open(f'data/json/{filename}.json') as jsonf:
            with open(f'data/md/gen/{filename}.md', 'w+') as mdf:
                mdf.write(explain_json(loads(jsonf.read())))
                mdf.close()
                jsonf.close()