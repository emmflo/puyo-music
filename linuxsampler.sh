#!/bin/bash
linuxsampler &
DIR=$( cd "$( dirname "$0" )" && pwd )
COMMAND="LOAD INSTRUMENT NON_MODAL '$DIR/Maestro\x20Concert\x20Grand\x20v2/maestro_concert_grand_v2.gig' 0 0\nQUIT"
sleep 0.5 && cat ./piano.lscp | netcat localhost 8888 &
sleep 2 && echo $COMMAND | netcat localhost 8888 &
