"""Offline English -> Japanese (curated phrase table + simple patterns), furigana and romaji.  (c)2026 EX Inc./HYPERION DIGITAL (c)2026"""
import re
import lje_data as D

# ---------------------------------------------------------------------------- markup
def parse(markup):
    """'日本[にほん] が 大好[だいす]き' -> words: list of list of (text, ruby or None)"""
    words = []
    for w in markup.split():
        segs = []; i = 0
        for m in re.finditer(r"([^\[\]]+?)\[([^\]]+)\]", w):
            pre = m.group(1)
            # the ruby belongs to the trailing kanji of pre
            k = len(pre)
            while k > 0 and is_kanji(pre[k - 1]): k -= 1
            if pre[:k]: segs.append((pre[:k], None))
            segs.append((pre[k:] or pre, m.group(2)))
            i = m.end()
        if w[i:]: segs.append((w[i:], None))
        words.append(segs)
    return words


def is_kanji(c):
    return "\u4e00" <= c <= "\u9fff" or c in "々〆ヶ"


def plain(markup):
    return "".join(t for w in parse(markup) for t, _ in w)


def reading(markup):
    return "".join((r or t) for w in parse(markup) for t, r in w)


# ---------------------------------------------------------------------------- romaji (Hepburn)
_R = {}
for row in ("あいうえお", "かきくけこ", "さしすせそ", "たちつてと", "なにぬねの", "はひふへほ", "まみむめも", "や ゆ よ", "らりるれろ", "わ   を"):
    pass
_BASE = dict(zip("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゔ",
                 "a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa o n "
                 "ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo pa pi pu pe po vu".split()))
_SMALL = {"ゃ": "ya", "ゅ": "yu", "ょ": "yo", "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o"}


def hira(s):
    return "".join(chr(ord(c) - 0x60) if "\u30a1" <= c <= "\u30f6" else c for c in s)


MAC = {"a": "ā", "i": "ī", "u": "ū", "e": "ē", "o": "ō"}


def romaji(kana, particle=False, macrons=True):
    r = _romaji(kana, particle)
    if macrons:
        r = re.sub(r"ou(?!$)|oo|ou$", "ō", r) if len(r) > 3 else r
        r = r.replace("uu", "ū")
    return r


def _romaji(kana, particle=False):
    s = hira(kana)
    if s.endswith(("んにちは", "んばんは")): return _romaji(s[:-1]) + "wa"
    if particle and s in ("は", "へ", "を"): return {"は": "wa", "へ": "e", "を": "o"}[s]
    out = []; i = 0; dbl = False
    while i < len(s):
        c = s[i]; nx = s[i + 1] if i + 1 < len(s) else ""
        if c == "っ": dbl = True; i += 1; continue
        if c == "ー":
            if out and out[-1][-1:] in "aeiou": out[-1] = out[-1][:-1] + MAC[out[-1][-1]]
            i += 1; continue
        if c in _BASE and nx in _SMALL:
            b = _BASE[c]
            if nx in "ゃゅょ":
                r = (b[:-1] if b.endswith("i") else b) + ("" if b in ("shi", "chi", "ji") else "") + _SMALL[nx]
                if b in ("shi", "chi", "ji"): r = b[:-1] + _SMALL[nx][1:]
            else:
                r = b[:-1] + _SMALL[nx]
            i += 2
        elif c in _BASE:
            r = _BASE[c]; i += 1
            if c == "ん" and nx and (nx in "あいうえおやゆよ"): r = "n'"
        else:
            r = c; i += 1
        if dbl and r and r[0].isalpha():
            r = ("t" if r.startswith("ch") else r[0]) + r; dbl = False
        out.append(r)
    return "".join(out)


def romaji_markup(markup):
    ws = []
    for w in parse(markup):
        k = "".join((r or t) for t, r in w)
        if k in ("、", "。", "？", "！"): ws.append(",") if k == "、" else ws.append(k.replace("。", ".").replace("？", "?").replace("！", "!")); continue
        ws.append(romaji(k, particle=True))
    s = " ".join(ws).replace(" ,", ",").replace(" ?", "?").replace(" .", ".")
    return s[:1].upper() + s[1:]


# ---------------------------------------------------------------------------- furigana for free text (user edits)
OVERRIDES = {"日本": "にほん", "日本語": "にほんご", "今日": "きょう", "明日": "あした", "昨日": "きのう", "大好": "だいす", "一人": "ひとり",
             "二人": "ふたり", "大人": "おとな", "上手": "じょうず", "下手": "へた", "先生": "せんせい", "学生": "がくせい", "友達": "ともだち"}
_kks = None


def _kakasi():
    global _kks
    if _kks is None:
        import pykakasi
        _kks = pykakasi.kakasi()
    return _kks


