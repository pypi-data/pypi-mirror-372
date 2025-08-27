from setuptools import setup, find_packages

def read_version():
    version = {}
    with open(os.path.join("ustat_var", "_version.py")) as f:
        exec(f.read(), version)
    return version["__version__"]

setup(
    name='ustat_var',
    version=read_version(),
    description='Unbiased estimators for variance of teacher effects',
    packages=find_packages(),  
    install_requires=[
        'numpy',
        'scipy',
    ],
    python_requires='>=3.7',
)
