# STEP ZERO: Install Curl, JQ
sudo apt-get install curl jq --yes

# STEP ONE: Extract "token.encoded" from auth token:
TOKEN=$(curl -H "Content-Type: application/json" \
  -X POST \
  -d '{"user":{"email":"skanda03prasad@gmail.com","password":"shaarvarp"}}' \
  https://my.farm.bot/api/tokens | jq ".token.encoded" --raw-output)

# STEP TWO: Download images from /api/images endpoint
mkdir -p downloaded_images
curl -H "Authorization: Bearer ${TOKEN}" https://my.farm.bot/api/images | \
  jq -r '.[] | .attachment_url' | \
  while IFS= read -r url; do
    # Extract the image file name from the URL
    filename=$(basename "${url}")
    # Download the image and save it with the correct extension
    curl -o "downloaded_images/${filename}.jpeg" -J -L -f "${url}"
  done
