import argparse
from typing import Union

import pickle
import cv2
import traceback
import clams 
from clams import ClamsApp, Restifier
from mmif import Mmif, View, Annotation, Document, AnnotationTypes, DocumentTypes

from skimage.metrics import structural_similarity

class BarsDetection(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:
        video_filename = mmif.get_document_location(DocumentTypes.VideoDocument)[7:]
        try:
            output = self.run_detection(
                video_filename, mmif, **parameters
            )
        except Exception as e:
            print(f"error processing file {video_filename}")
            output = []
            traceback.print_exc()
        config = self.get_configuration(**parameters)
        unit = config["timeUnit"]
        new_view = mmif.new_view()
        self.sign_view(new_view, config)
        new_view.new_contain(
            AnnotationTypes.TimeFrame,
            timeUnit=unit,
            document=mmif.get_documents_by_type(DocumentTypes.VideoDocument)[0].id
        )
        print(output) 

        if unit == "milliseconds":
            output = output[1]
        elif unit == "frames":
            output = output[0]
        else:
            raise TypeError(
                "Invalid unit type"
            )
        for _id, frames in enumerate(output):
            start_frame, end_frame = frames
            timeframe_annotation = new_view.new_annotation(AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start",start_frame)
            timeframe_annotation.add_property("end",end_frame)
            timeframe_annotation.add_property("frameType","bars")
        return mmif

    @staticmethod
    def run_detection(video_filename, mmif=None, **kwargs):
        sample_ratio = int(kwargs.get('sampleRatio',30))
        min_duration = int(kwargs.get('minFrameCount',10))
        stop_after_one = kwargs.get('stopAfterOne',False)
        stop_at = int(kwargs.get('stopAt',30*60*60*5))
        ssim_threshold = float(kwargs.get('threshold',0.7))
        with open("grey.p", "rb") as p:
            grey = pickle.load(p)
        
        def frame_in_range(frame_):
            '''Returns true if frame is of type being detected, else false'''
            def process_image(f):
                f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                return f
            f = process_image(frame_)
            if f.shape != grey.shape:
                f = cv2.resize(f (grey.shape[1], grey.shape[0]))
            score = structural_similarity(f, grey)
            return score > ssim_threshold

        cap = cv2.VideoCapture(video_filename)
        counter = 0
        frame_number_result = []
        seconds_result = []
        in_range = False
        start_frame = None
        start_seconds = None
        while True:
            _, frame = cap.read()
            if frame is None:
                break
            if counter > stop_at:
                if in_range:
                    if counter - start_frame > min_duration:
                        frame_number_result.append((start_frame, counter))
                        seconds_result.append(
                            (start_seconds, cap.get(cv2.CAP_PROP_POS_MSEC))
                        )
                break
            if counter % sample_ratio == 0:
                result = frame_in_range(frame)
                if result:
                    if not in_range:
                        in_range = True
                        start_frame = counter
                        start_seconds = cap.get(cv2.CAP_PROP_POS_MSEC)
                else:
                    if in_range:
                        in_range = False
                        if counter - start_frame > min_duration:
                            frame_number_result.append((start_frame, counter))
                            seconds_result.append(
                                (start_seconds, cap.get(cv2.CAP_PROP_POS_MSEC))
                            )
                            if stop_after_one:
                                break
            counter += 1
        return frame_number_result, seconds_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", action="store", default="5000", help="set port to listen"
    )
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    # more arguments as needed
    # parser.add_argument(more_arg...)

    parsed_args = parser.parse_args()

    # create the app instance
    app = BarsDetection()

    http_app = Restifier(app, port=int(parsed_args.port)
    )
    if parsed_args.production:
        http_app.serve_production()
    else:
        http_app.run()
