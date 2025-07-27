import os
import requests

SET_ID = "base1"  # npr. 'base1' za Base Set
DEST_DIR = "assets/cards/images"

os.makedirs(DEST_DIR, exist_ok=True)

# Preuzmi sve karte iz seta base1
response = requests.get(f"https://api.tcgdex.net/v2/en/sets/{SET_ID}")
data = response.json()

cards = data["cards"]

for card in cards:
    name = card["id"]
    image_url = card["image"] + "/high.png"
    image_path = os.path.join(DEST_DIR, f"{name}.png")

    print(f"Downloading {name} from {image_url}...")
    img_data = requests.get(image_url).content
    with open(image_path, "wb") as f:
        f.write(img_data)

print("Gotovo!")
