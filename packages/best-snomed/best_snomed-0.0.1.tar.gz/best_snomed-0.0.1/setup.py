from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='best_snomed',
  version='0.0.1',
  description='Fetches the top n SNOMED codes given a patient context',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Joshua Lowe',
  author_email='adinathdmohan97@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='SNOMED', 
  packages=find_packages(),
  install_requires=['ollama','dspy'] 
)