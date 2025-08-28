#!/usr/bin/env python3

import argparse

from rdkit import Chem
from crem.utils import enumerate_compounds


database_dict = {'sa2': '/home/pavel/QSAR/crem/0.2/db_noB_C5_sa2/replacements.db',
                 'sa25': '/home/pavel/QSAR/crem/0.2/db_noB_noC5_sa2.5/replacements.db',
                 'sa2f5': '/home/pavel/QSAR/crem/0.2/replacements_sa2_f5.db',
                 'sa25f5': '/home/pavel/QSAR/crem/0.2/replacements_sa25_f5.db'}

# database_dict = {'sa2': '/home/spci/.crem/db/replacements_sa2.db',
#                  'sa25': '/home/spci/.crem/db/replacements_sa25.db',
#                  'sa2f5': '/home/spci/.crem/db/replacements_sa2_f5.db',
#                  'sa25f5': '/home/spci/.crem/db/replacements_sa25_f5.db'}


def type_database(x):
    try:
        v = database_dict[x]
    except KeyError:
        raise ValueError(f'Supplied database argument {x} is wrong, it does not correspond to the predefined list')
    return v


def type_radius(x):
    return max(min(int(x), 5), 1)


def type_ids(x):
    return int(x) - 1


def entry_point():
    parser = argparse.ArgumentParser(description='Enumerate molecules based on a seed structure using CReM fragment '
                                                 'databases.')
    parser.add_argument('-i', '--input', metavar='input.sdf', required=True,
                        help='input MOL file.')
    parser.add_argument('-o', '--output', metavar='output.smi', required=True,
                        help='output SMILES file with enumerated structures.')
    parser.add_argument('-m', '--mode', metavar='scaffold/analogs', required=False, default='scaffold',
                        help='scaffold decoration or analogs enumeration.')
    parser.add_argument('--ids', metavar='INTEGER', required=False, default=None, nargs='*', type=type_ids,
                        help='ids of atoms to modify (starting from 1). If omitted, modifications will be applied to '
                             'all atoms.')
    parser.add_argument('-n', '--n_iterations', metavar='INTEGER', required=False, default=1, type=int,
                        help='number of consecutive iterations.')
    parser.add_argument('-d', '--database', metavar='/'.join(database_dict.keys()), required=False, default='sa2',
                        type=type_database, help='number of consecutive iterations.')
    parser.add_argument('-r', '--radius', metavar='INTEGER', required=False, default=3, type=type_radius,
                        help='context radius considered for fragment replacement.')
    parser.add_argument('--max_replacements', metavar='INTEGER', required=False, default=None, type=int,
                        help='maximum number of modifications applied for each molecule.')
    parser.add_argument('-s', '--max_size', metavar='INTEGER', required=False, default=10, type=int,
                        help='maximum size of a fragment to be replaced or added.')
    parser.add_argument('-c', '--ncpu', metavar='INTEGER', required=False, default=1,
                        help='Number of CPU cores to use. Default: 1.')

    args = parser.parse_args()

    mol = Chem.MolFromMolFile(args.input, removeHs=False)

    if args.mode == 'scaffold':
        smi = enumerate_compounds(mol, db_fname=args.database, mode=args.mode, n_iterations=args.n_iterations,
                                  radius=args.radius, max_replacements=args.max_replacements, return_smi=True,
                                  replace_ids=args.ids, max_atoms=args.max_size, ncpu=args.ncpu)
    elif args.mode == 'analogs':
        smi = enumerate_compounds(mol, db_fname=args.database, mode=args.mode, n_iterations=args.n_iterations,
                                  radius=args.radius, max_replacements=args.max_replacements, return_smi=True,
                                  replace_ids=args.ids, max_size=args.max_size, min_size=0, ncpu=args.ncpu)
    else:
        raise ValueError(f'Supplied mode should be only "scaffold" or "analogs".')

    with open(args.output, 'wt') as f:
        f.write('\n'.join(smi))


if __name__ == '__main__':
    entry_point()
