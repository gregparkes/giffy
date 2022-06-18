from setuptools import setup, find_packages


with open("README.md","r") as fh:
    long_description = fh.read()


setup(
    name='giffy',
    version='0.0.1',    
    description='Turning Data Arrays into GIFs.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gregparkes/giffy',
    author='Gregory Parkes',
    author_email='gregorymparkes@gmail.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    packages=['giffy'],
    python_requires=">=3.7",
    install_requires=[
        'numpy', "matplotlib", "scipy", "pandas"            
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',        
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: IPython",
        "Framework :: Jupyter"
    ],
)