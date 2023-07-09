from pathlib import Path
from typing import List

from setuptools import find_packages, setup

from mullvad_closest import __version__


def read_lines(file_path: Path) -> List[str]:
    with file_path.open("r") as f:
        return f.readlines()


setup(
    name="mullvad-closest",
    version=__version__,
    description="Find Mullvad servers with the lowest latency at your location",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Andrii Yurchuk",
    author_email="ay@mntw.re",
    license="Unlicense",
    url="https://github.com/Ch00k/mullvad-closest",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_lines(Path(__file__).parent / "requirements.txt"),
    entry_points={
        "console_scripts": ["mullvad-closest = mullvad_closest.cli:find"],
    },
)
