from setuptools import setup

setup(
    name='sqapi',
    version='0.59',
    packages=['sqapi'],
    install_requires=['requests', 'numpy', 'opencv-python', 'tqdm', 'pick'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='A python package that simplifies interactions with the SQUIDLE+ API. It can be used to integrate automated labelling from machine learning algorithms and plenty other cool things.',   # Give a short description about your library
    author='Greybits Engineering',                   # Type in your name
    url='https://bitbucket.org/ariell/pysq',   # Provide either the link to your github or to your website
    # download_url='https://bitbucket.org/ariell/pysq/get/a67b2f1e8082.zip',
    keywords=['SQUIDLE+', 'API', 'SQ', 'Machine Learning'],   # Keywords that define your package best
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)