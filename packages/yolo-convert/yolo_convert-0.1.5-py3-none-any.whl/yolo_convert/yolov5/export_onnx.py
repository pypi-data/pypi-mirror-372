import argparse
import sys
import time

import torch
import torch.nn as nn
from pathlib import Path
# 添加yolov5目录到Python路径
yolov5_dir = Path(__file__).parent
sys.path.insert(0, str(yolov5_dir))

from models.experimental import attempt_load
from utils.general import set_logging, check_img_size
from utils.torch_utils import select_device
import modify_model
from yolo_convert.yolov5.EfficientNMS import End2End

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='./yolov5s.pt', help='weights path')
    parser.add_argument('--img-size', nargs='+', type=int, default=[640, 640], help='image size')  # height, width
    parser.add_argument('--batch-size', type=int, default=1, help='batch size')
    parser.add_argument('--max-obj', type=int, default=100, help='topk')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='nms iou threshold')
    parser.add_argument('--score-thres', type=float, default=0.25, help='nms score threshold')
    parser.add_argument('--dynamic', action='store_true', help='dynamic ONNX axes')
    parser.add_argument('--device', default='cpu', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    opt = parser.parse_args()

    return opt


def run(weights="yolov5s.pt", 
        imgsz=(640, 640), 
        device="cpu", 
        hisi3559=False, 
        hisi3403=False, 
        hisi3519=False, 
        tensorrt=False,
        atlas=False, 
        opset=12, 
        dynamic=False, 
        conf_thres=0.20, 
        iou_thres=0.45, 
        class_num=80, 
        biases=[10.,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326],
        ):
    
    """运行ONNX转换"""
    import global_config
    global_config.HISI3559 = hisi3559
    global_config.ATLAS = atlas
    global_config.HISI3403 = hisi3403
    global_config.HISI3519 = hisi3519
    global_config.TENSORRT = tensorrt

    global_config.w = imgsz[1]
    global_config.h = imgsz[0]

    global_config.conf_thres = conf_thres
    global_config.iou_thres = iou_thres

    # Load PyTorch model
    device = select_device(device)
    model = attempt_load(weights, device=device) # load FP32 model

    # Checks
    gs = int(max(model.stride))  # grid size (max stride)
    img_size = [check_img_size(x, gs) for x in imgsz]  # verify img_size are gs-multiples
    
    # Input
    batch_size = 1
    img = torch.zeros(batch_size, 3, *img_size).to(device)  # image size(1,3,320,192) iDetection
    model.eval()
    
    model.model[-1].export = True
    if tensorrt:
        model.model[-1].dynamic = True
        # print(model.model[-1].dynamic) 
        model = End2End(model, max_obj=100, iou_thres=iou_thres, score_thres=conf_thres, max_wh=False, device=device)


    # ONNX export
    try:
        import onnx
        print('\nStarting ONNX export with onnx %s, opset=%d 🚀' % (onnx.__version__, opset))
        f = weights.replace('.pt', '.onnx')  # filename
        print(f)
        if dynamic:
            if hisi3559 or atlas:
                dynamic_axes = {
                    "images": {0: "batch", 2: "height", 3: "width"},
                    "output0": {0: "batch", 2: "height0", 3: "width0"},
                    "output1": {0: "batch", 2: "height1", 3: "width1"},
                    "output2": {0: "batch", 2: "height2", 3: "width2"},
                }
            elif tensorrt:
                dynamic_axes = {
                    "images": {0: "batch", 2: "height", 3: "width"},
                    'num_dets': {0: 'batch_size'},                     # [batch, 1]
                    'det_boxes': {0: 'batch_size'},                    # [batch, 100, 4] - 框数量固定为100
                    'det_scores': {0: 'batch_size'},                   # [batch, 100] - 框数量固定为100
                    'det_classes': {0: 'batch_size'}                   # [batch, 100] - 框数量固定为100
                }
            else:
                dynamic_axes = {
                    "images": {0: "batch", 2: "height", 3: "width"},
                    "output0": {0: "batch", 1: "anchors"}
                }
        else:
            dynamic_axes = None
        print(f'dynamic input: {dynamic_axes}')
        # 导出 ONNX
        # torch.onnx.export(
        #     model,
        #     img,
        #     f,
        #     opset_version=opset,
        #     input_names=['images'],
        #     dynamic_axes=dynamic_axes,
        #     do_constant_folding=True,  # 常量折叠优化
        #     custom_opsets={"custom_ops": 12},         
        # )

        export_args = dict(
            opset_version=opset,
            input_names=['images'],
            dynamic_axes=dynamic_axes,
            do_constant_folding=True,
        )

        if hisi3403 or hisi3519:
            export_args["custom_opsets"] = {"custom_ops": 12}

        torch.onnx.export(model, img, f, **export_args)

        # Checks
        onnx_model = onnx.load(f)  # load onnx model
    
        print("Simplifying ONNX model...")
        from onnxsim import simplify
        model_simp, check = simplify(onnx_model)
        if check:
            onnx.save(model_simp, str(f))
            print("ONNX model simplified successfully.")
        else:
            print("ONNX simplify check failed, using original model.")


        if atlas:
            import modify_model

            model_path = f
            modify_model.main(model_path, img_size, batch_size, conf_thres, iou_thres, class_num, biases)

            
        print('ONNX export success, saved as %s' % f)
    except Exception as e:
        print('ONNX export failure: %s' % e)

if __name__ == "__main__":
    opt = parse_opt()
    run(opt.weights, opt.img_size, opt.device)
