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

"""Agent module.

Agents are responsible for communicating with Q-CTRL APIs to determine a set of tasks to
perform (generally, QPU tasks such as execution of quantum circuits / configuration).
Importantly, to both simplify and ensure the security of the QPU adjacent host that the
agent will run on, the agent must initiate all communications (as opposed to opening a
port on the host).
"""

__all__ = [
    "Agent",
    "AgentSettings",
    "TaskHandler",
]

from boulderopalscaleupsdk.agent.worker import Agent, AgentSettings, TaskHandler
