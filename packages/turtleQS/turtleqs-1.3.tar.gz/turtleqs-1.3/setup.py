from setuptools import setup, find_packages

setup(
    name='turtleQS',
    version='1.3',
    packages=find_packages(),
    install_requires=[
        
    ],
    entry_points={
        "console_scripts":[
            "turtleQS = turtleQS:TurtleQS"
        ],
    },
)