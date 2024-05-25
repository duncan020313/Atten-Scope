import torch as t
from torch import Tensor


def nullspace(A: Tensor) -> Tensor:
    """
    Compute the null space of a matrix A.
    """
    A32 = A.float()
    try:
        ut, st, vht = t.Tensor.svd(A32, some=False, compute_uv=True)
    except:
        return None
    vht = vht.T
    Mt, Nt = ut.shape[0], vht.shape[1]
    rcondt = t.finfo(st.dtype).eps * max(Mt, Nt)
    tolt = t.max(st) * rcondt
    numt = t.sum(st > tolt, dtype=int)
    nullspace = vht[numt:, :].T.conj()
    return nullspace


def get_projection_matrix(A: Tensor) -> Tensor:
    """
    Compute the projection matrix onto the column space of A.
    """
    return A @ t.linalg.pinv(A.T @ A) @ A.T  # P = A (A^T A)^-1 A^T


def get_nullspace_projection_matrix(matrix: Tensor) -> Tensor:
    """
    Compute the projection matrix onto the null space of a matrix.
    """
    nullspace = nullspace(matrix.T)  # nullspace.T @ matrix = 0
    if nullspace is None:
        return None
    return get_projection_matrix(nullspace)  # project onto columnspace of nullspace


def get_effective_attention(
    attn: Tensor,
    value: Tensor,
) -> Tensor:
    """
    Compute the effective attention for a given layer and head.
    """
    null_projector_value = get_nullspace_projection_matrix(value)
    if null_projector_value is None:
        return t.zeros(attn.size())
    null_attn = attn @ null_projector_value.T  # AP^T = A_null
    null_attn = t.tril(null_attn)  # lower triangular
    effective_attn = attn - null_attn
    effective_attn = t.clamp(effective_attn, min=0.0)  # Remove negative values
    return effective_attn


def apply_value_norm_to_attention(
    attn: Tensor,
    value: Tensor,
) -> Tensor:
    """
    attn: = tok_len x tok_len
    value: = tok_len x dim
    """
    norm_value = t.norm(value, dim=1)  # tok_len
    norm_applied_attn = attn * norm_value.unsqueeze(0)
    normalized_attn = norm_applied_attn / t.sum(norm_applied_attn, dim=1).unsqueeze(1)
    return normalized_attn
