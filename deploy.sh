echo "Removing old builds:"
rm -rf .build

echo "Compile runtime code to build folder:"
mkdir -p .build/clustering
mkdir -p .build/postprocess
mkdir -p .build/preprocess

tar -czf ./.build/clustering/clustering.tar.gz -C ./src/cluster .
cp src/postprocess/merge.py ./.build/postprocess/merge.py
cp -R src/preprocess ./.build

echo "Validate and build SAM templates:"
sam validate
sam build

FILE=./samconfig.toml
if [ -f "$FILE" ]; then
    echo "Continuing with existing deployment from $FILE:"
    sam deploy --capabilities=CAPABILITY_NAMED_IAM
else
    echo "Starting a new guided deployment:"
    sam deploy --guided --capabilities=CAPABILITY_NAMED_IAM
fi

echo "Deploy runtime code to Amazon S3:"
bucket=$(awk -F '"' '/PinpointRFMS3BucketName/{print $3}' samconfig.toml | sed 's/\\//g')
echo $bucket
aws s3 cp ./.build "s3://${bucket}/code" --recursive

echo "Done."
