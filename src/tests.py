from jamdict import Jamdict

jam = Jamdict()
result = jam.lookup("食べる")

for entry in result.entries:
    for sense in entry.senses:
        # Extract Spanish glosses ('spa')
        spa_meanings = [g.text for g in sense.gloss if g.lang == 'spa']
        eng_meanings = [g.text for g in sense.gloss if g.lang == 'eng']
        
        # Fallback logic: prefer Spanish, default to English
        final_meanings = spa_meanings if spa_meanings else eng_meanings
        print(f"[{'SPA' if spa_meanings else 'ENG'}]", ", ".join(final_meanings))