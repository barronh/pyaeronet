import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("pyaeronet/__init__.py", "r") as fh:
    for l in fh:
        if l.startswith('__version__'):
            exec(l)
            break
    else:
        __version__ = 'x.y.z'

setuptools.setup(
    name="pyaeronet",
    version=__version__,
    author="Barron H. Henderson",
    author_email="barronh@gmail.com",
    description="Python interface to AEROSOL ROBOTIC NETWORK (AERONET) web-service v3 API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barronh/pyaeronet",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pandas", "requests"
    ],
)
