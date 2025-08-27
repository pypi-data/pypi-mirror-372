# Copyright (C) 2022 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

from enum import Enum


class AnnotationState(Enum):
    """
    Enum representing the different annotation statuses for media items within an
    Intel® Geti™ project.
    """

    TO_REVISIT = "to_revisit"
    ANNOTATED = "annotated"
    PARTIALLY_ANNOTATED = "partially_annotated"
    NONE = "none"

    def __str__(self):
        """
        Return the string representation of the AnnotationState instance.
        """
        return self.value
