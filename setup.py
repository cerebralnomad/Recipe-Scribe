from setuptools import setup, find_packages

with open('README.rst', encoding='UTF-8') as f:
    readme = f.read()

setup(
        name = 'recipe_creator',
        version = '0.3.4',
        description = 'No frills recipe creation tool to create and save recipes locally',
        long_description = readme,
        author = 'Clay Davenport'
        author_email = 'cerebralnomad@protonmail.com'
        install_requires = [],
        packages = find_packages('src'),
        package_dir = {'': 'src'}
)

