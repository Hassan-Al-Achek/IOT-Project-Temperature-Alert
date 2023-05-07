#!/bin/bash

function usage {
    echo "[?] Help:"
    echo "$0 -p <path/to/data>"
}

function scriptDescription {
    echo "[?] Description:"
    echo "This script run all the necessary scripts"
    echo "And save results on: LoraWan and result directory"
}

while getopts "hdp:" opt
do
    case "${opt}" in
        h)
            usage
            ;;
        d)
            scriptDescription
            ;;
        p)

            dataDirectory=${OPTARG}
            ./extractTemperatureMQTT.sh -p $dataDirectory
            echo ""
            ./exploreLoraWanData.sh -p $dataDirectory
            echo ""
            ./extractTemperatureFromLoraWan.sh -e
            ;;
    esac
done
if [ $OPTIND -eq 1 ]; then
    usage
fi
