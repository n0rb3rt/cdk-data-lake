#/bin/sh

echo "Download Chicago crimes data and split it into files by district"
read -p 'Bucket: ' bucket

curl https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv?accessType=DOWNLOAD | \
sudo awk -vFPAT='([^,]*)|("[^"]+")' -vOFS=, '
FNR==1 { hdr=$0; next }
{
    dir = "crimes/precinct="$12
    out = dir"/LOAD00000001.csv"
    if (!seen[out]++) {
        "sudo mkdir -p "dir | getline
        print hdr > out
    }
    print >> out
    close(out)
}'

sudo rm -rf crimes/precinct=
aws s3 cp --recursive crimes/ s3://$bucket/crimes/