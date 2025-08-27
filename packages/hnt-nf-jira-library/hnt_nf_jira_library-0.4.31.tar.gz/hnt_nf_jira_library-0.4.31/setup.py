from setuptools import setup, find_packages

setup(
    name='hnt_nf_jira_library',
    version='0.4.31',
    license='MIT License',
    author='Guillerme Rezende Manhaes',
    keywords='nota_fiscal',
    description=u'Lib to access nf from Jira',
    packages=find_packages(),
    package_data={'nf_jira': ['entities/*','entities/classes/*']},
    include_package_data=True,
    install_requires=[
        'requests',
        'pydantic>=2.5.2'
    ],
)