/*
 * Copyright 2022 NWChemEx-Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "modules.hpp"
#include "multiplier.hpp"
#include <numeric> // for std::inner_product

static constexpr auto module_desc = R"(
Multiplier for a submodule multiplier
---------------------------------

This module computes the inner multiplication of multiplying by the input and its corresponding submodules:
)";

namespace pluginplayer_examples {

MODULE_CTOR(MultiplyBySubmods) {
    description(module_desc);
    satisfies_property_type<Multiplier>();
    add_submodule<Multiplier>("internal multiplier 1")
      .set_description("Used to multiply a value by another");
    add_submodule<Multiplier>("internal multiplier 2")
      .set_description("Used to multiply a value by another");
}

MODULE_RUN(MultiplyBySubmods) {
    const auto& [input] = Multiplier::unwrap_inputs(inputs);

    int rt  = input;
    int rd      = submods.at("internal multiplier 1").run_as<Multiplier>(rt);
    int rs      = submods.at("internal multiplier 2").run_as<Multiplier>(rt);
    auto rv = results();
    return Multiplier::wrap_results(rv, rd * rs);
}

} // namespace pluginplayer_examples
