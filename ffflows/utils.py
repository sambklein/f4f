import torch


def set_trainable(model, trainable=True):
    for param in model.parameters():
        param.requires_grad = trainable
    model.eval()


def shuffle_tensor(data):
    mx = torch.randperm(len(data), device=torch.device('cpu'))
    return data[mx]
