from multiprocessing import Queue

from utils import PostProcess, Visualizer
from base import Camera, RK3588


rknn_postprocess_cfg = {'img_size' : 544,
                        'scales' : [24, 48, 96, 192, 384],
                        'aspect_ratios': [1, 0.5, 2],
                        'top_k' : 200,
                        'max_detections' : 100,
                        'nms_score_thre' : 0.5,
                        'nms_iou_thre' : 0.5,
                        'visual_thre' : 0.3,
                    }


def run(device, visualizer, post_process):
    device._camera.start()
    device._neuro.run_inference()
    if post_process is not None:
        post_process.run()
        while True:
            frame, outputs = post_process.get_outputs()
            visualizer.show_results(frame, outputs)
            # gps_data = matcher.get_gps_data(frame, mask)

def main(source):
    """
    """
    POST_ONNX = False
    queue_size = 5
    q_pre = Queue(maxsize=queue_size)
    model = ('YOLACT' if POST_ONNX else 'YOLACT_minimal')
    camera = Camera(source=source,
                    queue=q_pre,
                    onnx=POST_ONNX)
    device = RK3588(model, camera)
    post_processes = PostProcess(queue=device._neuro.net.inference.q_out,
                                 cfg=rknn_postprocess_cfg,
                                 onnx=POST_ONNX)
    visualizer = Visualizer(onnx=POST_ONNX)
    try:
        run(device, visualizer, post_processes)
    except Exception as e:
        print("Main exception: {}".format(e))
        exit()


if __name__ == "__main__":
    camera_source = 11 # '/home/firefly/11.mp4'
    main(camera_source)
