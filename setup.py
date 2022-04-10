import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='gitdir',
    version='1.2.6',
    author='Siddharth Dushantha',
    author_email='siddharth.dushantha@gmail.com',
    description='Download a single directory/folder from a GitHub repo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sdushantha/gitdir',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'gitdir = gitdir.gitdir:main',
        ]
    },
    install_requires=['colorama~=0.4']
)
