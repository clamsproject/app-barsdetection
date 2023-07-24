"""
The purpose of this file is to define the metadata of the app with minimal imports. 

DO NOT CHANGE the name of the file
"""

from mmif import DocumentTypes, AnnotationTypes

from clams.app import ClamsApp
from clams.appmetadata import AppMetadata


FRAME_TYPE_LABEL = 'bars'

# DO NOT CHANGE the function name 
def appmetadata() -> AppMetadata:
    """
    Function to set app-metadata values and return it as an ``AppMetadata`` obj.
    Read these documentations before changing the code below
    - https://sdk.clams.ai/appmetadata.html metadata specification. 
    - https://sdk.clams.ai/autodoc/clams.appmetadata.html python API
    
    :return: AppMetadata object holding all necessary information.
    """
    
    # Initial Metadata
    metadata = AppMetadata(
        name="Bars Detection",
        description="This tool detects SMPTE color bars.",
        app_license="MIT", 
        identifier="bars-detection",
        url=f"https://github.com/clamsproject/app-barsdetection" ,
    )
    # I/O Specification
    metadata.add_input(DocumentTypes.VideoDocument)
    metadata.add_output(AnnotationTypes.TimeFrame, typeSpecificProperty={"frameType": FRAME_TYPE_LABEL})
    
    # Runtime Param Specification
    metadata.add_parameter(name="timeUnit",
                           description="Unit for output typeframe.",
                           choices=["frames", "seconds", "milliseconds"],
                           default="frames",
                           type="string") 

    metadata.add_parameter(name="sampleRatio",
                           description="Frequency to sample frames.",
                           default=30,  # ~1 frame per second
                           type="integer")
    
    metadata.add_parameter(name="stopAt",
                           description="Frame number to stop processing.",
                           default=5 * 60 * 30,  # ~5 minutes of video at 30fps
                           type="integer")
    
    metadata.add_parameter(name="stopAfterOne",
                           description="When True, processing stops after first timeframe is found.",
                           default=True,
                           type="boolean")
    
    metadata.add_parameter(name="minFrameCount",
                           description="minimum number of frames required for a timeframe to be included in the output.",
                           default=10,
                           type="integer")

    metadata.add_parameter(name="threshold",
                           description="Threshold from 0-1, lower accepts more potential slates.",
                           type="number",
                           default=0.7)
    return metadata


# DO NOT CHANGE the main block
if __name__ == '__main__':
    import sys
    metadata = appmetadata()
    for param in ClamsApp.universal_parameters:
        metadata.add_parameter(**param)
    sys.stdout.write(metadata.jsonify(pretty=True))
