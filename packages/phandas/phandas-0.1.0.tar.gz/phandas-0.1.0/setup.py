from setuptools import setup, find_packages

setup(
    name='phandas',
    version='0.1.0',
    author='Phantom Management',
    author_email='quantbai@gmail.com',
    description='Simple cryptocurrency data fetching and visualization toolkit by Phantom Management.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/quantbai/phandas',  # 根據您的資訊更新
    packages=find_packages(),
    install_requires=[
        'numpy>=2.0.0',
        'pandas>=2.0.0,<3.0.0',
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'ccxt>=4.0.0',
        'scipy>=1.9.0',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
)
