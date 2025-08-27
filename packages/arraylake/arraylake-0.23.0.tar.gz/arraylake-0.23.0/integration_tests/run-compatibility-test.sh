export AWS_ACCESS_KEY_ID=minio123
export AWS_SECRET_ACCESS_KEY=minio123
export AWS_SECRET_ACCESS_KEY=minio123
export AWS_ENDPOINT_URL_S3=http://localhost:9000

# AWS_ACCESS_KEY_ID=minio123 AWS_SECRET_ACCESS_KEY=minio123 aws s3 --endpoint-url http://localhost:9000 cp ./small.nc s3://arraylake-repo-bucket/
set -e

RANDOMIZER=$(openssl rand -hex 3)
NEW_CLIENT=/Users/oli/dev/earthmover/arraylake/client
OLD_CLIENT=/tmp/test-al-clients/al-old-client

####
# "TEST MATERIALIZED OLD -> NEW"
###
echo "TEST MATERIALIZED OLD -> NEW"
echo -e "\n*write old from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    write-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*read old from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*read old from new"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*append old from new"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    append-old-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*read old from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER


####
# TEST MATERIALIZED NEW -> OLD
###
echo -e "\n\nTEST MATERIALIZED NEW -> OLD"
RANDOMIZER=$(openssl rand -hex 3)
echo -e "\n*write new from new"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    write-new-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER test

echo -e "\n*read new from new"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    read-new-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER

echo -e "\n*read new from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-new-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER

echo -e "\n*append new from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    append-new-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER

####
# TEST MATERIALIZED NEW (old style chunkstore) -> OLD
###
echo -e "\n\nTEST MATERIALIZED NEW (old style chunkstore) -> OLD"

RANDOMIZER=$(openssl rand -hex 3)
echo -e "\n*write old from new"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    write-old-chunkstore-from-new-client \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*read old from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*append old from old"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    append-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

echo -e "\n*read appended old from new"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER

####
# TEST VIRTUAL: OLD -> NEW
###
echo -e "\n\nTEST VIRTUAL: OLD -> NEW"
RANDOMIZER=$(openssl rand -hex 3)
echo -e "\nwrite old from old - virtual"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    write-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER --virtual

echo -e "\n*read old from old - virtual"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER --virtual

echo -e "\n*read old from new - virtual"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER --virtual

####
# TEST INLINE: OLD -> NEW
###
echo -e "\n\nTEST INLINE: OLD -> NEW"
RANDOMIZER=$(openssl rand -hex 3)
echo -e "\nwrite old from old - inline"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    write-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER --inline

echo -e "\n*read old from old - inline"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER --inline

echo -e "\n*read old from new - inline"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    read-old-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER $RANDOMIZER --inline


####
# TEST VIRTUAL: NEW -> OLD
###
echo -e "\n\nTEST VIRTUAL: NEW -> OLD"
RANDOMIZER=$(openssl rand -hex 3)
echo -e "\n*write new from new - virtual"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    write-new-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER test --virtual

echo -e "\n*read new from new - virtual"
poetry --directory $NEW_CLIENT \
    run python integration_tests/intercompat.py \
    read-new-client-chunkstore-from-new \
    bucketty/test-chunkstore-versions-$RANDOMIZER --virtual

echo -e "\n*read new from old - virtual"
poetry --directory $OLD_CLIENT \
    run python integration_tests/intercompat.py \
    read-new-client-chunkstore-from-old \
    bucketty/test-chunkstore-versions-$RANDOMIZER --virtual
