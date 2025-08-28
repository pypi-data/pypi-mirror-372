#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from setuptools import setup
from os import path, walk

# the name of the package
name = "galaxy"

packages = []

here = path.abspath(path.dirname(__file__))
pkg_root = path.join(here, name)

for d, _, _ in walk(pkg_root):
    if path.exists(path.join(d, "__init__.py")):
        packages.append(d[len(here) + 1:].replace(path.sep, '.'))

setup(name="galaxy-report",
      version="0.0.1",
      author="Bastien Saltel",
      author_email="bastien.saltel@gmail.com",
      description="Galaxy Framework - Reporting Module",
      long_description="Galaxy Framework - Reporting Module",
      long_description_content_type="text/markdown",
      url="https://github.com/bsaltel/galaxy-py-report",
      packages=packages,
      license="GPL",
      python_requires=">=3.10"
     )
