import argparse
import logging
import pickle
import warnings
from typing import Union

import cv2
from clams import ClamsApp, Restifier
from mmif import Mmif, AnnotationTypes, DocumentTypes
from mmif.utils import video_document_helper as vdh
from skimage.metrics import structural_similarity

import metadata


class BarsDetection(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        pass

    def _annotate(self, mmif: Union[str, dict, Mmif], **parameters) -> Mmif:
        if not isinstance(mmif, Mmif):
            mmif = Mmif(mmif)
        new_view = mmif.new_view()
        self.sign_view(new_view, parameters)
        vds = mmif.get_documents_by_type(DocumentTypes.VideoDocument)
        if vds:
            vd = vds[0]
        else:
            warnings.warn("No video document found in the input MMIF.")
            return mmif
        config = self.get_configuration(**parameters)
        unit = config["timeUnit"]
        new_view.new_contain(
            AnnotationTypes.TimeFrame,
            timeUnit=unit,
            document=vd.id
        )

        for bars in self.run_detection(vd, **config):
            start_frame, end_frame = bars
            timeframe_annotation = new_view.new_annotation(AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start", vdh.convert(start_frame, 'f', unit, vd.get_property("fps")))
            timeframe_annotation.add_property("end", vdh.convert(end_frame, 'f', unit, vd.get_property("fps")))
            timeframe_annotation.add_property("frameType", metadata.FRAME_TYPE_LABEL)
        return mmif

    @staticmethod
    def run_detection(vd, **kwargs):
        with open("grey.p", "rb") as p:
            grey = pickle.load(p)
        
        def frame_in_range(frame_):
            """
            Returns true if frame is of type being detected, else false
            """
            f = cv2.cvtColor(frame_, cv2.COLOR_BGR2GRAY)
            if f.shape != grey.shape:
                f = cv2.resize(f, (grey.shape[1], grey.shape[0]))
            score = structural_similarity(f, grey)
            self.logger.debug(f"frame score: {score}, {score>kwargs['threshold']}")
            return score > kwargs['threshold']
        
        cap = vdh.capture(vd)
        frames_to_test = vdh.sample_frames(0, kwargs['stopAt'], kwargs['sampleRatio'])
        self.logger.debug(f"frames to test: {frames_to_test}")
        bars_found = []
        in_slate = False
        start_frame = None
        cur_frame = frames_to_test[0]
        for cur_frame in frames_to_test:
            cap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame - 1)
            ret, frame = cap.read()
            if not ret:
                break
            if frame_in_range(frame):
                if not in_slate:
                    in_slate = True
                    start_frame = cur_frame
            elif in_slate:
                in_slate = False
                if cur_frame - start_frame > kwargs['minFrameCount']:
                    bars_found.append((start_frame, cur_frame))
                if kwargs['stopAfterOne']:
                    return bars_found
        if in_slate:
            if cur_frame - start_frame > kwargs['minFrameCount']:
                bars_found.append((start_frame, cur_frame))
        return bars_found

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", action="store", default="5000", help="set port to listen" )
    parser.add_argument("--production", action="store_true", help="run gunicorn server")

    parsed_args = parser.parse_args()

    # create the app instance
    app = BarsDetection()

    http_app = Restifier(app, port=int(parsed_args.port))
    # for running the application in production mode
    if parsed_args.production:
        http_app.serve_production()
    # development mode
    else:
        app.logger.setLevel(logging.DEBUG)
        http_app.run()
