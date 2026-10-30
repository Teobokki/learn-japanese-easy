"""Pre-generate the book's Japanese audio offline with Open JTalk (pyopenjtalk) -> assets/audio/*.wav + index.json"""
import json, os, wave, hashlib, sys
import numpy as np, pyopenjtalk
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lje_data as D, lje_lang as L, lje_render as R

OUT = "assets/audio"; os.makedirs(OUT, exist_ok=True)
items = {}  # key -> text to speak (kana when the reading must be exact)
for row in D.GOJUON:
    for c in row:
        if c: items[c[0]] = c[0]; items[D.kata(c[0])] = c[0]
for _, _, ws in D.WORDS:
    for mk, _, _ in ws: items[L.plain(mk)] = L.reading(mk)
for mk, _, _ in D.KANJI_WORDS: items[L.plain(mk)] = L.reading(mk)
for v in list(D.PHRASES.values()) + list(D.NOUNS.values()) + list(D.ADJ.values()): items[L.plain(v)] = L.reading(v)
for t, qs in R.make_quizzes():
    for p, *_ in qs: items.setdefault(L.plain(p), L.reading(p))
for k, rd, en in D.KANJI: items["kanji:" + k] = L.hira(rd.replace("・", "、"))
items["簡単に日本語を学ぶ"] = "かんたんににほんごをまなぶ"
index = {}
for key, say in items.items():
    say = say.replace(" ", "")
    if len(say) == 1: say = say + "。"
    name = hashlib.md5(key.encode()).hexdigest()[:12] + ".wav"
    if not os.path.exists(os.path.join(OUT, name)):
        x, sr = pyopenjtalk.tts(say)
        x = np.clip(x / max(1.0, np.abs(x).max()) * 30000, -32768, 32767).astype(np.int16)
        x = x[::3]  # 48k -> 16k
        nz = np.where(np.abs(x) > 300)[0]
        if len(nz): x = x[max(0, nz[0] - 800): nz[-1] + 1600]
        with wave.open(os.path.join(OUT, name), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(x.tobytes())
    index[key] = name
json.dump(index, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(index), sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)) // 1024, "KB")
