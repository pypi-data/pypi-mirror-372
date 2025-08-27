#    Copyright 2025 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import typing as tp
import importlib_metadata


EVENT_PAYLOADS_GROUP = "gcl_sdk_event_payloads"


def load_event_payload_map() -> dict:
    event_payload_map = {
        ep.name: ep.load()
        for ep in importlib_metadata.entry_points(
            group=EVENT_PAYLOADS_GROUP,
        )
    }
    return event_payload_map


def load_from_entry_point(group: str, name: str) -> tp.Any:
    """Load class from entry points."""
    for ep in importlib_metadata.entry_points(group=group):
        if ep.name == name:
            return ep.load()

    raise RuntimeError(f"No class '{name}' found in entry points {group}")
