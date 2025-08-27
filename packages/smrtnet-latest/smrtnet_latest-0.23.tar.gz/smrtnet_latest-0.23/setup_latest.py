

# -*- coding:utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(name='smrtnet_latest',
        version='0.23',
        packages=find_packages(),
        include_package_data=True,
        package_data={'data': ['data/SMRTnet-data-demo.txt'],\
                      'Figures': ['img_log/*.*'],\
                      'vocab':['LM_Mol/bert_vocab.txt']},
        python_requires="==3.8.10",
        description='A python lib for predicting small molecule-RNA interactions (SRIs)',
        long_description='Small molecules can bind RNAs to regulate their fate and functions, providing promising opportunities for treating human diseases. However, current tools for predicting small molecule-RNA interactions (SRIs) require prior knowledge of RNA tertiary structures, limiting their utility in drug discovery. Here, we present SMRTnet, a deep learning method to predict SRIs based on RNA secondary structure. By integrating large language models, convolutional neural networks, graph attention networks, and multimodal data fusion, SMRTnet achieves high performance across multiple experimental benchmarks, substantially outperforming existing state-of-the-art tools.',
        author='yuhan_Fei & jiasheng_Zhang',
        author_email='yuhan_fei@outlook.com',
        url='https://github.com/Yuhan-Fei/SMRTnet',  # homepage
        license='MIT',
        install_requires=[
"babel",
"charset-normalizer==3.3.2",
"dgllife",
"matplotlib",
"networkx",
"huggingface-hub",
"notebook",
"numpy",
"pandas",
"prefetch_generator",
"prettytable",
"pytorch-lightning",
"rdkit==2022.3.5",
"scikit-learn",
"scipy",
"seaborn",
"tensorboard",
"tensorboardX",
"tqdm",
"transformers==4.28.1",
"xsmiles",
]
    )









