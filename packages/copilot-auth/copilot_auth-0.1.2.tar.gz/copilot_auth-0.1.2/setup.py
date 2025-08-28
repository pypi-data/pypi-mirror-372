from os import path
from setuptools import setup


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='copilot_auth',
      version='0.1.2',
      long_description=long_description,
      long_description_content_type='text/markdown',
      description='Copilot authentication library to get GitHub and Copilot tokens',
      url='https://github.com/bhachauk/copilot-auth.git',
      author='Bhanuchander Udhayakumar',
      author_email='bhanuchander210@gmail.com',
      license='MIT',
      packages=['copilot_auth'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['requests']
      )
