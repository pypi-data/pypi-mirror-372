import torch
import math
try:
    from .transOrthogonal_ import transOrthogonal_
except ImportError:
    from transOrthogonal_ import transOrthogonal_

class FWMU2DT(torch.nn.Module):
    def __init__(self,in_channels,out_channels,kernel_size,stride=1,padding=0,output_padding=0,dilation=1,groups=1,padding_mode='zeros',bias=True,gain=1,kernel_size_N=None,stride_N=None,padding_N=None,output_padding_N=None,dilation_N=None,groups_N=None,padding_mode_N=None,gain_N=None,**kwargs):
        super(FWMU2DT, self).__init__()
        if kernel_size_N is None:
            kernel_size_N=kernel_size
        if stride_N is None:
            stride_N=stride
        if padding_N is None:
            padding_N=padding
        if output_padding_N is None:
            output_padding_N=output_padding
        if dilation_N is None:
            dilation_N=dilation
        if groups_N is None:
            groups_N=groups
        if padding_mode_N is None:
            padding_mode_N=padding_mode
        if gain_N is None:
            gain_N=gain
            
        self.ConvP=torch.nn.ConvTranspose2d(in_channels,out_channels,kernel_size,stride=stride,padding=padding,output_padding=output_padding,dilation=dilation,groups=groups,padding_mode=padding_mode,bias=True,**kwargs)
        self.ConvN=torch.nn.ConvTranspose2d(in_channels,out_channels,kernel_size_N,stride=stride_N,padding=padding_N,output_padding=output_padding_N,dilation=dilation_N,groups=groups_N,padding_mode=padding_mode_N,bias=True,**kwargs)
        
        if bias:
            self.bias=torch.nn.Parameter(torch.zeros((out_channels,1,1),**kwargs),requires_grad=True)
        else:
            self.bias=None

        g=math.sqrt(math.sqrt(1+gain**2)-1)
        g_N=math.sqrt(math.sqrt(1+gain_N**2)-1)
        with torch.no_grad():
            transOrthogonal_(self.ConvP.weight,gain=g)
            transOrthogonal_(self.ConvN.weight,gain=g_N)
            torch.nn.init.normal_(self.ConvP.bias)
            self.ConvP.bias.data.sign_()
            torch.nn.init.normal_(self.ConvN.bias)
            self.ConvN.bias.data.sign_()
            
    def forward(self,input):
        inputP=input.clamp(min=0)
        inputN=input.clamp(max=0)   
        output=self.ConvP(inputP)*self.ConvN(inputN)-(self.ConvP.bias*self.ConvN.bias).unsqueeze(-1).unsqueeze(-1)
            
        if self.bias is not None:
            output=output+self.bias
        
        return output

  
