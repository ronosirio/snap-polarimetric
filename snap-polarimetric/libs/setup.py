import os
import setuptools

def set_directory():
    # CD to this directory, to simplify package finding
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

set_directory()

setuptools.setup(
    name="interstellar",
    description="Interstellar block utils",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
)
