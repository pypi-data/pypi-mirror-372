from setuptools import setup, find_packages

setup(
    name="xlizard",
    version="1.1.0",
    packages=find_packages(),  # Автоматически найдет все подпакеты
    package_data={
        'xlizard': [
            'xlizard_ext/*',
            'xlizard_languages/*',
        ],
    },
    install_requires=[
        'jinja2>=3.1.3',
        'tqdm>=4.67.1',
        'pathspec>=0.12.1',
        'lxml>=5.1.0',
        'pygments>=2.19.2',
        'chardet>=5.2.0',
        'psutil>=5.9.8',
        'multiprocess>=0.70.16',
        'colorama>=0.4.6',
    ],
    entry_points={
        "console_scripts": [
            "xlizard = xlizard.xlizard:main",
        ],
    },
    description="Extended Lizard with additional static code analysis features",
    author="Xor1no",
    license="Proprietary",
)