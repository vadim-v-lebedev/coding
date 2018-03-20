import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from collections import OrderedDict

class Net(nn.Module):
    def __init__(self, in_dim, mid_dim, out_dim, n_layers, bn_mode, use_sigmoid):
        super(Net, self).__init__()
        sizes = [[mid_dim, mid_dim] for _ in range(n_layers)]
        sizes[0][0] = in_dim
        sizes[-1][-1] = out_dim
        if bn_mode == 'no':
            use_bn = [False] * n_layers
        elif bn_mode == 'all':
            use_bn = [True] * n_layers
        elif bn_mode == 'inside':
            use_bn = [True] * (n_layers - 1) + [False]
        else:
            raise ValueError('unknown bn_mode')
        layers = OrderedDict()
        for i in range(n_layers):
            layers['fc%d' % i] = nn.Linear(sizes[i][0], sizes[i][1])
            if use_bn[i]:
                layers['bn%d' % i] = nn.BatchNorm1d(sizes[i][1])
            if i < n_layers - 1:
                layers['relu%d' % i] = nn.ReLU()
        self.use_sigmoid = use_sigmoid
        self.layers = nn.Sequential(layers)
                                                         
    def forward(self, x):
        x = self.layers(x)
        if self.use_sigmoid:
            return 2*F.sigmoid(x) - 1
        else:
            return x

class Channel(nn.Module):
    def __init__(self, p):
        super(Channel, self).__init__()
        self.p = p
        
    def forward(self, x):
        noise = self.p * torch.randn(x.size()).type(type(x.data))
        noise = Variable(noise, requires_grad=False)
        return x + noise