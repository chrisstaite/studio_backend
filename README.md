
Studio Backend
==============

Overview
--------

This project is part of the radio studio project.  It has the goal of producing an open source and useable radio studio.  The feature set should include by the end:

 - Multiple live input sources     
   - From the device
   - From live streams
 - Multiple recorded input sources
   - From a library
   - From YouTube
   - From Bandcamp
 - Multiple live output sources
   - To devices
   - To live streams
   - A rolling recording file
 - Individual mapping and mixing between the inputs and outputs
 - Psuedo-devices for multi-channel output devices to allow, for example, 8 stereo streams to play back to a 16-channel output 

Getting started
---------------

You can set up an environment to run the software by installing Python 3.  For NPM to work, you will also need Python 2 installed unfortunately - this is for dependencies to build only, not for runtime.

On Mac OS X if running Python 3.6 (seems to be fixed in 3.7) you will also need to run the following:
`/Applications/Python\ 3.6/Install\ Certificates.command`

Then you can setup using

```
python3 -m virtualenv venv
curl https://bootstrap.pypa.io/get-pip.py | venv/bin/python3
venv/bin/pip3 install -r requirements.txt
venv/bin/python3 -m nodeenv -p
```

Finally run with:

```
venv/bin/python3 server.py
```

Current State
-------------

Features that are missing are as follows:

 - Downloading playlist items from external sources (e.g. YouTube/Bandcamp)
 - A nice UI that isn't all on one page and the same for all users
