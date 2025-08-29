from setuptools import setup

setup(
    name='payload-generator',
    version='0.6.0',    
    description='A package for generating payloads for sending to the Ingestion Gateway.',
    url='https://gitlab-app.eng.qops.net/zkhatri/payload-generator',
    author='Zeshan Khatri',
    author_email='zkhatri@qualtrics.com',
    packages=['payload_generator'],
    include_package_data=True,
    install_requires=['faker>=3.0.1',
                      'importlib-resources>=6.5.2'
                      ],
    entry_points={
        'console_scripts': [
            'payload-generator=payload_generator:generate_payloads'
        ]
    },
    classifiers=[    
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
