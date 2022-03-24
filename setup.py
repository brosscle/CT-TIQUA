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
    packages=['CT_TIQUA', 'CT_TIQUA.blast_ct', 'CT_TIQUA.blast_ct.blast_ct', 'CT_TIQUA.blast_ct.blast_ct.trainer', 'CT_TIQUA.blast_ct.blast_ct.nifti', 'CT_TIQUA.blast_ct.blast_ct.models', 'CT_TIQUA.python_scripts'],
    package_data={'': ['data/*', 'README.md', 'data/saved_models/*.pt', 'data/config.json', 'data/Labels_With_0.csv', 'data/Resliced_Registered_Labels_mod.nii.gz', 'data/TEMPLATE_miplab-ncct_sym_brain.nii.gz']},
    scripts=['CT_TIQUA/python_scripts/Volume_Estimation.py'],
    entry_points={
        'console_scripts': [
            'ct-tiqua = CT_TIQUA.console_tool:console_tool',
        ]
    },
    install_requires=[
        'scipy==1.4',
        'numpy',
        'pandas',
        'nibabel',
        'torch',
        'SimpleITK==1.2.4',
        'tensorboard',
        'pybids',
        'antspyx',
        'nipype',
    ],
    python_requires='>=3.7',
)
