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

#include "multiplier.hpp"
#include "modules.hpp"
#include <numeric> // for std::inner_product

static constexpr auto module_desc = R"(
Multiplier for Two's Multiply Nester
---------------------------------

This module computes the inner multiplication of multiplying by 2:
)";

namespace pluginplayer_examples {

MODULE_CTOR(MultiplyBy2) {
    description(module_desc);
    satisfies_property_type<Multiplier>();
    add_submodule<Multiplier>("internal multiplier")
      .set_description(
        "Used to multiply a value by another");
}

MODULE_RUN(MultiplyBy2) {
    const int& input = std::get<0>(Multiplier::unwrap_inputs(inputs));
    int r = input;

    int rt = submods.at("internal multiplier").run_as<Multiplier>(input) * 2;
    auto rv = results();
    return Multiplier::wrap_results(rv, rt);
}

} // namespace pluginplay_examples
