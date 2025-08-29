
from setuptools import setup
from setuptools import find_packages

if __name__ == "__main__":
	with open("requirements.txt", "r") as f:
		requirements = f.read().splitlines()

	with open("README.md", "r") as f:
		long_description = f.read()

	setup(
		name = "wela_agents",
		version = "0.0.12",
		packages = find_packages(),
		install_requires = requirements,
		description="An agent framework for Wela",
		long_description = long_description,
		long_description_content_type = "text/markdown",
		author = "Lewis Wu",
		author_email = "lewiswu1209@163.com",
		license = "MIT",
		url = "https://github.com/lewiswu1209/wela_agents.git"
	)
