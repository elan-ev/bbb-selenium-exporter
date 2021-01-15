bbb-selenium-exporter
=====================

A Selenium-based BigBlueButton monitoring for Prometheus.

The bbb-selenium-exporter runs a set of Selenium tests against BigBlueButton in a configurable interval and provides the results as OpenMetrics endpoint consumable by Prometheus.
This allows for a continuous monitoring of BigBlueButton based on the good working order of the user interface.


Installation
------------

To run the exporter, you need:

- Python 3
- [Google Chrome](https://www.google.com/chrome/)
- A matching [ChromeDriver](https://chromedriver.chromium.org/downloads)

Use the `setup.py` to build and install the bbb-selenium-exporter:

```sh
% python setup.py install
```


Command Line
------------

You can use the `--help` flag to get all command line options of the exporter:

```
% bbb-selenium-exporter --help
usage: bbb-selenium-exporter [-h] [--bind BIND] [--config CONFIG] [--interval INTERVAL] [--jobs JOBS] [--gui]

optional arguments:
  -h, --help            show this help message and exit
  --bind BIND, -b BIND  bind to address:port
  --config CONFIG, -c CONFIG
                        config file with BBB instances to scrape
  --interval INTERVAL, -i INTERVAL
                        interval between scrapes of the same host in seconds
  --jobs JOBS, -j JOBS  number of parallel webdriver instances
  --gui                 disable headless mode for webdriver

```


Configuration
-------------

To allow access to BigBlueButton, the exporter needs to know the API secret for every server to monitor.
For this, create a configuration file in `/etc/bbb-selenium-exporter/targets` or provide the location using the `-c` option.
The configuration file contains domain names and secrets separated by a space character like this:

```
bbb.example.com BBB-API-SECRET
```


Metrics
-------

```
# HELP connect_server_success Success of connecting to BBB server
# TYPE connect_server_success gauge
connect_server_success{backend="bbb.example.com"} 1.0
# HELP connect_server_duration_seconds Duration of connecting to BBB server
# TYPE connect_server_duration_seconds gauge
connect_server_duration_seconds{backend="bbb.example.com"} 1.4048139119986445
# HELP echo_test_success Success of waiting for echo test
# TYPE echo_test_success gauge
echo_test_success{backend="bbb.example.com"} 1.0
# HELP echo_test_duration_seconds Duration of waiting for echo test
# TYPE echo_test_duration_seconds gauge
echo_test_duration_seconds{backend="bbb.example.com"} 3.0636934980029764
# HELP join_headphone_success Success of joining room with headphones
# TYPE join_headphone_success gauge
join_headphone_success{backend="bbb.example.com"} 1.0
# HELP join_headphone_duration_seconds Duration of joining room with headphones
# TYPE join_headphone_duration_seconds gauge
join_headphone_duration_seconds{backend="bbb.example.com"} 0.17476947300019674
# HELP start_cam_success Success of starting camera
# TYPE start_cam_success gauge
start_cam_success{backend="bbb.example.com"} 1.0
# HELP start_cam_duration_seconds Duration of starting camera
# TYPE start_cam_duration_seconds gauge
start_cam_duration_seconds{backend="bbb.example.com"} 14.53077382000265
# HELP upload_pres_success Success of uploading presentation
# TYPE upload_pres_success gauge
upload_pres_success{backend="bbb.example.com"} 1.0
# HELP upload_pres_duration_seconds Duration of uploading presentation
# TYPE upload_pres_duration_seconds gauge
upload_pres_duration_seconds{backend="bbb.example.com"} 6.875032278003346
# HELP chat_test_success Success of testing chat
# TYPE chat_test_success gauge
chat_test_success{backend="bbb.example.com"} 1.0
# HELP chat_test_duration_seconds Duration of testing chat
# TYPE chat_test_duration_seconds gauge
chat_test_duration_seconds{backend="bbb.example.com"} 0.8765619519981556
# HELP poll_test_success Success of testing poll
# TYPE poll_test_success gauge
poll_test_success{backend="bbb.example.com"} 1.0
# HELP poll_test_duration_seconds Duration of testing poll
# TYPE poll_test_duration_seconds gauge
poll_test_duration_seconds{backend="bbb.example.com"} 0.8743671500014898
# HELP etherpad_test_success Success of testing etherpad
# TYPE etherpad_test_success gauge
etherpad_test_success{backend="bbb.example.com"} 1.0
# HELP etherpad_test_duration_seconds Duration of testing etherpad
# TYPE etherpad_test_duration_seconds gauge
etherpad_test_duration_seconds{backend="bbb.example.com"} 2.3751644189978833
```
