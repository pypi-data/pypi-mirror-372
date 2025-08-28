from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="netcontrol",
    version="1.106",
    author="Cedric GUSTAVE",
    author_email="cgustave@free.fr",
    description="Package netcontrol",
	long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cgustave/netcontrol",
    packages=find_packages(),
    classifiers=[
	    "Development Status :: 4 - Beta",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: POSIX :: Linux",
		"Natural Language :: English",
		"Topic :: System :: Networking",
    ],
    python_requires='>=3.5',
)

