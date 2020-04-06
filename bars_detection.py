import cv2
import pickle
import os

from skimage.measure import compare_ssim
from clams.serve import ClamApp
from clams.serialize import *
from clams.vocab import AnnotationTypes
from clams.vocab import MediaTypes
from clams.restify import Restifier


class BarsDetection(ClamApp):

    def appmetadata(self):
        metadata = {"name": "Bars Detection",
                    "description": "This tool detects bars based on structural similarity to a template frame.",
                    "vendor": "Team CLAMS",
                    "requires": [MediaTypes.V],
                    "produces": [AnnotationTypes.BD]}
        return metadata

    def sniff(self, mmif):
        # this mock-up method always returns true
        return True

    def annotate(self, mmif):
        if type(mmif) is not Mmif:
            mmif = Mmif(mmif)
        video_filename = mmif.get_medium_location(MediaTypes.V)
        bars_output = self.run_bd(video_filename) #bars_output is a list of frame number interval tuples

        new_view = mmif.new_view()
        contain = new_view.new_contain(AnnotationTypes.BD)
        contain.producer = self.__class__

        for int_id, (start_frame, end_frame) in enumerate(bars_output):
            annotation = new_view.new_annotation(int_id)
            annotation.start = str(start_frame)
            annotation.end = str(end_frame)
            annotation.attype = AnnotationTypes.BD

        for contain in new_view.contains.keys():
            mmif.contains.update({contain: new_view.id})
        return mmif

    @staticmethod
    def run_bd(video_filename):
        # detect bars and tones based on template match score compared with sample bar frame
        sample_ratio = 30
        with open("grey.p", "rb") as p:
            grey = pickle.load(p)

        def process_image(f):
            abs_lap = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            return abs_lap

        def calculate_similarity(frame):
            # returns boolean, score
            f = process_image(frame)
            (score, _) = compare_ssim(f, grey, full=True)
            return (score>.7), score

        cap = cv2.VideoCapture(video_filename)
        counter = 0
        bars = []
        first_frame = True
        start_frame = 0
        prev = None

        while cap.isOpened():
            ret, f = cap.read()
            if not ret:
                break
            if counter % sample_ratio == 0:
                is_similar, val = calculate_similarity(f)
                if is_similar: ## if it is bars and tones
                    if first_frame:
                        start_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                        start_image = f
                        first_frame = False
                else: ## if its not bars and tones
                    if not first_frame: ## if the start time has been set to false so we're in bars and tones
                        end_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                        if end_frame == "0":
                            continue
                        bars.append((start_frame, end_frame))
                        base_name = video_filename.split("/")[-1]
                        if not os.path.exists("/data/img"):
                            os.mkdir("/data/img")
                        cv2.imwrite(f"/data/img/{base_name}_{int(start_frame)}.png", start_image)
                        cv2.imwrite(f"/data/img/{base_name}_{int(end_frame)}.png", prev)
                        first_frame = True
                        break ## this stops running after first bars is found
                prev = f
            counter += 1
        return bars

if __name__ == "__main__":
    bd_tool = BarsDetection()
    bd_service = Restifier(bd_tool)
    bd_service.run()

