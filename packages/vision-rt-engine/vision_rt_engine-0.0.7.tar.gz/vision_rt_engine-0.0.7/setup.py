#! /usr/bin/env python

import os

from setuptools import find_packages, setup

try:
    with open('README.md', 'r') as f:
        readme = f.read()
except Exception:
    readme = str('')

current_dir = os.path.dirname(os.path.abspath(__file__))
package_name = 'vision_rt_engine'


def install_local_wheels():
    wheels_dir = os.path.join(os.path.dirname(__file__), 'dependencies/')
    return [os.path.join(wheels_dir, fname) for fname in os.listdir(wheels_dir) if fname.endswith('.whl')]


install_requires = [
    'numpy',
    'matplotlib',
    'opencv-python>=4.4',
    'pillow',
    'torch >= 2.0',
    'torchvision',
    'tqdm',
    'pytest',
    'igniter>=1.0.6',
]

setup(
    name=package_name,
    long_description=readme,
    author='Krishneel',
    email='krishneel@krishneel',
    license='MIT',
    version='0.0.7',
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
     data_files=[("wheels", install_local_wheels())],
    test_suite='tests',
    extras_require={
        'full': [
            # 'sam2 @ git+https://github.com/facebookresearch/sam2.git',
        ],
        'dev': [
            'jupyterlab',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
