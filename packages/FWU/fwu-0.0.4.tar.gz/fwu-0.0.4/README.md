# FWU
FWU is a series of PyTorch-based neural network units.It has higher information utilization, prevents neuronal necrosis, and eliminates the need to add additionall activation functions.

![image](./FWLU.png)
![image](./FWMU.png)

## 思路说明
ReLU滤除了小于零的输入,虽然高效实现了非线性,但对小于零的输入无梯度回传,导致了神经元坏死.目前有多种模仿ReLU的平滑版激活函数,通过在输入刚小于零时提供显著的反向梯度、在梯度更小时也提供微小的梯度,部分缓解了ReLU中神经元坏死的问题.
FWU系列直接输入的符号将输入分为>0和<0两部分,分别送入两个单元(Linear或Conv或其他),再对两个单元的输出做二元运算(加法或乘法或其他).即提供了非线性,又最大程度上利用信息完全杜绝了神经元坏死.

目前提供了加法(FWLU)和乘法(FWMU)的Linear、Conv1d、Conv2d、和对应转置卷积的实现.无后缀代表Linear,1D、2D后缀代表对应维度的卷积,加T后缀代表转置卷积.

部分参数,如kernel_size、padding可以通过加_N后缀实现对负分支的专门控制.用以对正负分支添加不同的前后偏移或使用不同宽高比的卷积核,可以减少参数量增大感受野.

## Install
```bash
pip install FWU
```

## Use
```python
from FWU import FWLU2DT
...
```
import后直接替代对应的Linear、Conv1d、Conv2d等,并取消与其组合的激活函数(输出层的SoftMax等承担特殊功能的激活函数除外).

## HomePage
<https://github.com/PsycheHalo/FWU/>
