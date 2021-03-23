
# To download all files in a flat folder, such as the PROMICE IV product
# https://doi.org/10.22008/promice/data/sentinel1icevelocity/greenlandicesheet
export SERVER=https://dataverse01.geus.dk
export DOI=10.22008/promice/data/sentinel1icevelocity/greenlandicesheet # <-- CUSTOMIZE THIS

curl ${SERVER}/api/datasets/:persistentId?persistentId=doi:${DOI} > dv.json
cat dv.json | tr ',' '\n' | grep -E '"persistentId"' | cut -d'"' -f4 > urls.txt
while read -r PID; do
    curl -O -J $SERVER/api/access/datafile/:persistentId?persistentId=${PID}
done < urls.txt
rm dv.json urls.txt # cleanup



# To download all files in a nested folder structure, such as the PROMICE freshwater runoff product
# https://doi.org/10.22008/FK2/AA6MTB
export SERVER=https://dataverse01.geus.dk
export DOI=10.22008/FK2/AA6MTB  # <-- CUSTOMIZE THIS

curl ${SERVER}/api/datasets/:persistentId?persistentId=doi:${DOI} > dv.json
cat dv.json | tr ',' '\n' | grep -E '"persistentId"|"directoryLabel"|"filename"' | cut -d'"' -f4 > urls.txt
while read -r dir; do
    mkdir -p ${dir}
    read -r FILE_DOI
    read -r fname
    curl $SERVER/api/access/datafile/:persistentId?persistentId=${FILE_DOI} -o ${dir}/${fname}
done < urls.txt
rm dv.json urls.txt # cleanup
