# STEP ZERO: Install Curl, JQ
sudo apt-get install curl jq --yes

# STEP ONE: Extract "token.encoded" from auth token:
TOKEN=$(curl -H "Content-Type: application/json" \
  -X POST \
  -d '{"user":{"email":"skanda03prasad@gmail.com","password":"shaarvarp"}}' \
  https://my.farm.bot/api/tokens | jq ".token.encoded" --raw-output)

# STEP TWO: Get the number of objects from coordinates.json
NUM_OBJECTS=$(jq length locations.json)

# STEP THREE: Download images
mkdir -p downloaded_images

curl -H "Authorization: Bearer ${TOKEN}" https://my.farm.bot/api/images | \
  jq -r --argjson num "$NUM_OBJECTS" 'sort_by(.created_at) | reverse | limit($num; .[]) | [.created_at, .attachment_url] | @tsv' | \
  while IFS=$'\t' read -r timestamp url; do
    # Convert timestamp to a filename-friendly format
    filename=$(date -d "$timestamp" +"%Y-%m-%d_%H-%M-%S")

    # Check if the file already exists in the folder
    if [ ! -f "downloaded_images/${filename}.jpeg" ]; then
      # Download the image and save it with the timestamp as its filename
      curl -o "downloaded_images/${filename}.jpeg" -J -L -f "$url"
      echo "Downloaded: ${filename}.jpeg"
    else
      echo "File ${filename}.jpeg already exists, skipping download."
    fi
  done