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
        torch::Tensor Sort(torch::Tensor in, int64_t topK, int64_t isMultiSort, int64_t classNum)
        {
            return in;
        }
        static auto registry =
            torch::RegisterOperators("custom_ops::Sort", &Sort);
        """

torch.utils.cpp_extension.load_inline(
    name='Sort',
    cpp_sources=op_source,
    is_python_module=False,
    verbose=True,
    )

@parse_args("v", "i", "i","i")
def symbolic_sort(g, self, topK, multi_sort, class_num):
    return g.op('custom_ops::Sort', self, topK_i=topK, multi_sort_i=multi_sort,class_num_i = class_num)
from torch.onnx import register_custom_op_symbolic
register_custom_op_symbolic('custom_ops::Sort', symbolic_sort, 12)

class Sort(torch.nn.Module):
    def __init__(self, topK, multi_sort, class_num):
        super(Sort, self).__init__()
        self.topK = topK
        self.multi_sort = multi_sort
        self.class_num = class_num

    def forward(self, x):
        return torch.ops.custom_ops.Sort(x, self.topK, self.multi_sort, self.class_num)
