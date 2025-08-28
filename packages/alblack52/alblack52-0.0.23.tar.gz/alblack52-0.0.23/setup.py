from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
      name='alblack52',
      version='0.0.23',
      author='__token__',
      description='This is the simplest module for quick work with files.',
      packages=['alblack52'],
      author_email='mihajlovic.aleksa@gmail.com',
      zip_safe=False
)
