# app-barsdetection

## User instruction

General user instruction for CLAMS apps is available at [CLAMS Apps documentation](https://apps.clams.ai/clamsapp/).

We provide a Dockerfile. If you want to run the SMPTE bar detector as a docker container (not worrying about dependencies), build an image from the Dockerfile and run it with the target directory mounted to /data. Just MAKE SURE that target directory is writable by others (chmod o+w $TARGET_DIR). For example,

```bash
chmod -R o+w data_dir && docker build . -t bar_detector && docker run --rm -p 5000:5000 -v data_dir:/data bar_detector
```

This will run the bar detector on port 5000.

The video files should be in a directory named `video` in the data_dir directory.

The bar detector can be applied to an mmif from the terminal with the following command `curl -X PUT -d @path/to/mmif/file http://0.0.0.0:5000`

Where the mmif file contains a video document with a location specified relative to the docker mount location:

```json
{ "metadata": { "mmif": "http://mmif.clams.ai/0.2.1" }, "documents": [ { "@type": "http://mmif.clams.ai/0.2.1/vocabulary/VideoDocument", "properties": { "mime": "video", "location": "/data/video/cpb-aacip-29-00ns1swq.h264.mp4", "id": "d1" } } ], "views": [] }
```

## Configurable runtime parameters

The runtime parameters of this tool are configured for various use cases, and are capable of streamlining certain tasks. In order to use these parameters, simply include them in the POST request:

```bash
curl -X PUT -d @path/to/mmif/file http://0.0.0.0:5000?stopAt=1800
```


