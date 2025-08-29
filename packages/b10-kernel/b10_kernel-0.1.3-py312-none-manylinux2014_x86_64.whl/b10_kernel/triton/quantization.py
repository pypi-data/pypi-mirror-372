import triton
import triton.language as tl
import torch
from typing import Tuple


@triton.jit
def _per_token_group_quant_fp8(
    y_ptr,
    y_q_ptr,
    y_s_ptr,
    B,
    T,
    K,
    stride_b,
    stride_t,
    stride_k,
    stride_q_b,
    stride_q_t,
    stride_q_k,
    total_groups,
    groups_per_row,
    N: tl.constexpr,
    eps: tl.constexpr,
    fp8_min: tl.constexpr,
    fp8_max: tl.constexpr,
    BLOCK: tl.constexpr,
):
    pid = tl.program_id(0)
    num_blocks = tl.num_programs(0)

    groups_per_block = (total_groups + num_blocks - 1) // num_blocks
    start_group = pid * groups_per_block
    end_group = tl.minimum(start_group + groups_per_block, total_groups)

    for g_id in range(start_group, end_group):
        row = g_id // groups_per_row
        g_in_row = g_id % groups_per_row
        b = row // T
        t = row % T

        cols = tl.arange(0, BLOCK)
        mask = cols < N

        # Input offsets (using input strides)
        input_base = b * stride_b + t * stride_t + (g_in_row * N) * stride_k
        input_offs = input_base + cols * stride_k

        # Output offsets (using output strides)
        output_base = b * stride_q_b + t * stride_q_t + (g_in_row * N) * stride_q_k
        output_offs = output_base + cols * stride_q_k

        y = tl.load(y_ptr + input_offs, mask=mask, other=0.0)
        _absmax = tl.maximum(tl.max(tl.abs(y)), eps)
        y_s = _absmax.to(tl.float32) / fp8_max
        y_s_inv = 1.0 / y_s
        y_q = tl.clamp(y * y_s_inv, fp8_min, fp8_max).to(y_q_ptr.dtype.element_ty)

        tl.store(y_q_ptr + output_offs, y_q, mask=mask)
        tl.store(y_s_ptr + g_id, y_s)


def per_token_group_quant_fp8(
    x: torch.Tensor,
    group_size: int,
    eps: float = 1e-10,
    flatten_output: bool = False,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Function to perform per-token-group quantization on an input tensor `x`.

    It converts the tensor values into signed float8 values and returns the
    quantized tensor along with the scaling factor used for quantization.

    Args:
        x: The input tensor with ndim >= 2.
        group_size: The group size used for quantization.
        eps: The minimum to avoid dividing zero.
        flatten_output: If True, flatten both x_q and x_s outputs. For 3D input (B, T, K),
                       output shapes become (B*T, K) and (B*T, groups_per_row) respectively.
                       Output tensors are always contiguous regardless of input stride.

    Returns:
        Tuple[torch.Tensor, torch.Tensor]: The quantized tensor and the scaling factor for quantization.
                                          Both tensors are guaranteed to be contiguous.
    """
    assert x.shape[-1] % group_size == 0, "K must be divisible by group_size"

    if x.ndim == 2:
        B, T, K = 1, x.shape[0], x.shape[1]
        stride_b = 0
        stride_t, stride_k = x.stride()
    else:
        assert x.ndim == 3
        B, T, K = x.shape
        stride_b, stride_t, stride_k = x.stride()

    FP8_DTYPE = torch.float8_e4m3fn
    fp8_info = torch.finfo(FP8_DTYPE)
    fp8_max, fp8_min = fp8_info.max, fp8_info.min

    groups_per_row = K // group_size
    total_groups = (B * T) * groups_per_row

    if flatten_output or x.ndim == 2:
        x_q = torch.empty((B * T, K), device=x.device, dtype=FP8_DTYPE)
        x_s = torch.empty((B * T, groups_per_row), device=x.device, dtype=torch.float32)
    else:
        x_q = torch.empty((B, T, K), device=x.device, dtype=FP8_DTYPE)
        x_s = torch.empty((B, T, groups_per_row), device=x.device, dtype=torch.float32)

    N = group_size
    BLOCK = triton.next_power_of_2(N)
    num_warps = min(max(BLOCK // 128, 1), 8)
    num_stages = 2

    sm_count = torch.cuda.get_device_properties(x.device).multi_processor_count
    grid_size = min(32 * sm_count, total_groups)

    if flatten_output or x.ndim == 2:
        x_q_stride_b = T * K
        x_q_stride_t = K
        x_q_stride_k = 1
    else:
        x_q_stride_b, x_q_stride_t, x_q_stride_k = x_q.stride()

    _per_token_group_quant_fp8[(grid_size,)](
        x,
        x_q,
        x_s,
        B,
        T,
        K,
        stride_b,
        stride_t,
        stride_k,
        x_q_stride_b,
        x_q_stride_t,
        x_q_stride_k,
        total_groups,
        groups_per_row,
        N,
        eps,
        fp8_min=fp8_min,
        fp8_max=fp8_max,
        BLOCK=BLOCK,
        num_warps=num_warps,
        num_stages=num_stages,
    )
    return x_q, x_s
