"""
The purpose of this file is to define the metadata of the app with minimal imports. 

DO NOT CHANGE the name of the file
"""

from mmif import DocumentTypes, AnnotationTypes
from clams.appmetadata import AppMetadata


APP_VERSION = "0.2.1"
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
        description="This tool detects SMPTE Bars.",
        app_license="MIT", 
        identifier="bars-detection",
        url=f"http://mmif.clams.ai/apps/barsdetection/{APP_VERSION}" ,
        #analyzer_version='version_X',
        #analyzer_version=[l.strip().rsplit('==')[-1] for l in open('requirements.txt').readlines() if re.match(r'^ANALYZER_NAME==', l)][0],
        #analyzer_license="",  # short name for a software license
    )
    # I/O Specification
    metadata.add_input(DocumentTypes.VideoDocument)
    metadata.add_output(AnnotationTypes.TimeFrame, typeSpecificProperty={"frameType":"string"})
    
    # Runtime Param Specification
    metadata.add_parameter(name="timeUnit",
                           description="Unit for output typeframe.",
                           choices=["frames","milliseconds"],
                           default="frames",
                           type="string") 

    metadata.add_parameter(name="sampleRatio",
                           description="Frequency to sample frames.",
                           default=30,
                           type="integer")
    
    metadata.add_parameter(name="stopAt",
                           description="Frame number to stop processing.",
                           default=30 * 60 * 60 * 5, 
                           type="integer")
    
    metadata.add_parameter(name="stopAfterOne",
                           description="When True, processing stops after first timeframe is found.",
                           default=True,
                           type="boolean")
    
    metadata.add_parameter(name="minFrameCount",
                           description="minimum number of frames required for a timeframe to be included in the output.",
                           default=10,
                           type="integer")
    return metadata


# DO NOT CHANGE the main block
if __name__ == '__main__':
    import sys
    sys.stdout.write(appmetadata().jsonify(pretty=True))
