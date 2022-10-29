#!/bin/bash
#-----------Auther: Hassan Al Achek-----------#

function usage {
    echo "[?] Help Menu"
    echo -e "-h: help \n-d: script description \n-p: to specify the data directory"
    echo ""
    echo "Usage: $0 -p </path/to/data/directory>"
    echo "Example: $0 -p ../databat_data/"
}

function scriptDescription {
    echo "[?] Description:
        This script take a path to a directory that contains all 
        *_knx_raw.csv files and extract LoRaWan data"
}

function getAllKNXRawFiles {
    echo "[+] Getting all KNX_raw collected files"
    echo "[+] Reading from the following directory: $1"
    files=$(ls $dataDirectory | grep "[[:digit:]]_knx_raw\.csv$")
}

function lorawanData {
    echo "[+] Get LoRaWan data"
    mkdir LoraWan 2>/dev/null
    totalNumOfFiles=$(echo $files | tr " " "\n" | wc -l)

    for file in $files
    do
        loraData=$(cat "$dataDirectory$file" | grep "LoRaObject" > "LoraWan/LoRaWanData_"$file)
        echo "[+] LoraWan/LoRaWanData_$file done"
    done | pv -l -s "$totalNumOfFiles" > /dev/null
    
    echo "[+] Done, Results saved to $(pwd)/LoraWan"
    tree LoraWan/
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
            # Global Variables
            set files
            getAllKNXRawFiles $dataDirectory
            lorawanData
            ;;
    esac
done

