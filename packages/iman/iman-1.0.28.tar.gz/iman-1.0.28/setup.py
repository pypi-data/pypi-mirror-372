import os
from setuptools import setup, find_packages
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    


setup(
        # the name must match the folder name 'verysimplemodule'
        name="iman", 
        version='1.0.28',
        author="Iman Sarraf",
        author_email="imansarraf@gmail.com",
        description='Python package for daily Tasks',
        long_description=read('README.rst'),
        packages=find_packages(),
        
        # add any additional packages that 
        # needs to be installed along with your package.
        install_requires=['scipy','numpy','six','matplotlib','joblib'], 
        
        keywords=['python', 'iman'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
        ]
        

)