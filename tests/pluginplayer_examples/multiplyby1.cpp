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
Multiplier for One's Multiply Nester
---------------------------------

This module computes the inner multiplication of multiplying by 1:
)";

namespace pluginplayer_examples {

MODULE_CTOR(MultiplyBy1) {
    description(module_desc);
    satisfies_property_type<Multiplier>();
}

MODULE_RUN(MultiplyBy1) {
    const auto& [r] = Multiplier::unwrap_inputs(inputs);

    int rt  = r;
    auto rv = results();
    return Multiplier::wrap_results(rv, rt);
}

} // namespace pluginplayer_examples
