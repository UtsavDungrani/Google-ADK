import json

with open('convoai_data/parsed_calls.json', 'r', encoding='utf-8') as f:
    calls = json.load(f)

for c in calls:
    print(f"=== Call {c['tab_id']} ({len(c['turns'])} turns) | Audio: {c['audio_url']} ===")
    for turn in c['turns'][:3]:
        print(f"  {turn['speaker_label'].upper()}: {turn['message'][:90]}")
    print("  ...")
    for turn in c['turns'][-2:]:
        print(f"  {turn['speaker_label'].upper()}: {turn['message'][:90]}")
    print()
