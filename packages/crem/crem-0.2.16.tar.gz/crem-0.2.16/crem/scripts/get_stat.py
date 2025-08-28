import sqlite3 as sqlite
from rdkit import Chem
from rdkit.Chem.Scaffolds.MurckoScaffold import GetScaffoldForMol

db_name = '/home/pavel/QSAR/crem/0.2/db_noB_noC5_sc2/replacements02_sc2.db'
output = 'r1.txt'

con = sqlite.connect(db_name)
cur = con.cursor()
cur.execute('select core_smi from radius1')

with open(output, 'wt') as f:
    for i, row in enumerate(cur, 1):
        m = Chem.MolFromSmiles(row[0])
        a = GetScaffoldForMol(m).GetNumHeavyAtoms()
        b = m.GetNumHeavyAtoms()
        d = round(a / b, 3) if b > 0 else 0
        f.write('\t'.join(map(str, (a, b, d))) + '\n')
        if i % 1000 == 0:
            print(i)
