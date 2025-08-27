from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r", encoding='utf-8') as f:
  long_description = f.read()

setup(name='autofree',  # 包名
      version='1.0.3',  # 版本号
      description='A RPA services API',
      long_description=long_description,
      author='yangmuyi',
      author_email='1791500400@qq.com',
      url='',
      install_requires=[],
      license='GPLv3 License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          # 'Programming Language :: Python',
          # 'Programming Language :: Python :: 2',
          # 'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Topic :: Software Development :: Libraries'
      ],
      )
