import zipfile
import xml.etree.ElementTree as ET
import re
import json

docx_path = r'convoai_data/Convoai recordings with transcript.docx'
with zipfile.ZipFile(docx_path) as z:
    xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    for p in tree.iterfind('.//w:p', namespaces):
        texts = [node.text for node in p.iterfind('.//w:t', namespaces) if node.text]
        if texts:
            paragraphs.append(''.join(texts))

full_text = '\n'.join(paragraphs)
urls = re.findall(r'https?://[^\s\"\'\<\>]+\.wav', full_text)
tabs = re.split(r'Tab\s+(\d+)', full_text)
parsed_tabs = []
for i in range(1, len(tabs), 2):
    tab_num = int(tabs[i])
    content = tabs[i+1].strip()
    wav_match = re.search(r'https?://[^\s\"\'\<\>]+\.wav', content)
    wav_url = wav_match.group(0) if wav_match else None
    
    # Extract json objects or message/speaker pairs
    # In the text, turns are formatted as {"message": "...", "speaker": 0/1}
    turns = []
    # Pattern to match message and speaker
    pattern = re.compile(r'\{\s*"message":\s*"(.*?)"\s*,\s*"speaker":\s*(\d+)\s*\}', re.DOTALL)
    for m in pattern.finditer(content):
        turns.append({
            "speaker": int(m.group(2)),
            "speaker_label": "agent" if int(m.group(2)) == 0 else "user",
            "message": m.group(1).replace('\\"', '"')
        })
    
    print(f"Tab {tab_num}: {len(turns)} turns captured, WAV: {wav_url}")
    parsed_tabs.append({
        "tab_id": tab_num,
        "audio_url": wav_url,
        "turns": turns
    })

with open('convoai_data/parsed_calls.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_tabs, f, indent=2)

print(f"\nSuccessfully parsed and saved {len(parsed_tabs)} calls to convoai_data/parsed_calls.json")

