import argparse
import numpy as np
import pandas as pd
import os
import random
import sys
from utils.gen_data import generate_correlated_gaussian_vectors
import json 



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Synth Data Generation')


    #mu num
    parser.add_argument('--n_mu', type=int, required=True,  help='Количество сценариев')

    #path to data
    parser.add_argument('--params_path', type=str, required=True,  help='Путь до JSON-файла с параметрами (mu и sigma)')

    #config for params of norm distr
    parser.add_argument('--output_path', type=str, required=True,  help='Путь для сохранения итоговых данных')

    parser.add_argument('--n_samples', type=int, default= 200, help='Количество сэмплов для генерации (по умолчанию: 100)')

    args = parser.parse_args()
    # Загрузка параметров из JSON
    with open(args.params_path, 'r', encoding='utf-8') as f:
        params = json.load(f)

    mu = [np.array(params[f'mu{i}']) for i in range(1, args.n_mu+1)]
    sigma = np.array(params['sigma'])
    
    for m in mu:
        generate_correlated_gaussian_vectors(m, sigma, args.output_path, n_samples=args.n_samples)
    

