# Copyright 2022 NWChemEx-Project
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

import pluginplay as pp
import pluginplayer_examples as ppe


class MultiplyBy2(pp.ModuleBase):

    def __init__(self):
        pp.ModuleBase.__init__(self)
        self.description("Two's Multiplier")
        self.satisfies_property_type(ppe.Multiplier())
        self.add_submodule(ppe.Multiplier(), "internal multiplier").set_description(
            "Multiplier sub process")

    def run_(self, inputs, submods):
        pt = ppe.Multiplier()
        r = pt.unwrap_inputs(inputs)
        rv = self.results()
        output = submods["internal multiplier"].run_as(ppe.Multiplier(), r) * 2
        return pt.wrap_results(rv, output)
    
class MultiplyBy1(pp.ModuleBase):
    def __init__(self):
        pp.ModuleBase.__init__(self)
        self.description("Multiplies by 1")
        self.satisfies_property_type(ppe.Multiplier())

    def run_(self, inputs, submods):
        pt = ppe.Multiplier()
        r = pt.unwrap_inputs(inputs)
        rv = self.results()
        return pt.wrap_results(rv, r)
