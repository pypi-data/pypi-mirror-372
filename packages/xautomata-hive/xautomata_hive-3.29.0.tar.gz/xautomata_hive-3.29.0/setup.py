from setuptools import find_packages, setup
import os


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()


version = []
with open("hive/version.py", "r") as f:
    for line in f:
        version.append(str(line.strip()))

version = version[0].split("'")[1]

# version go
requests = 'requests==2.31.0'
tqdm = 'tqdm==4.64.1'
urllib3 = 'urllib3==2.0.4'
# version end

setup(
    name='xautomata-hive',
    python_requires='>=3.8.0',
    version=version,
    packages=find_packages(include=['hive*']),
    license='MIT',
    author='Enrico Ferro - Andrea Jacassi',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author_email='',
    description='',
    url="https://github.com/sherlogic/xautomata-hive.git",
install_requires=[requests, tqdm, urllib3],
)
