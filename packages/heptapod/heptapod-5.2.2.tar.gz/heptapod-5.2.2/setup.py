from pathlib import Path
from setuptools import setup, find_packages

with open('install-requirements.txt', 'r') as install_reqf:
    install_req = [req.strip() for req in install_reqf]

VERSION_FILE = 'VERSION'

setup(
    name='heptapod',
    version=Path('heptapod', VERSION_FILE).read_text().strip(),
    author='Georges Racinet',
    author_email='georges.racinet@octobus.net',
    url='https://foss.heptapod.net/heptapod/py-heptapod',
    description="Heptapod server-side Mercurial hooks, extension, etc.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords='hg mercurial heptapod gitlab',
    license='GPLv2+',
    package_data=dict(heptapod=['*.hgrc', VERSION_FILE]),
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
        " :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Software Development :: Version Control :: Mercurial",
    ],
    install_requires=install_req,
)
