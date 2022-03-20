import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CT_TIQUA",
    version="0.0.1",
    author="Brossard Clement",
    author_email="clement.brossard@univ-grenoble-alpes.fr",
    description="computed Tomography traumatic brain Injury QUAntification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=['CT_TIQUA'],
    package_data={'': ['data/*', 'README.md']},
    entry_points={
        'console_scripts': [
            'ct-tiqua = CT_TIQUA.console_tool:console_tool',
            'ct-test = CT_TIQUA.console_tool:console_test'
        ]
    },
    install_requires=[
        'scipy==1.4',
        'numpy',
        'Cython',
        'pandas',
        'nibabel',
    ],
    python_requires='>=3.6',
)
