from setuptools import setup, find_packages


setup(
    name='logery',
    version='1.1.1',
    packages=find_packages(),
    install_requires=[
        'rich',
        'python-dotenv'
    ],
    description='Logs personalizados',
    author='Miguel Tenório',
    author_email='deepydev42@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
