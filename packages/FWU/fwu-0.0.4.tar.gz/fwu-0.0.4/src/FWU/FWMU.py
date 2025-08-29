import torch
import math

class FWMU(torch.nn.Module):
    def __init__(self,in_features,out_features,bias=True,gain=1,**kwargs):
        super(FWMU, self).__init__()
        self.LinearP=torch.nn.Linear(in_features,out_features,bias=True,**kwargs)
        self.LinearN=torch.nn.Linear(in_features,out_features,bias=True,**kwargs)
        
        if bias:
            self.bias=torch.nn.Parameter(torch.zeros((out_features),**kwargs),requires_grad=True)
        else:
            self.bias=None
         
        with torch.no_grad():
            torch.nn.init.orthogonal_(self.LinearP.weight,gain=gain)
            torch.nn.init.orthogonal_(self.LinearN.weight,gain=gain)
            torch.nn.init.normal_(self.LinearP.bias)
            self.LinearP.bias.data.sign_()
            torch.nn.init.normal_(self.LinearN.bias)
            self.LinearN.bias.data.sign_()
        
    def forward(self,input):
        inputP=input.clamp(min=0)
        inputN=input.clamp(max=0)   
        output=self.LinearP(inputP)*self.LinearN(inputN)-self.LinearP.bias*self.LinearN.bias
         
        if self.bias is not None:
            output=output+self.bias
        
        return output
    
