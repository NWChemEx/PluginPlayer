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

#pragma once
#include <pluginplay/pluginplay.hpp>

namespace pluginplayer_examples {
DECLARE_PROPERTY_TYPE(Multiplier);
PROPERTY_TYPE_INPUTS(Multiplier) {
    auto rv = pluginplay::declare_input().add_field<const int&>("r");

    rv.at("r").set_description("The number to be multiplied");
    return rv;
}
PROPERTY_TYPE_RESULTS(Multiplier) {
    return pluginplay::declare_result().add_field<int>("Multiplied value");
}

} // namespace pluginplayer_examples
