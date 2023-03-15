from setuptools import setup


setup(
    name='homie-client-rx',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=['homieclientrx',],
    license='MIT License',
    author='Brice Copy',
    url='https://github.com/cmcrobotics/homie-client-rx',
    description='Reactive client to interact with Homie IoT devices via MQTT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.0',
    platforms='any',
    install_requires=[
        'paho-mqtt==1.6.1',
        'RxPy3==1.0.2'
    ],
    tests_require=['pytest', 'callee'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Home Automation"
    ]
)
