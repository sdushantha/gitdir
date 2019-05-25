import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='gitdir',
    version='1.0',
    author='Siddharth Dushantha',
    author_email='siddharth.dushantha@gmail.com',
    description='Download a single directory/folder from a GitHub repo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sdushantha/gitdir',
    packages=setuptools.find_packages(),
    scripts=['gitdir/gitdir']
)
