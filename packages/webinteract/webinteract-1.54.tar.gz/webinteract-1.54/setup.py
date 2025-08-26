import os

from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
requires = ['splinter', 'selenium', 'keyring', 'prompt_toolkit', 'colorama']

from setuptools.command.egg_info import egg_info
class egg_info_ex(egg_info):
    """Includes license file into `.egg-info` folder."""
    def run(self):
        # don't duplicate license into `.egg-info` when building a distribution
        if not self.distribution.have_run.get('install', True):
            # `install` command is in progress, copy license
            self.mkpath(self.egg_info)
            self.copy_file('LICENSE', self.egg_info)
        egg_info.run(self)
        
setup(
    name='webinteract',
    version='1.54',    
    description='A Python module for simple web interaction',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.pg12.org/software',
    project_urls={
        "Documentation": "https://blog.pg12.org/web-page-interaction-in-python",
        "Download": "https://www.pg12.org/dist/py/lib/webinteract/",
    },
    author='A Andersen',
    author_email='a.andersen@pg12.org',
    license='Modified BSD License',
    license_files = ('LICENSE',),
    cmdclass = {'egg_info': egg_info_ex},
    packages=['webinteract'],
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'webinteract=webinteract:main']},
    classifiers=[
        'License :: OSI Approved :: BSD License',  
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
