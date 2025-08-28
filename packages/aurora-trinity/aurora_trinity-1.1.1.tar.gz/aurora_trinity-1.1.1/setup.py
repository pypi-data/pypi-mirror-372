from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name='aurora-trinity',
    version='1.1.1',
    description='Aurora Trinity-3: Fractal, Ethical, Free Electronic Intelligence',
    long_description=(here / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='Aurora Alliance',
    author_email='contacto@aurora-program.org',
    url='https://github.com/Aurora-Program/Trinity-3',
    license='Apache-2.0',
    packages=['trinity_3'],
    python_requires='>=3.8',
    install_requires=[
        # No external dependencies - pure Python implementation
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Natural Language :: Spanish',
    ],
    keywords='ai, ternary-logic, fractal, neural-networks, knowledge-base, ethical-ai',
    project_urls={
        'Bug Reports': 'https://github.com/Aurora-Program/Trinity-3/issues',
        'Source': 'https://github.com/Aurora-Program/Trinity-3',
        'Documentation': 'https://github.com/Aurora-Program/Trinity-3/blob/main/README.md',
    },
)
