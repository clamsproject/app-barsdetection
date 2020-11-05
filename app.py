import pickle
import cv2
from imutils.video import FileVideoStream
from clams.serve import ClamsApp
from clams.restify import Restifier
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from mmif import Mmif

from skimage.metrics import structural_similarity

class BarDetection(ClamsApp):
    def appmetadata(self):
        metadata = {
            "name": "Bar Detection",
            "description": "This tool detects SMPTE Bars.",
            "vendor": "Team CLAMS",
            "requires": [DocumentTypes.VideoDocument],
            "produces": [AnnotationTypes.TimeFrame],
        }
        return metadata

    def setupmetadata(self):
        return None

    def sniff(self, mmif):
        # this mock-up method always returns true
        return True

    def annotate(self, mmif: Mmif):
        video_filename = mmif.get_document_location(DocumentTypes.VideoDocument.value)
        output = self.run_detection(
            video_filename, mmif
        )
        new_view = mmif.new_view()
        for _id, frames in enumerate(output):
            start_frame, end_frame = frames
            timeframe_annotation = new_view.new_annotation(f"tf{_id}", AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start", start_frame)
            timeframe_annotation.add_property("end", end_frame)
            timeframe_annotation.add_property("unit", "frame")
            timeframe_annotation.add_property("frameType", "bars")
        return mmif

    @staticmethod
    def run_detection(video_filename, mmif=None, stop_after_one=True):
        sample_ratio = 30

        with open("grey.p", "rb") as p:
            grey = pickle.load(p)

        def frame_in_range(frame_):
            '''returns true is frame is of type being detected, else false'''
            def process_image(f):
                f = cv2.cvtColor(frame_, cv2.COLOR_BGR2GRAY)
                return f

            f = process_image(frame_)
            if f.shape != grey.shape:
                f = cv2.resize(f, (grey.shape[1], grey.shape[0]))
            (score, _) = structural_similarity(f, grey, full=True)
            return score > .7


        fvs = FileVideoStream(video_filename).start()
        counter = 0
        result_list = []
        in_range = False
        start_frame = None
        while fvs.running():
            frame = fvs.read()
            if counter > (30 * 60 * 5):  ## about 5 minutes
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
                        if counter - start_frame > 30: # minimum duration to be included
                            result_list.append((start_frame, counter))
                        if stop_after_one:
                            return result_list
            counter += 1
        return result_list


if __name__ == "__main__":
    tool = BarDetection()
    service = Restifier(tool)
    service.run()
