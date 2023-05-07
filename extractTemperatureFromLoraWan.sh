#!/bin/bash
#-----------Auther: Hassan Al Achek-----------#

function usage {
    echo "[?] Help Menu"
    echo -e "-h: help \n-d: script description \n-p: to specify the data directory"
    echo ""
    echo "Usage: $0 -e"
}

function scriptDescription {
    echo "[?] Description:
        This script take a path to a directory that contains all 
        LoRaWanData_*_knx_raw.csv files and extract temperatures available on each file"
}

function getAllLoraWanFiles {
    echo "[+] Getting all LoraWan collected files"
    # files=$(ls LoraWan | grep "LoRaWanData_[[:digit:]]_knx_raw\.csv$")
    files=$(ls LoraWan)
}

#-- To be completed --#
function getAllLoraWanJsonFiles {
    echo "[+] Getting all LoraWan json files"
    echo "[+] Reading from the following directory: $1"
    jsonFiles=$(ls LoraWan | grep "LoRaWanData_[[:digit:]]_knx_raw\.json$")
    
    for jsonFile in jsonFiles
    do
       echo "Not Finished" 
    done
}

function extractLoraData {
    totalNumOfFiles=$(echo $files | tr " " "\n" | wc -l)
    for file in $files
    do
        jsonData=$(cat LoraWan/$file | cut -d"\"" -f2- | sed 's/.$//')
        echo $jsonData > LoraWan/${file%.csv}.json
        echo "LoraWan/${file%.csv}.json"
    done | pv -l -s "$totalNumOfFiles" > /dev/null

}


while getopts "hde" opt
do
    case "${opt}" in
        h)
            usage
            ;;
        d)
            scriptDescription
            ;;
        e)
            # Global Variables
            set files
            # set jsonFiles
            getAllLoraWanFiles 
            extractLoraData
            ;;
    esac
done

