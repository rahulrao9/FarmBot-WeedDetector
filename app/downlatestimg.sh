# STEP ZERO: Install Curl, JQ
sudo apt-get install curl jq --yes

# STEP ONE: Extract "token.encoded" from auth token:
TOKEN=$(curl -H "Content-Type: application/json" \
  -X POST \
  -d '{"user":{"email":"skanda03prasad@gmail.com","password":"shaarvarp"}}' \
  https://my.farm.bot/api/tokens | jq ".token.encoded" --raw-output)

# STEP TWO: Get the latest image from /api/images endpoint
mkdir -p downloaded_images
latest_image_url=$(curl -H "Authorization: Bearer ${TOKEN}" https://my.farm.bot/api/images | \
  jq -r 'sort_by(.updated_at) | reverse | .[0].attachment_url')

# Extract the image file name from the URL
filename=$(basename "${latest_image_url}")

# Check if the file already exists in the folder
if [ ! -f "downloaded_images/${filename}.jpeg" ]; then
  # Download the latest image and save it with the correct extension
  curl -o "downloaded_images/${filename}.jpeg" -J -L -f "${latest_image_url}"
else
  echo "File ${filename}.jpeg already exists, skipping download."
fi