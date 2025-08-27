# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


setup_args = dict(
    name="notonames",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "notonames=notonames.notonames:main",
        ],
    },
    setup_requires=["setuptools_scm"],
    install_requires=[
        "absl-py>=2.3.1",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black==25.1.0",
        ],
    },
    # this is so we can use the built-in dataclasses module
    python_requires=">=3.9",
    # metadata to display on PyPI
    author="Rod S",
    author_email="rsheeter@google.com",
    description=(
        "Checks for noto-emoji style filenames"
    ),
)


if __name__ == "__main__":
    setup(**setup_args)