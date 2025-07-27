from tcgdexsdk import TCGdex
import json

def make_serializable(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return str(obj)
    seen.add(obj_id)

    if isinstance(obj, dict):
        return {k: make_serializable(v, seen) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [make_serializable(i, seen) for i in obj]
    elif hasattr(obj, '__dict__'):
        return make_serializable(vars(obj), seen)
    elif hasattr(obj, '_asdict'):
        return make_serializable(obj._asdict(), seen)
    elif isinstance(obj, str):
        return obj.replace("\u00d7", "x")  # Replace Unicode multiply with ASCII x
    elif isinstance(obj, (int, float, bool, type(None))):
        return obj
    else:
        return str(obj)


# Initialize TCGdex for English
tcgdex = TCGdex("en")

tcgendpoint = tcgdex.getEndpoint()
print(f"endpoint: {tcgendpoint}")
tcgsets = tcgdex.set.listSync()
print(f"sets: {tcgsets}")

for tcgset in tcgsets:
    print("---------------------------------------------------")
    print(f"Set: {tcgset.name} ({tcgset.id})")

tcgset = tcgdex.set.getSync("base1")  # Example for Base Set
print(f"Set: {tcgset})")
tcgcard_resumes = tcgset.cards
print(f"card_resumes: {tcgcard_resumes})")
tcgdeck = []
for card_resume in tcgcard_resumes:
    print(f"Card: {card_resume.name} ({card_resume.id})")
    data = tcgdex.card.getSync(card_resume.id)
    # Use attribute access directly, as tcgdexsdk card objects typically use attributes, not dict keys.
    card = {
        "rarity": getattr(data, "rarity", None),
        "category": getattr(data, "category", None),
        "set": getattr(data.set, "id", None) if hasattr(data, "set") else None,
        "hp": getattr(data, "hp", None),
        "types": getattr(data, "types", None),
        "evolvesFrom": getattr(data, "evolvesFrom", None),
        "description": getattr(data, "description", None),
        "level": getattr(data, "level", None),
        "stage": getattr(data, "stage", None),
        "suffix": getattr(data, "suffix", None),
        "item": getattr(data, "item", None),
        "abilities": getattr(data, "abilities", None),
        "attacks": getattr(data, "attacks", None),
        "weaknesses": getattr(data, "weaknesses", None),
        "resistances": getattr(data, "resistances", None),
        "retreat": getattr(data, "retreat", None),
        "effect": getattr(data, "effect", None),
        "trainerType": getattr(data, "trainerType", None),
        "energyType": getattr(data, "energyType", None),
        "regulationMark": getattr(data, "regulationMark", None),
        "id": getattr(data, "id", None),
        "localId": getattr(data, "localId", None),
        "name": getattr(data, "name", None),
        "image": getattr(data, "image", None),
        "boosters": getattr(data, "boosters", None),
    }
    tcgdeck.append(make_serializable(card))

with open("assets/deck.json", "w", encoding="utf-8") as f:
    json.dump(tcgdeck, f, ensure_ascii=False, indent=2)