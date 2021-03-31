import pickle
import cv2
from imutils.video import FileVideoStream
from clams.app import ClamsApp
from clams.restify import Restifier
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from mmif import Mmif

from skimage.metrics import structural_similarity

APP_VERSION="0.2.0"


class BarDetection(ClamsApp):
    def _appmetadata(self):
        metadata = {
            "name": "Bar Detection",
            "description": "This tool detects SMPTE Bars.",
            "vendor": "Team CLAMS",
            "iri": f"http://mmif.clams.ai/apps/barsdetection/{APP_VERSION}",
            "requires": [DocumentTypes.VideoDocument],
            "produces": [AnnotationTypes.TimeFrame],
        }
        return metadata

    def _annotate(self, mmif: Mmif, **kwargs):
        video_filename = mmif.get_document_location(DocumentTypes.VideoDocument.value)
        output = self.run_detection(
            video_filename, mmif, **kwargs
        )
        new_view = mmif.new_view()
        new_view.metadata.set_additional_property("parameters", kwargs.copy())
        new_view.metadata['app'] = self.metadata["iri"]

        for _id, frames in enumerate(output):
            start_frame, end_frame = frames
            timeframe_annotation = new_view.new_annotation(f"tf{_id}", AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start", start_frame)
            timeframe_annotation.add_property("end", end_frame)
            timeframe_annotation.add_property("unit", "frame")
            timeframe_annotation.add_property("frameType", "bars")
        return mmif

    @staticmethod
    def run_detection(video_filename, mmif=None, **kwargs):
        sample_ratio = int(kwargs.get('sampleRatio', 30))
        min_duration = int(kwargs.get('minFrameCount', 10))
        stop_after_one = kwargs.get('stopAfterOne', False)
        stop_at = int(kwargs.get('stopAt', 30*60*60*5)) # default 5 hours
        ssim_threshold=float(kwargs.get("threshold", .7))
        with open("grey.p", "rb") as p:
            grey = pickle.load(p)

        def frame_in_range(frame_):
            '''returns true is frame is of type being detected, else false'''
            def process_image(f):
                f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                return f
            f = process_image(frame_)
            if f.shape != grey.shape:
                f = cv2.resize(f, (grey.shape[1], grey.shape[0]))
            score = structural_similarity(f, grey)
            return score > ssim_threshold

        fvs = FileVideoStream(video_filename).start()
        counter = 0
        result_list = []
        in_range = False
        start_frame = None
        while fvs.running():
            frame = fvs.read()
            if counter > stop_at:  ## about 5 minutes
                break
            if counter % sample_ratio == 0:
                result = frame_in_range(frame)
                if result:
                    if not in_range:
                        in_range = True
                        start_frame = counter
                else:
                    if in_range:
                        in_range = False
                        if counter - start_frame > min_duration:
                            result_list.append((start_frame, counter))
                            if stop_after_one:
                                return result_list
            counter += 1
        return result_list


if __name__ == "__main__":
    tool = BarDetection()
    service = Restifier(tool)
    service.run()
