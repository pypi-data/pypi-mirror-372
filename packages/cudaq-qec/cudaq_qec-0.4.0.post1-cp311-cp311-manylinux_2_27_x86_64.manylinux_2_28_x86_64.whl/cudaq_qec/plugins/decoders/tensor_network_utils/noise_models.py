# ============================================================================ #
# Copyright (c) 2025 NVIDIA Corporation & Affiliates.                          #
# All rights reserved.                                                         #
#                                                                              #
# This source code and the accompanying materials are made available under     #
# the terms of the Apache License 2.0 which accompanies this distribution.     #
# ============================================================================ #
from typing import Any, Optional, Union
import numpy as np
from quimb import oset
from quimb.tensor import TensorNetwork, Tensor


def factorized_noise_model(
        error_indices: list[str],
        error_probabilities: Union[list[float], np.ndarray],
        tensors_tags: Optional[list[str]] = None) -> TensorNetwork:
    """
    Construct a factorized (product state) noise model as a tensor network.

    Args:
        error_indices (list[str]): list of error index names.
        error_probabilities (Union[list[float], np.ndarray]): list or array of error probabilities for each error index.
        tensors_tags (Optional[list[str]], optional): list of tags for each tensor. If None, default tags are used.

    Returns:
        TensorNetwork: The tensor network representing the factorized noise model.
    """
    assert len(error_indices) == len(error_probabilities), \
        "Length of error_indices and error_probabilities must match."
    if isinstance(error_probabilities, np.ndarray):
        assert error_probabilities.ndim == 1 and len(error_probabilities) == len(
            error_indices
        ), "error_probabilities must be a 1D array with length matching error_indices."
    elif isinstance(error_probabilities, list):
        assert all(isinstance(p, (float, int)) for p in error_probabilities), \
            "error_probabilities must be a list of floats or ints."
    else:
        raise TypeError("error_probabilities must be a list or numpy array.")
    assert all(p >= 0 and p <= 1 for p in error_probabilities), \
        "All error probabilities must be in the range [0, 1]."
    assert all(isinstance(ind, str) for ind in error_indices), \
        "All error indices must be strings."
    tensors = []

    if tensors_tags is None:
        tensors_tags = ["NOISE"] * len(error_indices)

    for ei, eprob, etag in zip(error_indices, error_probabilities,
                               tensors_tags):
        tensors.append(
            Tensor(
                data=np.array([1.0 - eprob, eprob]),
                inds=(ei,),
                tags=oset([etag]),
            ))
    return TensorNetwork(tensors)


def error_pairs_noise_model(
        error_index_pairs: list[tuple[str, str]],
        error_probabilities: list[np.ndarray],
        tensors_tags: Optional[list[str]] = None) -> TensorNetwork:
    """
    Construct a noise model as a tensor network for correlated error pairs.

    Args:
        error_index_pairs (list[tuple[str, str]]): list of pairs of error index names.
        error_probabilities (list[np.ndarray]): list of 2x2 probability matrices for each error pair.
        tensors_tags (Optional[list[str]], optional): list of tags for each tensor. If None, default tags are used.

    Returns:
        TensorNetwork: The tensor network representing the error pairs noise model.
    """
    assert len(error_index_pairs) == len(error_probabilities), \
        "Length of error_index_pairs and error_probabilities must match."
    if isinstance(error_probabilities, np.ndarray):
        assert (error_probabilities.ndim == 2 and
                error_probabilities.shape[1] == 2 and
                error_probabilities.shape[0] == len(error_index_pairs)), \
            "error_probabilities must be a 2D array with shape (N, 2) where N is the number of error pairs."
    elif isinstance(error_probabilities, list):
        assert all(isinstance(p, np.ndarray) and p.ndim == 2 and p.shape == (2, 2)
                   for p in error_probabilities), \
            "error_probabilities must be a list of 2x2 numpy arrays."
    else:
        raise TypeError("error_probabilities must be a list or numpy array.")
    assert all((p >=0).all() and (p <= 1).all() for p in error_probabilities), \
        "All error probabilities must be in the range [0, 1]."
    tensors = []

    if tensors_tags is None:
        tensors_tags = ["NOISE"] * len(error_index_pairs)

    for ei, etensors, etag in zip(error_index_pairs, error_probabilities,
                                  tensors_tags):
        tensors.append(Tensor(
            data=etensors,
            inds=ei,
            tags=oset([etag]),
        ))
    return TensorNetwork(tensors)
