BeatDown
========

Beatdown is an audio analysis tool for powering concerts.

Beatdown detects incoming musical properties using your Mac's microphone and then transmits MIDI to configurable channels and CCs. It is suitable for controlling both automated stage lighting (example: DMX) and VJ software.

Currently this automation is primarily in the form of the relative volume level, which could be used to dim stage lighting in response to music, etc. It may evolve to include chord detection and other features.

Tempo detection sending to MIDI clock is in progress.

Requirements
============

Requires Python 3.5/3.6 on OSX so far.

Installation
============

* Assuming an OS X install, get Python here:

   https://www.python.org/downloads/mac-osx/

* Install pyo for your version of Python using the installer: 
 
   http://ajaxsoundstudio.com/software/pyo/

* Add Python3 to your system path:

   vim ~/.bash/profile

   export PATH=/Library/Frameworks/Python.framework/Versions/3.6/bin/:$PATH
   
   source ~/.bash_profile

* pip3 install -U wxPython

Recommended Software
====================

* LightKey controls DMX stage lighting and is free for up to 24 channels and can be configured to respond to MIDI events:

   http://www.lightkeyapp.com/en/

* MIDI responsive VJ software of your choice (optional)

Usage
=====

To open the GUI, launch ./beatdown.py and then select your input and MIDI channels.  You should be able to observe the changes in the VU meter.

To send MIDI clock (in progress), run ./midiclock.py in the scripts directory.

License
=======

beatdown is available under an Apache2 license

Contact info
============

Chris Church - chris@ninemoreminutes.com

