from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

reqs = [
    'botorch'
]

long_description = "BOTS: Batch Bayesian Optimization of Extended Thompson Sampling for Severely Episode-Limited RL Settings"

if __name__ == '__main__':
    setup(
        name="batchBOTS",
        version='0.0.1',
        package_data={'': ['default.yml']},
        description="BOTS",
        long_description_content_type='text/markdown',
        long_description=long_description,
        author='REML lab developer',
        author_email='remlabdeveloper@gmail.com',
        license='MIT',
        url = 'https://github.com/reml-lab/BOTS/',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Healthcare Industry',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: System :: Distributed Computing'
        ],

        keywords='mHealth machine-learning reinforcement-learning jitai',

        # You can just specify the packages manually here if your project is
        # simple. Or you can use find_packages().
        packages=find_packages(exclude=['contrib', 'docs', 'tests','Examples']),

        # List run-time dependencies here.  These will be installed by pip when
        # your project is installed. For an analysis of "install_requires" vs pip's
        # requirements files see:
        # https://packaging.python.org/en/latest/requirements.html
        install_requires=reqs,

        entry_points={
            'console_scripts': [
                'main=main:main'
            ]
        },

    )
