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

#include "load_modules.hpp"
#include "modules.hpp"

namespace pluginplayer_examples {

void load_modules(pluginplay::ModuleManager& mm) {
    mm.add_module<MultiplyBySubmods>("Multiply by Submods");
    mm.add_module<MultiplyBy2>("Multiply by 2");
    mm.add_module<MultiplyBy1>("Multiply by 1");
    mm.change_submod("Multiply by 2", "internal multiplier", "Multiply by 1");
    
}

} // namespace pluginplay_examples