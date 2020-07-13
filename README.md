### Conducto Demo

This is an example of the following Conducto features:
* Serial & Parallel pipelines
* Dynamic/Lazy pipeline generation (based on config file, in this case)
* persistent data / aggregation step
* visualization of data in dashboard

Additionally, I created a new docker image in DockerHub that has all the right libraries for plotting, and an appropriate glibc for running the included executable experiment.

Run with:
```sh
git clone https://github.com/joryschossau/js-conducto
cd js-conducto
python pipeline.py --local
```
