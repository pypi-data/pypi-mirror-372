from setuptools import setup

with open('AFR_manual.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='AFR',
    version='3.0.1',
    description='Statistical toolkit aimed to help statisticians, data analysts, data scientists, bankers and other professionals to analyze financial data',
    author='Timur Abilkassymov, Alua Makhmetova, Sultan Zhaparov',
    author_email='sultan.saldau@gmail.com',
    url='https://github.com/AFRKZ/AFR',
    license="3-clause BSD",
    packages=['AFR', 'AFR.load'],
    package_dir={'': '.'},
    install_requires=[
        'setuptools>=66.6.0', 'pandas',
        'scikit-learn>=1.3.1', 'numpy', 'statsmodels',
        'matplotlib', 'mlxtend'
    ],
    package_data={'AFR': ['load/*.csv', 'load/*.rst']},
    include_package_data=True,
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    options={
        'bdist_wheel': {
            'universal': True,
        }
    }
)