def auto_markup(text):
    """plain Japanese -> markup with furigana (curated overrides first, then the offline kakasi dictionary)"""
    text = text.strip()
    if not text: return ""
    parts = []
    toks = []
    for tok in _kakasi().convert(text):
        o, h = tok["orig"], tok["hira"]
        if len(o) > 1 and o[-1] in "はをへ" and is_kanji(o[-2]):
            toks.append({"orig": o[:-1], "hira": h[:-1]}); toks.append({"orig": o[-1], "hira": h[-1]})
        elif toks and o in ("ます", "ました", "ません", "ましょう", "した", "て", "た", "たい") and toks[-1]["orig"] not in "はをへがにでと":
            toks[-1] = {"orig": toks[-1]["orig"] + o, "hira": toks[-1]["hira"] + h}
        else:
            toks.append(tok)
    for tok in toks:
        o, h = tok["orig"], tok["hira"]
        if not any(is_kanji(c) for c in o):
            parts.append(o); continue
        # longest curated override inside the token
        done = False
        for k in sorted(OVERRIDES, key=len, reverse=True):
            if o.startswith(k):
                rest = o[len(k):]
                parts.append(k + "[" + OVERRIDES[k] + "]" + (auto_markup(rest).replace(" ", "") if rest else "")); done = True; break
        if done: continue
        # split okurigana: trailing kana of orig matches trailing kana of reading
        a, b = o, h; tail = ""
        while a and b and not is_kanji(a[-1]) and hira(a[-1]) == b[-1]:
            tail = a[-1] + tail; a = a[:-1]; b = b[:-1]
        head = ""
        while a and b and not is_kanji(a[0]) and hira(a[0]) == b[0]:
            head += a[0]; a = a[1:]; b = b[1:]
        parts.append(head + (a + "[" + b + "]" if a else "") + tail)
    return " ".join(parts)


# ---------------------------------------------------------------------------- English -> Japanese
def _norm(s):
    s = s.lower().strip().replace("’", "'")
    s = re.sub(r"[!?.。！？]+$", "", s).strip()
    return re.sub(r"\s+", " ", s)


def _noun(x):
    x = x.strip()
    x = re.sub(r"^(the|a|an|some|any)\s+", "", x)
    if x.startswith("my "): n = _noun(x[3:]); return None if n is None else "私[わたし] の " + n
    if x.startswith("your "): n = _noun(x[5:]); return None if n is None else "あなた の " + n
    if " and " in x:
        a, b = x.split(" and ", 1); na, nb = _noun(a), _noun(b)
        return None if (na is None or nb is None) else na + " と " + nb
    if x in D.NOUNS: return D.NOUNS[x]
    if x.endswith("s") and x[:-1] in D.NOUNS: return D.NOUNS[x[:-1]]
    w = x.split()
    if len(w) == 2 and w[0] in D.ADJ:
        n = _noun(w[1])
        if n: a = D.ADJ[w[0]]; return a + (" な " if a in D.NA_ADJ else " ") + n
    return None


def translate(english):
    """-> (markup, note).  markup is None when nothing could be translated."""
    s = _norm(english)
    if not s: return None, ""
    if s in D.PHRASES: return D.PHRASES[s], "phrase book"
    m = re.match(r"^(good morning|good evening|good night|hello|hi|goodbye|thank you|thanks),? (.+)$", s)
    if m and _noun(m.group(2)):
        return _noun(m.group(2)) + " 、 " + D.GREETINGS[m.group(1)], "phrase book + dictionary"
    pats = [
        (r"^i (?:really )?love (.+)$", "{} が 大好[だいす]き です"), (r"^i like (.+)$", "{} が 好[す]き です"),
        (r"^i (?:want|would like) (.+)$", "{} が ほしい です"), (r"^(?:please give me|can i have|i'd like) (.+)$", "{} を ください"),
        (r"^(.+) please$", "{} を お願[ねが]い します"), (r"^where is (.+)$", "{} は どこ です か"), (r"^this is (.+)$", "これ は {} です"),
        (r"^that is (.+)$", "それ は {} です"), (r"^i eat (.+)$", "{} を 食[た]べます"), (r"^i drink (.+)$", "{} を 飲[の]みます"),
        (r"^i (?:go|am going) to (.+)$", "{} に 行[い]きます"), (r"^i (?:see|watch) (.+)$", "{} を 見[み]ます"),
        (r"^i read (.+)$", "{} を 読[よ]みます"), (r"^i have (.+)$", "{} が あります"), (r"^my name is (.+)$", "私[わたし] の 名前[なまえ] は {} です"),
        (r"^i am (?:a |an )?(.+)$", "私[わたし] は {} です"), (r"^i'm (?:a |an )?(.+)$", "私[わたし] は {} です"),
    ]
    for p, tpl in pats:
        m = re.match(p, s)
        if not m: continue
        x = m.group(1); n = _noun(x)
        if n is None and x in D.ADJ and "私[わたし] は" in tpl: n = D.ADJ[x]
        if n is None and p.startswith("^my name"): n = x.title()
        if n is not None: return tpl.format(n), "pattern + dictionary"
    m = re.match(r"^(?:the |this |my )?(.+?) (?:is|are) (?:very )?(.+)$", s)
    if m and _noun(m.group(1)) and m.group(2) in D.ADJ:
        return _noun(m.group(1)) + " は " + ("とても " if " very " in " " + s + " " else "") + D.ADJ[m.group(2)] + " です", "pattern + dictionary"
    n = _noun(s)
    if n: return n, "dictionary"
    if s in D.ADJ: return D.ADJ[s], "dictionary"
    # word by word (honest: rough)
    out = []; miss = []
    for w in s.split():
        j = D.NOUNS.get(w) or D.ADJ.get(w) or (D.PHRASES.get(w))
        if j: out.append(j)
        else: miss.append(w)
    if out and not miss: return " ".join(out), "word by word - check the grammar"
    return None, "not in the offline dictionary: %s - type the Japanese yourself" % ", ".join(miss or [s])
