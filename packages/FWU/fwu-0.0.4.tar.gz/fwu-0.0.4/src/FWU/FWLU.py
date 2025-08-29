import torch
import math

class FWLU(torch.nn.Module):
    def __init__(self,in_features,out_features,bias=True,gain=1,**kwargs):
        super(FWLU, self).__init__()
        self.LinearP=torch.nn.Linear(in_features,out_features,bias=False,**kwargs)
        self.LinearN=torch.nn.Linear(in_features,out_features,bias=False,**kwargs)
        
        if bias:
            self.bias=torch.nn.Parameter(torch.zeros((out_features),**kwargs),requires_grad=True)
        else:
            self.bias=None
 
        with torch.no_grad():
            torch.nn.init.orthogonal_(self.LinearP.weight,gain=gain)
            torch.nn.init.orthogonal_(self.LinearN.weight,gain=gain)
        
    def forward(self,input):
        inputP=input.clamp(min=0)
        inputN=input.clamp(max=0)   
        output=self.LinearP(inputP)+self.LinearN(inputN)
            
        if self.bias is not None:
            output=output+self.bias
        
        return output
  


