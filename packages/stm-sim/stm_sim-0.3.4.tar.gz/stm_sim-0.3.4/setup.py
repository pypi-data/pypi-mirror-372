from setuptools import setup

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'ase',
    'surface_construct',
]

setup(
    name='stm_sim',
    version='0.3.4',
    packages=['stm_sim'],
    url='https://gitee.com/pjren/stm_sim',
    license='MIT',
    author='Renpj',
    author_email='0403114076@163.com',
    description='An STM simulation python library.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
