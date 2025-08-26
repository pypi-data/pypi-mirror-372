from setuptools import setup

setup(
    name='erioon',
    version='0.6.1',
    author='Zyber Pireci',
    author_email='zyber.pireci@erioon.com',
    description='Erioon Python SDK for seamless interaction with Erioon data services',
    long_description=(
        "The Erioon SDK for Python provides a robust interface to interact "
        "with Erioon resources such as collections, databases, and playboxes. "
        "It supports CRUD operations, querying, and connection management "
        "with ease, enabling developers to integrate Erioon data services "
        "into their applications efficiently."
    ),
    long_description_content_type='text/plain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    packages=['erioon'],
    install_requires=[
        'requests>=2.25.1',
        'azure-storage-blob>=12.14.1',
        'msgpack>=1.0.4',
        'scikit-learn>=1.3.0',
        'numpy>=1.24.0',
        'kubernetes==26.1.0',
        'rich>=13.5.2'
    ],
    entry_points={
        'console_scripts': [
            'erioon=erioon.cli:main'
        ]
    },
    python_requires='>=3.6',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
)


