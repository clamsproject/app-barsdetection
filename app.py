import pickle
import cv2
import traceback
import clams
from clams.app import ClamsApp
from clams.restify import Restifier
from mmif.vocabulary import AnnotationTypes, DocumentTypes
from mmif import Mmif

from skimage.metrics import structural_similarity

APP_VERSION="0.2.1"


class BarDetection(ClamsApp):
    def _appmetadata(self):
        metadata = {
            "name": "Bar Detection",
            "description": "This tool detects SMPTE Bars.",
            "app_version": str(APP_VERSION),
            "app_license": "MIT",
            "url": f"http://mmif.clams.ai/apps/barsdetection/{APP_VERSION}",
            "identifier": f"http://mmif.clams.ai/apps/barsdetection/{APP_VERSION}",
            "input": [{"@type": DocumentTypes.VideoDocument, "required": True}],
            "output": [{"@type": AnnotationTypes.TimeFrame, "properties": {"frameType": "string"}}],
            "parameters": [
                {
                    "name": "timeUnit",
                    "type": "string",
                    "choices": ["frames", "milliseconds"],
                    "default": "frames",
                    "description": "Unit for output typeframe.",
                },
                {
                    "name": "sampleRatio",
                    "type": "integer",
                    "default": "30",
                    "description": "Frequency to sample frames.",
                },
                {
                    "name": "stopAt",
                    "type": "integer",
                    "default": 30 * 60 * 60 * 5,
                    "description": "Frame number to stop processing",
                },
                {
                    "name": "stopAfterOne",
                    "type": "boolean",
                    "default": True,
                    "description": "When True, processing stops after first timeframe is found.",
                },
                {
                    "name": "minFrameCount",
                    "type": "integer",
                    "default": 10,  # minimum value = 1 todo how to include minimum
                    "description": "Minimum number of frames required for a timeframe to be included in the output",
                }
            ]
        }
        return clams.AppMetadata(**metadata)

    def _annotate(self, mmif: Mmif, **kwargs):
        video_filename = mmif.get_document_location(DocumentTypes.VideoDocument.value)[7:]
        try:
            output = self.run_detection(
                video_filename, mmif, **kwargs
            )
        except Exception as e:
            print (f"error processing file {video_filename}")
            output = []
            traceback.print_exc()
        config = self.get_configuration(**kwargs)
        unit = config["timeUnit"]
        new_view = mmif.new_view()
        self.sign_view(new_view, config)
        new_view.new_contain(
            AnnotationTypes.TimeFrame,
            timeUnit=unit,
            document=mmif.get_documents_by_type(DocumentTypes.VideoDocument)[0].id
        )
        print (output)
        if unit == "milliseconds":
            output = output[1]
        elif unit == "frames":
            output = output[0]
        else:
            raise TypeError(
                "invalid unit type"
        )
        for _id, frames in enumerate(output):
            start_frame, end_frame = frames
            timeframe_annotation = new_view.new_annotation(AnnotationTypes.TimeFrame)
            timeframe_annotation.add_property("start", start_frame)
            timeframe_annotation.add_property("end", end_frame)
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

        print (f"running file {video_filename}")
        fvs = FileVideoStream(video_filename).start()
        counter = 0
        result_list = []
        in_range = False
        start_frame = None
        start_seconds = None
        while True:
            _, frame = cap.read()
            if frame is None: ##todo 4/27/21 kelleylynch revisit  this , is  it really necessary, why are we getting a None frome?
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
        return result_list


if __name__ == "__main__":
    tool = BarDetection()
    service = Restifier(tool)
    service.run()
