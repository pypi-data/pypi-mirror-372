from setuptools import setup
import os


requirements = []
f = open('requirements.txt', 'r')
while True:
    l = f.readline()
    if l == '':
        break
    requirements.append(l.rstrip())
f.close()
f = open('html_requirements.txt', 'r')
while True:
    l = f.readline()
    if l == '':
        break
    requirements.append(l.rstrip())
f.close()

test_requirements = []
f = open('test_requirements.txt', 'r')
while True:
    l = f.readline()
    if l == '':
        break
    test_requirements.append(l.rstrip())
f.close()

f = open('README.md', 'r')
description = f.read()
f.close()


setup(
        install_requires=requirements,
        tests_require=test_requirements,
        data_files=[("man/man1", ["man/man1/piknik.1"],)],
        long_description=description,
        long_description_content_type='text/markdown',
    )
