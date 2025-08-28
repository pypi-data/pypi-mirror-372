import unittest
import torch
import torch.utils.cpp_extension

import onnx

import numpy as np
import io
from torch.onnx.symbolic_helper import parse_args
from torch.onnx import register_custom_op_symbolic

op_source = """
        #include <torch/script.h>
        torch::Tensor NMS(torch::Tensor in, int64_t topK, double nmsThresh)
        {
            return in;
        }
        static auto registry =
            torch::RegisterOperators("custom_ops::NMS", &NMS);
        """

torch.utils.cpp_extension.load_inline(
    name='NMS',
    cpp_sources=op_source,
    is_python_module=False,
    verbose=True,
    )

@parse_args("v", "i", "f")
def symbolic_nms(g, self, topK, nmsThresh):
    return g.op('custom_ops::NMS', self, topK_i=topK, nms_thresh_f = nmsThresh)
from torch.onnx import register_custom_op_symbolic
register_custom_op_symbolic('custom_ops::NMS', symbolic_nms, 12)

class NMS(torch.nn.Module):
    def __init__(self, topK,nms_thresh):
        super(NMS, self).__init__()
        self.topK = topK
        self.nms_thresh = nms_thresh

    def forward(self, x):
        return torch.ops.custom_ops.NMS(x, self.topK, self.nms_thresh)