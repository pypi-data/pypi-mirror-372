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
        torch::Tensor Filter(torch::Tensor in, int64_t topK, double m_lowScoreThresh)
        {
            return in;
        }
        static auto registry =
            torch::RegisterOperators("custom_ops::Filter", &Filter);
        """

torch.utils.cpp_extension.load_inline(
    name='Filter',
    cpp_sources=op_source,
    is_python_module=False,
    verbose=True,
    )

@parse_args("v", "i", "f")
def symbolic_filter(g, self, topK, conf_thres):
    return g.op('custom_ops::Filter', self, topK_i=topK, low_score_thresh_f=conf_thres)
from torch.onnx import register_custom_op_symbolic
register_custom_op_symbolic('custom_ops::Filter', symbolic_filter, 12)

class Filter(torch.nn.Module):
    def __init__(self, topK, conf_thres):
        super(Filter, self).__init__()
        self.topK = topK
        self.conf_thres = conf_thres

    def forward(self, x):
        return torch.ops.custom_ops.Filter(x, self.topK, self.conf_thres)