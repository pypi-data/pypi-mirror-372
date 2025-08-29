#
# Copyright © 2022-2024 University of Strasbourg. All Rights Reserved.
# Copyright © 2032-2024 QPerfect. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'quantanium.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from .Quantanium import Quantanium
__version__ = "1.11.0"
__all__ = ["Quantanium"]
