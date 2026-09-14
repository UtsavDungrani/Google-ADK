import os
import glob
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def parse_docx_call_samples(
    source_dir: str = os.path.expanduser("~/Downloads/archive (1)/Call center data samples"),
    output_path: str = "callcenter_archive_eval/data/parsed_calls.json"
) -> List[Dict[str, Any]]:
    print(f"Parsing call recordings and transcripts from: {source_dir}")
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    folders = sorted(os.listdir(source_dir))
    parsed_calls = []

    for idx, folder in enumerate(folders, 1):
        folder_path = os.path.join(source_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        docxs = glob.glob(os.path.join(folder_path, "*.docx"))
        mp3s = glob.glob(os.path.join(folder_path, "*.mp3"))

        if not docxs:
            continue

        docx_path = docxs[0]
        mp3_path = mp3s[0] if mp3s else None

        # Extract folder metadata (ID and Tag from name like: "1735404531.458927 (EN customer support )")
        folder_match = re.match(r"^([\d\.]+)\s*\((.*?)\)", folder)
        if folder_match:
            call_id = folder_match.group(1).strip()
            call_tag = folder_match.group(2).strip()
        else:
            call_id = folder.split()[0]
            call_tag = folder

        # Parse DOCX paragraphs
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paras = []
            for p in tree.iterfind(".//w:p", namespaces):
                texts = [node.text for node in p.iterfind(".//w:t", namespaces) if node.text]
                if texts:
                    paras.append("".join(texts).strip())
            paras = [p for p in paras if p]

        # Extract Summary/Metadata Sections
        metadata: Dict[str, Any] = {
            "call_id": call_id,
            "call_tag": call_tag,
            "folder_name": folder,
            "audio_file": os.path.basename(mp3_path) if mp3_path else "",
            "audio_path": mp3_path or "",
            "docx_file": os.path.basename(docx_path)
        }

        known_sections = [
            "Conversation type", "Key points", "Customer sentiment", "Next steps",
            "Primary purpose", "Main topics", "Customer problems", "Key action items",
            "Business opportunities", "Risks"
        ]

        trans_start_idx = None
        for i, p in enumerate(paras):
            p_lower = p.lower()
            if any(k in p_lower for k in ["en transcription", "english transcription", "english translation", "transcription"]):
                trans_start_idx = i
                break
            if re.match(r"^\d\d:\d\d:\d\d", p):
                trans_start_idx = i
                break

        meta_paras = paras[:trans_start_idx] if trans_start_idx is not None else paras
        trans_paras = paras[trans_start_idx:] if trans_start_idx is not None else []

        current_section = None
        section_content: List[str] = []
        for p in meta_paras:
            matched_header = None
            for sec in known_sections:
                if p.strip().lower() == sec.lower() or p.strip().lower().startswith(sec.lower() + ":"):
                    matched_header = sec
                    break
            
            if matched_header:
                if current_section and section_content:
                    metadata[current_section] = " ".join(section_content).strip()
                current_section = matched_header
                if ":" in p:
                    inline = p.split(":", 1)[1].strip()
                    section_content = [inline] if inline else []
                else:
                    section_content = []
            elif current_section:
                section_content.append(p)

        if current_section and section_content:
            metadata[current_section] = " ".join(section_content).strip()

        # Parse Turns from trans_paras
        turns = []
        curr_time = None
        curr_speech = []

        for p in trans_paras:
            if any(p.lower().startswith(x) for x in ["ru transcription", "pl transcription", "fr transcription", "de transcription", "ge transcription", "es transcription", "portuguese transcription", "original transcription"]):
                break
            if "transcription" in p.lower() or "translation" in p.lower():
                continue

            ts_match = re.match(r"^(\d\d:\d\d:\d\d)", p.strip())
            if ts_match:
                if curr_time and curr_speech:
                    turns.append({
                        "timestamp": curr_time,
                        "turn_index": len(turns) + 1,
                        "text": " ".join(curr_speech).strip()
                    })
                curr_time = ts_match.group(1)
                curr_speech = []
            else:
                if curr_time:
                    curr_speech.append(p.strip())

        if curr_time and curr_speech:
            turns.append({
                "timestamp": curr_time,
                "turn_index": len(turns) + 1,
                "text": " ".join(curr_speech).strip()
            })

        first_text = turns[0]["text"].lower() if turns else ""
        agent_starts = False
        if any(w in first_text for w in ["i'm calling", "this is", "calling from", "my name is"]):
            agent_starts = True

        for i, t in enumerate(turns):
            if agent_starts:
                t["speaker_role"] = "AGENT" if i % 2 == 0 else "CUSTOMER"
            else:
                t["speaker_role"] = "CUSTOMER" if i % 2 == 0 else "AGENT"

        call_record = {
            "index": idx,
            "call_id": call_id,
            "call_tag": call_tag,
            "metadata": metadata,
            "turn_count": len(turns),
            "turns": turns,
            "audio_file": metadata.get("audio_file"),
            "audio_path": metadata.get("audio_path")
        }
        parsed_calls.append(call_record)
        print(f"[{idx}/{len(folders)}] Parsed {call_tag}: {len(turns)} turns, Audio: {metadata.get('audio_file')}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_calls, f, indent=2)

    print(f"\nSuccessfully parsed and saved {len(parsed_calls)} calls to {output_path}!")
    return parsed_calls

if __name__ == "__main__":
    parse_docx_call_samples()
