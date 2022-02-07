#/bin/sh

read -p 'Bucket: ' bucket

curl https://data.cityofchicago.org/api/views/ijzp-q8t2/rows.csv?accessType=DOWNLOAD | \
awk -vFPAT='([^,]*)|("[^"]+")' -vOFS=, '
FNR==1 { hdr=$0; next }
{
    dir = "crimes/district_"$12
    out = dir"/LOAD00000001.csv"
    if (!seen[out]++) {
        "mkdir -p "dir | getline
        print hdr > out
    }
    print >> out
    close(out)
}'

rm -rf crimes/district_
aws s3 cp --recursive crimes/ s3://$bucket/crimes/