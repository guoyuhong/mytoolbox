from setuptools import setup, find_packages
import setuptools.command.build_ext

import os
import subprocess
import sys

py_version = sys.version_info[:2]

assert py_version > (3, 5), "Python3.6 is the lowest supported version"

# gtbox is short for GYH's tool box.
PACKAGE_NAME = "gtbox"

requires = [
    "yapf==0.32.0",
]

tests_require = []

testing_extras = tests_require + [
    'pytest',
]

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
print("find_packages():" + str(find_packages()))
VERSION = "0.0.1"
README = "GYH's toolbox for github projects"

# If extend build required, implement this.
def pip_run(build_ext):
    pass


class my_build_ext(setuptools.command.build_ext.build_ext):
    def run(self):
        return pip_run(self)


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=README,
    author='Yuhong Guo',
    author_email='guoyuhong1985@outlook.com',
    url='https://github.com/guoyuhong',
    packages=find_packages(),
    cmdclass={"build_ext": my_build_ext},
    python_requires='>=3.6',
    install_requires=requires,
    extras_require={
        'testing': testing_extras,
    },
    include_package_data=True,
    tests_require=tests_require,
    test_suite=(PACKAGE_NAME + ".test"),
    entry_points={
        'console_scripts': [
            'ortdeps=gtbox.onnxruntime.download_deps:main',
            'ortlint=gtbox.onnxruntime.lint:main',
        ],
    },
    scripts=[],
)
