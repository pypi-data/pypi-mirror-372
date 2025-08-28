# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from boulderopalscaleupsdk.common.dtypes import Duration, TimeUnit

# See https://docs.quantum-machines.co/latest/docs/API_references/qua/dsl_main/?h=clock+cycle#qm.qua._dsl.wait
QUA_CLOCK_CYCLE = Duration(4, TimeUnit.NS)
MIN_TIME_OF_FLIGHT = Duration(24, TimeUnit.NS)

QUA_MAX_DELAY = Duration(2**31 - 1, TimeUnit.NS)
