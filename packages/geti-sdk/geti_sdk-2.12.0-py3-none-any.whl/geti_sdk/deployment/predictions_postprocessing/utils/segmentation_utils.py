# INTEL CONFIDENTIAL
#
# Copyright (C) 2024 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were provided to
# you ("License"). Unless the License provides otherwise, you may not use, modify, copy,
# publish, distribute, disclose or transmit this software or the related documents
# without Intel's prior written permission.
#
# This software and the related documents are provided as is,
# with no express or implied warranties, other than those that are expressly stated
# in the License.
import logging
from copy import copy
from typing import Optional, cast

import cv2
import numpy as np

from geti_sdk.data_models.annotations import Annotation
from geti_sdk.data_models.label import ScoredLabel
from geti_sdk.data_models.shapes import Point, Polygon

logger = logging.getLogger(__name__)

Contour = list[tuple[float, float]]
ContourInternal = Optional[list[tuple[float, float]]]  # noqa: UP045


def get_subcontours(contour: Contour) -> list[Contour]:
    """
    Split contour into sub-contours that do not have self intersections.

    :param contour: the contour to split
    :return: list of sub-contours
    """

    def find_loops(points: ContourInternal) -> list:
        """For each consecutive pair of equivalent rows in the input matrix returns their indices."""
        _, inverse, count = np.unique(points, axis=0, return_inverse=True, return_counts=True)  # type: ignore
        duplicates = np.where(count > 1)[0]
        indices = []
        for x in duplicates:
            y = np.nonzero(inverse == x)[0]
            for i, _ in enumerate(y[:-1]):
                indices.append(y[i : i + 2])
        return indices

    base_contour = cast("ContourInternal", copy(contour))

    # Make sure that contour is closed.
    if not np.array_equal(base_contour[0], base_contour[-1]):  # type: ignore
        base_contour.append(base_contour[0])

    subcontours: list[Contour] = []
    loops = sorted(find_loops(base_contour), key=lambda x: x[0], reverse=True)
    for loop in loops:
        i, j = loop
        subcontour = base_contour[i:j]
        subcontour = [x for x in subcontour if x is not None]
        subcontours.append(cast("Contour", subcontour))
        base_contour[i:j] = [None] * (j - i)

    return [i for i in subcontours if len(i) > 2]


def create_annotation_from_segmentation_map(
    hard_prediction: np.ndarray, soft_prediction: np.ndarray, label_map: dict
) -> list[Annotation]:
    """
    Create polygons from the soft predictions.

    Note: background label will be ignored and not be converted to polygons.

    :param hard_prediction: hard prediction containing the final label index per pixel.
        See function `create_hard_prediction_from_soft_prediction`.
    :param soft_prediction: soft prediction with shape H x W x N_labels,
            where soft_prediction[:, :, 0] is the soft prediction for
            background. If soft_prediction is of H x W shape, it is
            assumed that this soft prediction will be applied for all
            labels.
    :param label_map: dictionary mapping labels to an index. It is assumed
            that the first item in the dictionary corresponds to the
            background label and will therefore be ignored.
    :return: list of annotations with polygons
    """
    # pylint: disable=too-many-locals
    img_class = hard_prediction.swapaxes(0, 1)

    # pylint: disable=too-many-nested-blocks
    annotations: list[Annotation] = []
    for label_index, label in label_map.items():
        # Skip background
        if label_index == 0:
            continue

        # obtain current label soft prediction
        if len(soft_prediction.shape) == 3:
            current_label_soft_prediction = soft_prediction[:, :, label_index]
        else:
            current_label_soft_prediction = soft_prediction

        obj_group = img_class == label_index
        label_index_map = (obj_group.T.astype(int) * 255).astype(np.uint8)

        # Contour retrieval mode CCOMP (Connected components) creates a two-level
        # hierarchy of contours
        contours, hierarchies = cv2.findContours(label_index_map, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

        if hierarchies is not None:
            for contour, hierarchy in zip(contours, hierarchies[0]):
                if len(contour) <= 2 or cv2.contourArea(contour) < 1.0:
                    continue

                if hierarchy[3] == -1:
                    # In this case a contour does not represent a hole
                    _contour = [(point[0][0], point[0][1]) for point in contour]

                    # Split contour into subcontours that do not have self intersections.
                    subcontours = get_subcontours(_contour)
                    for subcontour in subcontours:
                        # compute probability of the shape
                        mask = np.zeros(hard_prediction.shape, dtype=np.uint8)
                        cv2.drawContours(
                            mask,
                            np.asarray([[[x, y]] for x, y in subcontour]),
                            contourIdx=-1,
                            color=1,
                            thickness=-1,
                        )
                        probability = cv2.mean(current_label_soft_prediction, mask)[0]

                        # convert the list of points to a closed polygon
                        points = [Point(x=x, y=y) for x, y in subcontour]
                        polygon = Polygon(points=points)

                        if polygon.area > 0:
                            # Contour is a closed polygon with area > 0
                            annotations.append(
                                Annotation(
                                    shape=polygon,
                                    labels=[ScoredLabel.from_label(label, probability)],
                                    # id=ID(ObjectId()),
                                )
                            )
                        else:
                            # Contour is a closed polygon with area == 0
                            logger.warning(
                                "The geometry of the segmentation map you are converting "
                                "is not fully supported. Polygons with a area of zero "
                                "will be removed.",
                            )
                else:
                    # If contour hierarchy[3] != -1 then contour has a parent and
                    # therefore is a hole
                    # Do not allow holes in segmentation masks to be filled silently,
                    # but trigger warning instead
                    logger.warning(
                        "The geometry of the segmentation map you are converting is "
                        "not fully supported. A hole was found and will be filled.",
                    )
    return annotations
