import argparse
import json
import os
from typing import List

import datetime
import random
from rdkit import Chem
from rdkit.Chem.Descriptors import MolWt

from guacamol.assess_distribution_learning import assess_distribution_learning
from guacamol.distribution_matching_generator import DistributionMatchingGenerator
from guacamol.utils.helpers import setup_default_logger

from crem.crem import mutate_mol


def get_random_smi(fname):
    with open(fname) as afile:
        line = next(afile)
        for num, aline in enumerate(afile, 2):
            if random.randrange(num):
                continue
            line = aline
        return line


class CREM_Generator(DistributionMatchingGenerator):

    def __init__(self, input_smi, db_fname, radius, min_size, max_size, min_inc, max_inc, max_replacements, min_freq,
                 max_mw, ncpu, output_dir):
        self.input_smi_fname = input_smi
        self.db_fname = db_fname
        self.radius = radius
        self.min_size = min_size
        self.max_size = max_size
        self.min_inc = min_inc
        self.max_inc = max_inc
        self.max_replacements = max_replacements
        self.max_mw = max_mw
        self.ncpu = ncpu
        self.min_freq = min_freq
        self.output_dir = output_dir

    def generate(self, number_samples: int) -> List[str]:

        population = []

        smi = get_random_smi(self.input_smi_fname)
        mol = Chem.AddHs(Chem.MolFromSmiles(smi))
        while MolWt(mol) >= 450:
            smi = get_random_smi(self.input_smi_fname)
            mol = Chem.AddHs(Chem.MolFromSmiles(smi))

        while len(population) < number_samples:

            new_smi = list(mutate_mol(mol, db_name=self.db_fname, radius=self.radius, min_size=self.min_size,
                                      max_size=self.max_size, min_rel_size=0, max_rel_size=0.3, min_inc=self.min_inc,
                                      max_inc=self.max_inc, max_replacements=self.max_replacements,
                                      replace_cycles=False, min_freq=self.min_freq, ncores=self.ncpu))
            new_smi = [s for s in new_smi if MolWt(Chem.MolFromSmiles(s)) <= self.max_mw]
            population.extend(new_smi)
            if new_smi:
                mol = Chem.AddHs(Chem.MolFromSmiles(random.choice(new_smi)))
            else:
                mol = Chem.AddHs(Chem.MolFromSmiles(random.choice(population)))

        with open(os.path.join(self.output_dir, str(datetime.datetime.now().time()) + '.smi'), 'wt') as f:
            f.write(smi + '\n')
            f.write('\n'.join(population[:number_samples]))

        return population[:number_samples]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smiles_file',
                        help='Location of the ChEMBL dataset to use for the distribution benchmarks.')
    parser.add_argument('--db', type=str)
    parser.add_argument('--radius', type=int, default=3)
    parser.add_argument('--min_size', type=int, default=0)
    parser.add_argument('--max_size', type=int, default=8)
    parser.add_argument('--min_inc', type=int, default=-2)
    parser.add_argument('--max_inc', type=int, default=2)
    parser.add_argument('--max_replacements', type=int, default=100)
    parser.add_argument('--min_freq', type=int, default=0)
    parser.add_argument('--max_mw', type=float, default=500)
    parser.add_argument('--ncpu', type=int, default=1)
    # parser.add_argument('--input_smiles', type=str, default='c1ccccc1')
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--suite', default='v2')
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

    setup_default_logger()

    # save command line args
    with open(os.path.join(args.output_dir, 'distribution_learning_params.json'), 'w') as jf:
        json.dump(vars(args), jf, sort_keys=True, indent=4)

    sampler = CREM_Generator(input_smi=args.smiles_file,
                             db_fname=args.db,
                             radius=args.radius,
                             min_size=args.min_size,
                             max_size=args.max_size,
                             min_inc=args.min_inc,
                             max_inc=args.max_inc,
                             max_replacements=args.max_replacements,
                             min_freq=args.min_freq,
                             max_mw=args.max_mw,
                             output_dir=args.output_dir,
                             ncpu=args.ncpu)

    json_file_path = os.path.join(args.output_dir, 'distribution_learning_results.json')
    assess_distribution_learning(sampler, json_output_file=json_file_path, chembl_training_file=args.smiles_file,
                                 benchmark_version=args.suite)


if __name__ == "__main__":
    main()