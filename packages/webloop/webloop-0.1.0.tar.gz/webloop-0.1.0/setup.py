from setuptools import setup, find_packages

setup(
    name="webloop",
    version="0.1.0",
    description="Flask-inspired Python web framework with ORM, Auth, and NanoHTML.",
    author="Aftab Alam",
    author_email="aftabbytex@gmail.com",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'webloop=webloop.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],
)
