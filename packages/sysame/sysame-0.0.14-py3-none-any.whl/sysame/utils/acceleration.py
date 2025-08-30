import numpy as np
import cupy as cp
import time
from numba import njit, cuda

# Problem size
N = 1_000_000_000


# CPU: raw numpy
def numpy_sum_squares(x):
    return np.sum(x**2)


# CPU: numba-accelerated
@njit(cache=True)
def numba_sum_squares(x):
    total = 0.0
    for i in range(x.size):
        total += x[i] ** 2
    return total


# GPU: cupy (vectorized)
def cupy_sum_squares(x_gpu):
    return cp.sum(x_gpu**2)


# GPU: Improved CUDA kernel with reduction for sum of squares
@cuda.jit(cache=True)
def numba_cuda_sum_squares(input_arr, output_arr):
    """CUDA kernel that performs both squaring and partial sum in one pass"""
    tid = cuda.threadIdx.x
    bid = cuda.blockIdx.x
    bdim = cuda.blockDim.x

    # Calculate global thread ID
    idx = bid * bdim + tid

    # Shared memory for block-level reduction
    temp = cuda.shared.array(shape=(256), dtype=np.float32)
    temp[tid] = 0.0

    # Each thread squares and adds its elements
    stride = cuda.gridsize(1)
    sum_val = 0.0

    # Grid-stride loop to handle arrays larger than grid
    i = idx
    while i < input_arr.size:
        sum_val += input_arr[i] ** 2
        i += stride

    # Load sum to shared memory
    temp[tid] = sum_val

    # Synchronize threads within the block
    cuda.syncthreads()

    # Perform parallel reduction in shared memory
    s = bdim // 2
    while s > 0:
        if tid < s:
            temp[tid] += temp[tid + s]
        cuda.syncthreads()
        s //= 2

    # Write block sum to global memory
    if tid == 0:
        output_arr[bid] = temp[0]


# Keep original kernel for comparison
@cuda.jit(cache=True)
def numba_cuda_square(input_arr, output_arr):
    idx = cuda.grid(1)
    if idx < input_arr.size:
        output_arr[idx] = input_arr[idx] ** 2


# Modified optimized approach that leverages CuPy's optimized routines
def optimized_numba_cupy(x_gpu):
    # Create output array
    output_gpu = cp.empty_like(x_gpu)

    # Configure grid
    threads_per_block = 256
    blocks = min(65535, (x_gpu.size + threads_per_block - 1) // threads_per_block)

    # Execute kernel (just square calculation)
    numba_cuda_square[blocks, threads_per_block](x_gpu, output_gpu)

    # Use CuPy's highly optimized reduction
    return cp.sum(output_gpu)


def run_all(warmup=True):
    print("Allocating CPU array...")
    x = np.random.rand(N).astype(np.float32)

    # Transfer data to GPU once (outside timing) for fair comparison
    x_gpu = cp.asarray(x)

    # Warm up the GPU and JIT compilation if requested
    if warmup:
        print("Warming up...")
        # Small GPU ops to trigger JIT compilation and warm up GPU
        small_x = cp.random.rand(1000).astype(cp.float32)
        _ = cp.sum(small_x**2)

        # Warm up Numba JIT
        @njit
        def warmup_numba():
            return 1 + 1

        warmup_numba()
        # Warm up CUDA JIT
        small_gpu = cp.ones(1000, dtype=cp.float32)
        small_out = cp.empty_like(small_gpu)
        numba_cuda_square[4, 256](small_gpu, small_out)
        cuda.synchronize()
        print("Warm-up complete.")

    # ---------------------- Raw NumPy
    start = time.time()
    result_np = numpy_sum_squares(x)
    end = time.time()
    np_time = end - start
    print(f"[NumPy] Result: {result_np:.4f}, Time: {np_time:.4f} s")

    # ---------------------- Numba
    start = time.time()
    result_numba = numba_sum_squares(x)
    end = time.time()
    numba_time = end - start
    print(f"[Numba] Result: {result_numba:.4f}, Time: {numba_time:.4f} s")

    # ---------------------- CuPy
    cp.cuda.Device(0).synchronize()  # ensure any previous operations completed
    start = time.time()
    result_cupy = cupy_sum_squares(x_gpu)
    cp.cuda.Device(0).synchronize()  # ensure completion before timing
    end = time.time()
    cupy_time = end - start
    print(f"[CuPy] Result: {result_cupy:.4f}, Time: {cupy_time:.4f} s")

    # ---------------------- Improved Numba + CUDA with parallel reduction
    threads_per_block = 256
    blocks = min(16384, (N + threads_per_block - 1) // threads_per_block)

    # Create output array for block results
    output_gpu = cuda.device_array(blocks, dtype=np.float32)

    cuda.synchronize()  # ensure GPU is ready
    start = time.time()
    # Launch kernel for parallel reduction
    numba_cuda_sum_squares[blocks, threads_per_block](x_gpu, output_gpu)

    # Get final result by summing block results on CPU
    result_blocks = output_gpu.copy_to_host()
    result_combined = np.sum(result_blocks)
    end = time.time()
    improved_time = end - start
    print(
        f"[Improved Numba + CUDA] Result: {result_combined:.4f}, Time: {improved_time:.4f} s"
    )

    # ---------------------- Original method + optimization
    cp.cuda.Device(0).synchronize()
    start = time.time()
    result_optimized = optimized_numba_cupy(x_gpu)
    cp.cuda.Device(0).synchronize()
    end = time.time()
    optimized_time = end - start
    print(
        f"[Optimized Numba + CuPy] Result: {float(result_optimized):.4f}, Time: {optimized_time:.4f} s"
    )

    # Find the fastest method
    methods = {
        "NumPy": np_time,
        "Numba": numba_time,
        "CuPy": cupy_time,
        "Improved Numba + CUDA": improved_time,
        "Optimized Numba + CuPy": optimized_time,
    }
    fastest = min(methods, key=methods.get)
    print(f"\nFastest method: {fastest} ({methods[fastest]:.4f}s)")
    print(f"Speedup vs NumPy: {np_time / methods[fastest]:.2f}x")


if __name__ == "__main__":
    run_all(warmup=True)
