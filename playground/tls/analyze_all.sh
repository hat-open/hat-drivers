#!/bin/sh

RUN_PATH=$(dirname -- "$0")

ANALYZER_OPTS="--general-msgs"

find "$1" -type f -name '*.pcapng' | while read path; do
    for stream in $(tshark -r "$path" -T fields -e tcp.stream | sort -un); do
        echo ">>" $path $stream
        tshark -r "$path" -q -z follow,tcp,raw,$stream | \
            grep -v '[=:]' | \
            $RUN_PATH/analyzer.sh $ANALYZER_OPTS
    done
done
