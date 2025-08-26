import pytest
import torch
from grassmann_tensor import GrassmannTensor


@pytest.mark.parametrize("arrow", [(i, j, k, l, m) for i in [False, True] for j in [False, True] for k in [False, True] for l in [False, True] for m in [False, True]])
@pytest.mark.parametrize("plan_range", [(i, j) for i in range(5) for j in range(5) if j > i])
def test_reshape_consistency(arrow: tuple[bool, ...], plan_range: tuple[int, int]) -> None:
    l, h = plan_range
    if not all(arrow[l:h]) and any(arrow[l:h]):
        pytest.skip("Invalid reshape plan for the given arrow configuration.")
    edge = (2, 2)
    a = GrassmannTensor(arrow, (edge, edge, edge, edge, edge), torch.randn([4, 4, 4, 4, 4]))
    plan = tuple([-1] * l + [4**(h - l)] + [-1] * (5 - h))
    b = a.reshape(plan)
    c = b.reshape(a.edges)
    assert torch.allclose(a.tensor, c.tensor)
