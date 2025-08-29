# Auteur : Esteban COLLARD, Nordine EL AMMARI
# Modifications : Reda ID TALEB & Manal LAGHMICH

from setuptools import find_packages, setup
import os.path


def recursive_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            if not filename.endswith(".pyc"):
                paths.append(os.path.join('..', path, filename))
    return paths

packages = find_packages()

def get_packages_data(packages: list[str]=packages):
    py_packs = dict([(p, ["*.py"]) for p in packages])
    unpackaged = {"": recursive_files("thonnycontrib/i18n/locale") + recursive_files("thonnycontrib/img")}
    return {**py_packs, **unpackaged} 

setupdir = os.path.dirname(__file__)


requirements = []
for line in open(os.path.join(setupdir, "requirements.txt"), encoding="ASCII"):
    if line.strip() and not line.startswith("#"):
        requirements.append(line)
        
setup(
    name="L1test",
    version="3.2.1",
    author="Mirabelle MARVIE-NEBUT, Reda ID TALEB",
    description="A plug-in which adds a test framework",
    long_description="""A plug-in for Thonny which allows you to test your doc examples
 
More info: https://gitlab.univ-lille.fr/mirabelle.nebut/thonny-tests""",
    url="https://gitlab.univ-lille.fr/mirabelle.nebut/thonny-tests",
#    keywords="IDE education programming tests in documentation",
    classifiers=[
        "Topic :: Education :: Testing",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education"
        ],
    platforms=["Windows", "macOS", "Linux"],
    python_requires=">=3.9",
    package_data=get_packages_data(),
    install_requires=requirements,
    packages=packages,
)

