#!/usr/bin/env python

__author__ = 'pavel'

import argparse
import sys
from multiprocessing import Pool, cpu_count
from rdkit import Chem
from rdkit.Chem import Descriptors


patterns = ['[C-,C+,S+,S-,P-,P+,Cl-,Br-,I-,Cl+,Br+,I+,O+]',
            '[CX4R0]([H,Cl,F,Br,I])([H,Cl,F,Br,I])[CX4R0]([H,Cl,F,Br,I])([H,Cl,F,Br,I])[CX4R0]([H,Cl,F,Br,I])([H,Cl,F,Br,I])[CX4R0]([H,Cl,F,Br,I])([H,Cl,F,Br,I])[CX4R0]([H,Cl,F,Br,I])([H,Cl,F,Br,I])']
patterns = [Chem.MolFromSmarts(a) for a in patterns]
org_elm = {'H', 'C', 'O', 'N', 'F', 'Cl', 'Br', 'I', 'P', 'S'}


def read_smiles(fname):
    # returns SMILES or SMILES and mol name
    with open(fname) as f:
        for line in f:
            yield line.strip().split()[:2]


def process_smi(smi, mol_name):
    mol = Chem.MolFromSmiles(smi)
    if mol:
        if Descriptors.NumRadicalElectrons(mol) == 0:
            a = set(a.GetSymbol() for a in mol.GetAtoms())
            if not a.difference(org_elm):
                if not any(mol.HasSubstructMatch(q) for q in patterns):
                    return mol_name
    return None


def process_smi_map(items):
    return process_smi(*items)


def entry_point():
    parser = argparse.ArgumentParser(description='Returns names of compounds which do not contain undesired patterns, '
                                                 'non-organic atoms or radicals.')
    parser.add_argument('-i', '--input', metavar='FILENAME', required=True,
                        help='SMILES file separated by whitespaces and containing compound names.')
    parser.add_argument('-o', '--output', metavar='FILENAME', required=True,
                        help='output text file with compound names which satisfy all requirements.')
    parser.add_argument('-c', '--ncpu', metavar='NUMBER', required=False, default=1, type=int,
                        help='number of cpus used for computation. Default: 1.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='print progress.')
    args = parser.parse_args()

    pool = Pool(min(max(cpu_count(), args.ncpu), 1))

    with open(args.output, 'wt') as f:
        for i, mol_name in enumerate(pool.imap(process_smi_map, read_smiles(args.input), chunksize=10), 1):
            if mol_name:
                f.write(mol_name +'\n')
            if args.verbose and i % 1000:
                sys.stderr.write(f'\r{i} molecules were passed')


if __name__ == '__main__':
    entry_point()
