# Copyright 2024 NWChemEx-Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import parallelzone as pz
import pluginplay as pp
import pluginplayer_examples as ppe
import unittest


class TestExampleModules(unittest.TestCase):

    def test_module_loading(self):
        mm = pp.ModuleManager()
        ppe.load_modules(mm)
        self.assertTrue(len(mm.keys()) == 2)

    def test_module1(self):
        mm = pp.ModuleManager()
        ppe.load_modules(mm)
        mult1 = mm.at("Multiply by 1")
        mult_pt = ppe.Multiplier()
        result = mult1.run_as(mult_pt, 3)
        self.assertTrue(result == 3)

    def test_module2(self):
        mm = pp.ModuleManager()
        ppe.load_modules(mm)
        mult2 = mm.at("Multiply by 2")
        mm.change_submod("Multiply by 2", "internal multiplier",
                         "Multiply by 1")
        mult_pt = ppe.Multiplier()
        result = mult2.run_as(mult_pt, 3)
        self.assertTrue(result == 6)


if __name__ == "__main__":
    rv = pz.runtime.RuntimeView()
    unittest.main()
