from setuptools import setup, find_packages

setup(
    name='LoSearch',
    version='0.1.0',
    description='A high-performance Python search library with intelligent relevance scoring, advanced indexing capabilities, and multilingual support for Persian and English.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Madric',
    author_email='madric.offical@gmail.com',
    url='https://github.com/MadricTeam/LoSearch',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'build>=1.2.2',
        'flask>=3.0.3',
        'nltk>=3.9.1',
        'redis>=6.1.1',
        'scikit-learn>=1.3.2',
        'sqlalchemy>=2.0.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    include_package_data=True,
)
