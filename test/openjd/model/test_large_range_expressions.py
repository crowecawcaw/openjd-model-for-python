# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import pytest

from openjd.model import (
    ParameterValueType,
    StepParameterSpaceIterator,
)
from openjd.model.v2023_09 import (
    RangeExpressionTaskParameterDefinition as RangeExpressionTaskParameterDefinition_2023_09,
    StepParameterSpace as StepParameterSpace_2023_09,
    TaskChunksDefinition as TaskChunksDefinition_2023_09,
    TaskChunksRangeConstraint as TaskChunksRangeConstraint_2023_09,
)

LARGE_RANGE = "1-999999999"


class TestLargeRangeExpressions:
    @pytest.mark.timeout(5)
    def test_non_chunked_large_range_is_lazy(self):
        """A massive range expression without chunking should be O(1) —
        IntRangeExpr is lazy and never materializes the full list."""
        space = StepParameterSpace_2023_09(
            taskParameterDefinitions={
                "Frame": RangeExpressionTaskParameterDefinition_2023_09(
                    type=ParameterValueType.INT, range=LARGE_RANGE
                ),
            }
        )
        it = StepParameterSpaceIterator(space=space)
        assert len(it) == 999999999
        params = it[0]
        assert params["Frame"].value == "1"
        params = it[999999998]
        assert params["Frame"].value == "999999999"

    @pytest.mark.timeout(5)
    def test_chunked_large_range_materializes(self):
        """Chunking a massive range expression materializes the full list,
        which exhausts time/memory. This documents the known limitation."""
        space = StepParameterSpace_2023_09(
            taskParameterDefinitions={
                "Frame": RangeExpressionTaskParameterDefinition_2023_09(
                    type=ParameterValueType.CHUNK_INT,
                    range=LARGE_RANGE,
                    chunks=TaskChunksDefinition_2023_09(
                        defaultTaskCount=1000,
                        rangeConstraint=TaskChunksRangeConstraint_2023_09.CONTIGUOUS,
                    ),
                ),
            }
        )
        StepParameterSpaceIterator(space=space)
