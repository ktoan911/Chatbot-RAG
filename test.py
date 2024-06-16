import bitsandbytes as bnb
import torch

# Create a simple tensor and move it to GPU if available
tensor = torch.randn(10).cuda()

# Use bitsandbytes operations
quantized_tensor = bnb.nn.quantization.quantize_fp8(tensor)
print(quantized_tensor)
