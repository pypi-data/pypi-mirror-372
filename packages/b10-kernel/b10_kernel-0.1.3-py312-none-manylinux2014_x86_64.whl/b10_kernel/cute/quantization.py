from typing import Tuple

import cuda.bindings.driver as cuda
import cutlass
import cutlass.cute as cute
from cutlass.cute.runtime import from_dlpack

import torch

torch2cute_dtype_map = {
    torch.float16: cutlass.Float16,
    torch.bfloat16: cutlass.BFloat16,
    torch.float32: cutlass.Float32,
}

FP8_E4M3_MAX = 448.0
FP8_E4M3_MIN = -448.0


class PerTokenGroupQuantFP8:
    def __init__(self, dtype: cutlass.Numeric, N: int, group_size: int = 128):
        assert N % group_size == 0, (
            f"N ({N}) must be divisible by group_size ({group_size})"
        )
        self.dtype = dtype
        self.N = N
        self.group_size = group_size
        self.groups_per_row = N // group_size

    @cute.jit
    def __call__(
        self,
        mX: cute.Tensor,
        mQ: cute.Tensor,
        mS: cute.Tensor,
        stream: cuda.CUstream,
        eps: cute.Float32 = 1e-10,
    ):
        mS_shape = (mX.shape[0], self.groups_per_row)
        mS_stride = (mS.stride[0], 1)
        mS = cute.make_tensor(mS.iterator, cute.make_layout(mS_shape, stride=mS_stride))

        self.kernel(mX, mQ, mS, eps).launch(
            grid=[mX.shape[0], 1, 1],
            block=[256, 1, 1],
            smem=4096,
            stream=stream,
        )

    @cute.kernel
    def kernel(
        self,
        mX: cute.Tensor,
        mQ: cute.Tensor,
        mS: cute.Tensor,
        eps: cute.Float32,
    ):
        tidx, _, _ = cute.arch.thread_idx()
        bidx, _, _ = cute.arch.block_idx()

        row_idx = bidx

        if row_idx < mX.shape[0]:
            elements_per_thread = cute.ceil_div(self.N, 256)
            start_col = tidx * elements_per_thread
            end_col = min(start_col + elements_per_thread, self.N)

            group_max_0 = cute.Float32(0.0)
            group_max_1 = cute.Float32(0.0)

            for col in range(start_col, end_col):
                x_val = mX[row_idx, col].to(cute.Float32)
                group_idx = col // self.group_size
                abs_val = x_val if x_val >= 0.0 else -x_val

                if group_idx == 0:
                    group_max_0 = abs_val if abs_val > group_max_0 else group_max_0
                elif group_idx == 1:
                    group_max_1 = abs_val if abs_val > group_max_1 else group_max_1

            for col in range(start_col, end_col):
                x_val = mX[row_idx, col].to(cute.Float32)
                group_idx = col // self.group_size

                group_absmax = cute.Float32(eps)
                if group_idx == 0:
                    group_absmax = group_max_0 if group_max_0 > eps else eps
                elif group_idx == 1:
                    group_absmax = group_max_1 if group_max_1 > eps else eps

                scale = group_absmax / cutlass.const_expr(FP8_E4M3_MAX)
                scaled_val = x_val / scale
                clamped_val = (
                    scaled_val
                    if scaled_val >= cutlass.const_expr(FP8_E4M3_MIN)
                    else cutlass.const_expr(FP8_E4M3_MIN)
                )
                clamped_val = (
                    clamped_val
                    if clamped_val <= cutlass.const_expr(FP8_E4M3_MAX)
                    else cutlass.const_expr(FP8_E4M3_MAX)
                )

                # This preserves the FP8 E4M3FN value range in uint8 storage
                mQ[row_idx, col] = cutlass.Uint8(clamped_val)

            if tidx == 0 and self.groups_per_row >= 1:
                group_absmax = group_max_0 if group_max_0 > eps else eps
                scale = group_absmax / cutlass.const_expr(FP8_E4M3_MAX)
                mS[row_idx, 0] = scale

                if self.groups_per_row >= 2:
                    group_absmax = group_max_1 if group_max_1 > eps else eps
                    scale = group_absmax / cutlass.const_expr(FP8_E4M3_MAX)
                    mS[row_idx, 1] = scale


def per_token_group_quant_fp8(
    x: torch.Tensor,
    group_size: int = 128,
    eps: float = 1e-10,
    flatten_output: bool = False,
) -> Tuple[torch.Tensor, torch.Tensor]:
    original_shape = x.shape
    assert original_shape[-1] % group_size == 0, (
        "Last dimension must be divisible by group_size"
    )

    if x.ndim == 2:
        x_2d = x
    else:
        x_2d = x.view(-1, x.shape[-1])

    M, N = x_2d.shape
    groups_per_row = N // group_size
    device = x.device

    x_q_uint8 = torch.empty(M, N, device=device, dtype=torch.uint8)
    x_s = torch.empty(M, groups_per_row, device=device, dtype=torch.float32)

    dtype = torch2cute_dtype_map[x.dtype]
    x_tensor = from_dlpack(x_2d.detach(), assumed_align=16)
    x_q_tensor = from_dlpack(x_q_uint8.detach(), assumed_align=16)
    x_s_tensor = from_dlpack(x_s.detach(), assumed_align=16)

    current_stream = cuda.CUstream(torch.cuda.current_stream().cuda_stream)

    op = PerTokenGroupQuantFP8(dtype, N, group_size)
    kernel = cute.compile(op, x_tensor, x_q_tensor, x_s_tensor, current_stream)
    kernel(x_tensor, x_q_tensor, x_s_tensor, current_stream, eps)

    x_q_fp8 = x_q_uint8.view(torch.float8_e4m3fn)

    if flatten_output or x.ndim == 2:
        return x_q_fp8, x_s
    else:
        groups_shape = original_shape[:-1] + (groups_per_row,)
        return x_q_fp8.view(original_shape), x_s.view(groups_shape)


if __name__ == "__main__":
    from b10_kernel.triton.quantization import (
        per_token_group_quant_fp8 as triton_quant_fp8,
    )

    x = torch.randn(64, 512, dtype=torch.float16, device="cuda")

    x_q_cute, x_s_cute = per_token_group_quant_fp8(x, group_size=128)
    x_q_triton, x_s_triton = triton_quant_fp8(x, group_size=128)

    print(f"Shapes: q={x_q_cute.shape}, s={x_s_cute.shape}")
    print(f"CuTe scales: min={x_s_cute.min():.6f}, max={x_s_cute.max():.6f}")
    print(f"Triton scales: min={x_s_triton.min():.6f}, max={x_s_triton.max():.6f}")
    print("OK")
