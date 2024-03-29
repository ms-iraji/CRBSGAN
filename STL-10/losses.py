# Copyright (c) 2018, Curious AI Ltd. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution-NonCommercial
# 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to
# Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

"""Custom loss functions"""

import torch
from torch.nn import functional as F
from torch.autograd import Variable


def softmax_mse_loss(input_logits, target_logits):
    """Takes softmax on both sides and returns MSE loss

    Note:
    - Returns the sum over all examples. Divide by the batch size afterwards
      if you want the mean.
    - Sends gradients to inputs but not the targets.
    """
    assert input_logits.size() == target_logits.size()
    input_softmax = F.softmax(input_logits, dim=1)
    target_softmax = F.softmax(target_logits, dim=1)
    num_classes = input_logits.size()[1]
    return F.mse_loss(input_softmax, target_softmax, reduction = 'sum') / num_classes
        

def softmax_kl_loss(input_logits, target_logits):
    """Takes softmax on both sides and returns KL divergence

    Note:
    - Returns the sum over all examples. Divide by the batch size afterwards
      if you want the mean.
    - Sends gradients to inputs but not the targets.
    """
    assert input_logits.size() == target_logits.size()
    input_log_softmax = F.log_softmax(input_logits, dim=1)
    target_softmax = F.softmax(target_logits, dim=1)
    return F.kl_div(input_log_softmax, target_softmax, reduction = 'sum')

def nll_loss_neg(y_pred, y_true):  # # #
    out = torch.sum(y_true * y_pred, dim=1)
    return torch.mean(- torch.log((1 - out) + 1e-6))

def softmax_nll_loss(input_logits, target_logits):
    """Takes softmax on both sides and returns KL divergence

    Note:
    - Returns the sum over all examples. Divide by the batch size afterwards
      if you want the mean.
    - Sends gradients to inputs but not the targets.
    """
    assert input_logits.size() == target_logits.size()

    input_logits = torch.max(input_logits, 1)[1]
                
                

    input_logits = input_logits.view(-1, 1)

    input_logits = torch.zeros(input_logits.shape[0], 10).cuda().scatter_(1, input_logits, 1)

    #print(input_logits.shape)



    #input_log_softmax = F.log_softmax(input_logits, dim=1)
    #print(input_log_softmax)

    target_logits = torch.max(target_logits, 1)[1]
                
                

    target_logits = target_logits.view(-1, 1)

    target_logits = torch.zeros(target_logits.shape[0], 10).cuda().scatter_(1, target_logits, 1)


    #target_softmax = F.softmax(target_logits, dim=1)
    
    #print(input_log_softmax)
    #print(target_softmax.shap)

    out = torch.sum(target_logits * input_logits, dim=1)
    return torch.mean(- torch.log((1 - out) + 1e-6)) 
    #return F.nll_loss(input_log_softmax, target_logits)



def softmax_nll_loss2(input_logits, target_logits):
    """Takes softmax on both sides and returns KL divergence

    Note:
    - Returns the sum over all examples. Divide by the batch size afterwards
      if you want the mean.
    - Sends gradients to inputs but not the targets.
    """
    assert input_logits.size() == target_logits.size()
    input_log_softmax = F.log_softmax(input_logits, dim=1)
    #print(input_log_softmax)

    target_softmax = F.softmax(target_logits, dim=1)
    
    #print(input_log_softmax)
    #print(target_softmax.shap)

    out = torch.sum(target_softmax * input_log_softmax, dim=1)
    return torch.mean(- torch.log((1 - out) + 1e-6)) 
    #return F.nll_loss(input_log_softmax, target_logits)


def softmax_nll_loss3(input_logits, target_logits):
    """Takes softmax on both sides and returns KL divergence

    Note:
    - Returns the sum over all examples. Divide by the batch size afterwards
      if you want the mean.
    - Sends gradients to inputs but not the targets.
    """
    assert input_logits.size() == target_logits.size()
    #input_log_softmax = F.log_softmax(input_logits, dim=1)
    #print(input_log_softmax)

    #target_softmax = F.softmax(target_logits, dim=1)
    
    #print(input_log_softmax)
    #print(target_softmax.shap)

    out = torch.sum(target_logits * input_logits, dim=1)
    return torch.mean(- torch.log((1 - out) + 1e-6)) 
    #return F.nll_loss(input_log_softmax, target_logits)







def symmetric_mse_loss(input1, input2):
    """Like F.mse_loss but sends gradients to both directions

    Note:
    - Returns the sum over all examples. Divide by the batch size afterwards
      if you want the mean.
    - Sends gradients to both input1 and input2.
    """
    assert input1.size() == input2.size()
    num_classes = input1.size()[1]
    return torch.sum((input1 - input2)**2) / num_classes
