import torch

def transOrthogonal_(weight: torch.Tensor, gain: float = 1):
    tmp = torch.empty_like(weight.transpose(0,1),layout=weight.layout,memory_format=torch.contiguous_format)
    torch.nn.init.orthogonal_(tmp, gain)
    tmp.transpose_(0,1)
    weight.data.copy_(tmp)
  