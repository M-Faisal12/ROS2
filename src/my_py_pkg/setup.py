from setuptools import find_packages, setup

package_name = 'my_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'sounddevice',
        'numpy',
        'scipy',
        'speech_recognition',
        'sentence-transformers',
        'sqlite3'
    ],
    zip_safe=True,
    maintainer='M-Faisal',
    maintainer_email='mfaisalsaeed18@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        "test_node = my_py_pkg.my_first_node:main",
        "number_publisher = my_py_pkg.number_publisher:main",
        "number_counter = my_py_pkg.number_counter:main",
        "reset_counter_client=my_py_pkg.reset_counter_client:main",
        "listen=my_py_pkg.listener:main",
        "note=my_py_pkg.notes:main",
        "schedule=my_py_pkg.schedule:main",
    ],
},
)
