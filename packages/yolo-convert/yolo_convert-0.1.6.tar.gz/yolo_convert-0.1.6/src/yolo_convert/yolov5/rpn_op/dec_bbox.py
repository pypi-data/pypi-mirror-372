import unittest
import torch
import torch.utils.cpp_extension

import onnx

import numpy as np
import io
from torch.onnx.symbolic_helper import parse_args
from torch.onnx import register_custom_op_symbolic
from torch.onnx.symbolic_helper import _maybe_get_const
import pickle

op_source = """
        #include <torch/script.h>
        torch::Tensor DecBBox(torch::Tensor input0, torch::Tensor bias, int64_t num_anchors,
            int64_t num_coords, int64_t num_classes, int64_t m_gridH, int64_t m_gridW, int64_t m_imgW, int64_t m_imgH,
            int64_t useClassId, int64_t calc_mode,int64_t clip_box,int64_t share_loc, int64_t multi_label)
        {
            if ((calc_mode == 3 || calc_mode == 5) && multi_label == 0) {
                return torch::zeros({1, 1, 5 + useClassId, input0.size(3)});
            } else {
                return torch::zeros({1, num_classes, 5 + useClassId, input0.size(3)});
            }
        }
        static auto registry =
            torch::RegisterOperators("custom_ops::DecBBox", &DecBBox);
        """

torch.utils.cpp_extension.load_inline(
    name='DecBBox',
    cpp_sources=op_source,
    is_python_module=False,
    verbose=True,
    )

@parse_args('v', 'v', 'i', 'i', 'i', 'i', 'i', 'i', 'i', 'i','i','i','i', 'i')
def symbolic_decbbox(g, input, bias, num_anchors, num_coords, num_classes, gridH, gridW, imgW, imgH, useClassId, calc_mode, clip_bbox, share_loc, multi_label):
    return g.op('custom_ops::DecBBox', input,  bias, num_anchors_i = num_anchors, num_coords_i = num_coords, num_classes_i = num_classes,
                gridH_i = gridH, gridW_i = gridW, imgW_i = imgW, imgH_i = imgH, useClassId_i = useClassId, calc_mode_i = calc_mode,
                clip_bbox_i = clip_bbox,share_loc_i = share_loc, multi_label_i = multi_label)
from torch.onnx import register_custom_op_symbolic
register_custom_op_symbolic('custom_ops::DecBBox', symbolic_decbbox, 12)

class DecBBox(torch.nn.Module):
    def __init__(self, y,num_anchors,num_coords,num_classes, gridH, gridW, imgW, imgH, useClassId, calc_mode,clip_bbox,share_loc, multi_label = 0):
        super(DecBBox, self).__init__()
        self.register_buffer('y', torch.tensor(y))
        self.num_anchors = num_anchors
        self.num_coords = num_coords
        self.num_classes = num_classes
        self.gridH = gridH
        self.gridW = gridW
        self.imgW = imgW
        self.imgH = imgH
        self.useClassId = useClassId
        self.calc_mode = calc_mode
        self.clip_bbox = clip_bbox
        self.share_loc = share_loc
        self.multi_label = multi_label
    def forward(self, x):
        return torch.ops.custom_ops.DecBBox(x,self.y,self.num_anchors, self.num_coords,self.num_classes, self.gridH,self.gridW,
            self.imgW,self.imgH, self.useClassId, self.calc_mode,self.clip_bbox,self.share_loc, self.multi_label)

# DecBBox2: for ssd & fastercnn with 2 inputs
class DecBBox2(torch.nn.Module):
    def __init__(self, num_anchors,num_coords,num_classes, gridH, gridW, imgW, imgH, useClassId, calc_mode,clip_bbox,share_loc):
        super(DecBBox, self).__init__()
        self.num_anchors = num_anchors
        self.num_coords = num_coords
        self.num_classes = num_classes
        self.gridH = gridH
        self.gridW = gridW
        self.imgW = imgW
        self.imgH = imgH
        self.useClassId = useClassId
        self.calc_mode = calc_mode
        self.clip_bbox = clip_bbox
        self.share_loc = share_loc
        self.multi_label = 0
    def forward(self, x, y):
        return torch.ops.custom_ops.DecBBox(x, y, self.num_anchors, self.num_coords,self.num_classes, self.gridH,self.gridW,
            self.imgW,self.imgH, self.useClassId, self.calc_mode,self.clip_bbox,self.share_loc, self.multi_label)