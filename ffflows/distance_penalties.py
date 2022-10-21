import torch
from torch import nn


class BasePenalty(nn.Module):

    def __init__(self, weight):
        super(BasePenalty, self).__init__()
        self.register_buffer('weight', torch.Tensor(weight))

    def forward(self, inputs, outputs):
        return self.weight * 0


class LOnePenalty(BasePenalty):

    def forward(self, inputs, outputs):
        return self.weight * (outputs - inputs)
