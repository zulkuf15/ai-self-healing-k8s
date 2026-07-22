import json
import re


def extract_json(text: str) -> dict | None:
    """
    LLM'ler bazen JSON'u ```json ... ``` bloguna sarar ya da oncesine/sonrasina
    aciklama metni ekler. Bu fonksiyon, metindeki ilk gecerli JSON nesnesini
    cikarmaya calisir.
    """
    # once dogrudan parse dene
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # kod bloklarini temizle
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # metin icindeki ilk { ... } bloğunu regex ile bul
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None
