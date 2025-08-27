from setuptools import setup, find_packages

with open('scr/README.md', 'r') as f:
    long_description = f.read()

setup(
    name='streamapp',
    version='0.0.13',
    author='nmrls',
    description='Base modules to use in a Streamlit basic project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nmrls/streamapp_utils',
    package_dir={'': 'scr'},
    packages=find_packages(where='scr'),
    license='MIT License',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.10.0',
    install_requires=[
        'streamlit>=1.30.0',
        'pydantic>=2.5.3',
        'openpyxl==3.1.2',
        'snowflake-connector-python>=3.0.4',
        'streamlit-authenticator==0.3.2',
        'pymongo==4.6.3',
        'twine>=4.0.2'
    ]
)
