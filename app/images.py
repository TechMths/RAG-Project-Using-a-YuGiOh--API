from base.processing.processor import load_cards

a = load_cards()

# primeiro nome
# 0 para entrar na lista

print(dict(a["name"]))
print(a[1]["card_images"][0]["image_url"])
