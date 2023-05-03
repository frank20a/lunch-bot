import os
from glob import glob


keys = {}
for filename in glob(os.path.join(os.getcwd(), 'keys/*.key')):
    with open(filename, 'r') as f:
        keys[os.path.basename(filename).strip('.key')] = f.read()
