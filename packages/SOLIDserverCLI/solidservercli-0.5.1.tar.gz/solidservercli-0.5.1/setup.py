from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='SOLIDserverCLI',
    version='0.5.1',
    description='EfficientIP SOLIDserver cli',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Alex Chauvin',
    author_email='ach@efficientip.com',
    project_urls={
        'GitHub': 'https://gitlab.com/efficientip/cli-for-solidserver',
        'Changelog': 'https://gitlab.com/efficientip/cli-for-solidserver/-/raw/master/CHANGELOG.md',
    },
    url='https://gitlab.com/efficientip/cli-for-solidserver',
    license=license,
    packages=['sds'],

    entry_points={
        'console_scripts': [
            'sds = sds.cli:main',
        ],
    },

    python_requires='>=3.10',
    install_requires=['typer',
                      'rich',
                      'SOLIDserverRest>=2.9.5'],

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: System :: Networking"
    ],
)
