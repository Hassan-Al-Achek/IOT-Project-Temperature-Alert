#!/bin/bash

function usage {
    echo "[?] Help:"
    echo "./$0 -p <path/to/data>"
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
            ./extractTemperatureFromLoraWan.sh -p $dataDirectory
            ;;
    esac
done
