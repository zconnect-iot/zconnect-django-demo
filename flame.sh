#!/bin/sh

set -ex

displayflame () {
    curl http://localhost:$1/stats/stacksampler/ | tail -n +2 | $HOME/code/FlameGraph/flamegraph.pl  > $2.svg && chromium-browser $2.svg
    # curl http://localhost:$1/stats/stacksampler/ | $HOME/code/FlameGraph/flamegraph.pl  > $2.svg && chromium-browser $2.svg
}

displayflame 8981 stats
