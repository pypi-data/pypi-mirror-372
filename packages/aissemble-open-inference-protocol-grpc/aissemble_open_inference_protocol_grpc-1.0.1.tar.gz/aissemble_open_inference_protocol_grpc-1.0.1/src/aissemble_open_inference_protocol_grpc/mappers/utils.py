###
# #%L
# aiSSEMBLE::Open Inference Protocol::gRPC
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from typing import Mapping


def merge_infer_parameters(protobuf_map: Mapping, value_dict: Mapping) -> Mapping:
    """
    Merge values from a dictionary into a protobuf map
    :param protobuf_map: the protobuf map to populate
    :param value_dict: dictionary of key-value pairs to merge into the map
    :return: the updated protobuf map
    """
    for key, value in value_dict.items():
        protobuf_map[key].MergeFrom(value)
    return protobuf_map


class MappingException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
