import sys
import torch

def check_gpu():
    cuda_available = torch.cuda.is_available()
    pytorch_version = torch.__version__
    cuda_version = torch.version.cuda if cuda_available else "N/A"
    
    print("=" * 50)
    print("ANIME REALITY AI - GPU & ENVIRONMENT DIAGNOSTIC")
    print("=" * 50)
    print(f"PyTorch version: {pytorch_version}")
    print(f"CUDA version:    {cuda_version}")
    print(f"CUDA available:  {cuda_available}")
    
    if cuda_available:
        device_count = torch.cuda.device_count()
        print(f"Device Count:    {device_count}")
        for i in range(device_count):
            gpu_name = torch.cuda.get_device_name(i)
            total_mem = torch.cuda.get_device_properties(i).total_memory / (1024 ** 3)
            free_mem, _ = torch.cuda.mem_get_info(i)
            free_mem_gb = free_mem / (1024 ** 3)
            print(f"GPU [{i}]:        {gpu_name}")
            print(f"VRAM Total:      {total_mem:.2f} GB")
            print(f"VRAM Free:       {free_mem_gb:.2f} GB")
            
            # Simple tensor allocation test on GPU
            test_tensor = torch.zeros((100, 100), device=f"cuda:{i}")
            print(f"Tensor Test:     SUCCESS (allocated on {test_tensor.device})")
    else:
        print("WARNING: CUDA is not available. PyTorch is running on CPU.")
    print("=" * 50)

if __name__ == "__main__":
    check_gpu()
