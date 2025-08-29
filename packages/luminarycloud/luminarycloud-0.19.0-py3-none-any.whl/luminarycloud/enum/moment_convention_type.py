# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.output import output_pb2 as outputpb


class MomentConventionType(IntEnum):
    """
    Whether the body frame or stability frame is used for pitch, roll and yaw moment calculations.

    Attributes
    ----------
    BODY_FRAME
    STABILITY_FRAME
    """

    UNSPECIFIED = outputpb.INVALID_MOMENT_CONVENTION_TYPE

    BODY_FRAME = outputpb.MOMENT_CONVENTION_BODY_FRAME
    STABILITY_FRAME = outputpb.MOMENT_CONVENTION_STABILITY_FRAME
