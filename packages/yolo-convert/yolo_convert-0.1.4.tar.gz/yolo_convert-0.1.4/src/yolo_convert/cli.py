import argparse
from pathlib import Path
from .yolov5 import export_onnx as yolo_export

def main():
    parser = argparse.ArgumentParser(prog="yolo_convert", description="YOLOv5 model converter")
    parser.add_argument("-i", "--input", type=str, default='./yolov5s.pt', help='weights path')
    parser.add_argument("--hisi3559", action="store_true", help="Export to 3-heads ONNX outputs for HiSilicon 3559")
    parser.add_argument("--hisi3403", action="store_true", help="Export to 3-heads ONNX outputs for HiSilicon 3403")
    parser.add_argument("--hisi3519", action="store_true", help="Export to 3-heads ONNX outputs for HiSilicon 3519")
    parser.add_argument("--tensorrt", action="store_true", help="Export to TensorRT ONNX outputs")
    parser.add_argument("--imgsz", "--img", "--img-size", nargs="+", type=int, default=[640, 640], help="image (h, w)")
    parser.add_argument("--opset", type=int, default=12, help="ONNX opset version")
    parser.add_argument("--dynamic", action="store_true", help="ONNX/TF/TensorRT: dynamic axes")
    parser.add_argument("--atlas", action="store_true", help="Process for Atlas with NMS")
    parser.add_argument("--conf-thres", type=float, default=0.20, help="NMS confidence threshold")
    parser.add_argument("--iou-thres", type=float, default=0.45, help="NMS IoU threshold")
    parser.add_argument("--class-num", type=int, default=80, help="Number of classes")
    parser.add_argument("--biases", nargs="+", type=float, default=[10.0,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326], help="Anchor biases")
    args = parser.parse_args()

    # weights_path = str(Path(args.input).resolve())

    # 调用 run() 时直接传 Python 参数
    yolo_export.run(weights=args.input,
                    imgsz=args.imgsz,
                    hisi3559=args.hisi3559,
                    hisi3403=args.hisi3403,
                    hisi3519=args.hisi3519,
                    tensorrt=args.tensorrt,
                    opset=args.opset,
                    dynamic=args.dynamic,
                    atlas=args.atlas,
                    conf_thres=args.conf_thres,
                    iou_thres=args.iou_thres,
                    class_num=args.class_num,
                    biases=args.biases
                    )
