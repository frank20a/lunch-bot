import os
from glob import glob


keys = {}
for filename in glob(os.path.join(os.getcwd(), 'keys/*.key')):
    try:
        with open(filename, 'r') as f:
            keys[os.path.basename(filename).strip('.key')] = f.read()
    except FileNotFoundError:
        keys[os.path.basename(filename).strip('.key')] = os.environ.get(f'{os.path.basename(filename).strip(".key")}_KEY')
