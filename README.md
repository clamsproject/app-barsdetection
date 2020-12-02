### Using docker

We provide a [`Dockerfile`](Dockerfile). If you want to run the SMPTE bar detector as a docker container (not worrying about dependencies), build an image from the `Dockerfile` and run it with the target directory mounted to `/data`. Just MAKE SURE that target directory is writable by others (`chmod o+w $TARGET_DIR`). For example, 

```bash
chmod -R o+w data_dir && docker build . -t bar_detector && docker run --rm -p 5000:5000 -v data_dir:/data bar_detector
```
This will run the bar detector on port 5000. 

The video files should be in a directory named `video` in the data_dir directory.

The bar detector can be applied to an mmif from the terminal with the following command. 
`curl -X PUT -d @path/to/mmif/file http://0.0.0.0:5000`

Where the mmif file contains a video document with a location specified relative to the docker mount location:

`{
  "metadata": {
    "mmif": "http://mmif.clams.ai/0.2.1"
  },
  "documents": [
    {
      "@type": "http://mmif.clams.ai/0.2.1/vocabulary/VideoDocument",
      "properties": {
        "mime": "video",
        "location": "/data/video/cpb-aacip-29-00ns1swq.h264.mp4",
        "id": "d1"
      }
    }
  ],
  "views": []
}`

### Tutorial

Running the docker container. 

`git clone https://github.com/clamsproject/app-barsdetection.git`

`cd app-barsdetection`

`docker build . -t bar_detector`

`docker run --rm -p 5000:5000 -v ~/data/clams/video/:/data bar_detector`

Apply the bars detector to a directory of mmifs.

First generate a directory of mmifs from a directory of video files.
Note: This assumes clams-python is installed.

`sh scripts/wrap_all.sh /path/to/videos/ /data/demo/`


Next apply the tool to all of the mmifs you just created. 

`sh scripts/apply_all.sh source_directory target_directory 0.0.0.0:5000`

