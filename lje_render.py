"""Page rendering for 簡単に日本語を学ぶ (page-3 parchment style and page-2 grey vertical style).
Every page is 1200x1800; renderers return (PIL.Image RGB, hotspots[(x0,y0,x1,y1,action)]).
(c)2026 EX Inc./HYPERION DIGITAL (c)2026"""
import os, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import lje_data as D
import lje_lang as L

W, H = 1200, 1800
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
A = lambda *p: os.path.join(BASE, "assets", *p)
INK = (48, 26, 18); BROWN = (96, 58, 34); ORANGE = (205, 128, 58); OUTLINE = (52, 28, 16)
COPY = "©2026 EX Inc./HYPERION DIGITAL ©2026"
_f = {}


def font(size, kind="jp"):
    k = (size, kind)
    if k not in _f:
        _f[k] = ImageFont.truetype(A("NotoSansJP-Bold-subset.otf" if kind == "jp" else "IBMPlexSerif-SemiBoldItalic.ttf"), size)
    return _f[k]


_bg = {}


def parchment():
    if "p" not in _bg: _bg["p"] = Image.open(A("parchment.jpg")).convert("RGB").resize((W, H))
    return _bg["p"].copy()


def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]


def center(d, y, s, f, fill=INK, x0=0, x1=W, **kw):
    d.text(((x0 + x1 - tw(d, s, f)) // 2, y), s, font=f, fill=fill, **kw)


def footer(d, n=None):
    f = font(22, "rm")
    if n: center(d, 1668, "— %d —" % n, font(26, "rm"), BROWN)
    center(d, 1712, COPY, f, (120, 92, 70))


# ---------------------------------------------------------------------------- ruby text
def ruby_layout(d, markup, size):
    """-> list of (x, text, ruby) and total width; words joined without spaces"""
    f = font(size); rf = font(max(14, int(size * .34)))
    items = []; x = 0
    for w in L.parse(markup):
        for t, r in w:
            bw = tw(d, t, f); rw = tw(d, r, rf) if r else 0
            cw = max(bw, rw + 4)
            items.append((x + (cw - bw) / 2, t, r, x + (cw - rw) / 2, bw)); x += cw
    return items, x


def draw_ruby(d, x, y, markup, size, fill=INK, orange=False, ruby_fill=INK, max_w=None):
    while True:
        items, total = ruby_layout(d, markup, size)
        if not max_w or total <= max_w or size < 30: break
        size = int(size * .9)
    f = font(size); rf = font(max(14, int(size * .34)))
    if x == "c": x = (W - total) / 2
    for bx, t, r, rx, bw in items:
        bx += x; rx += x
        if r: d.text((rx, y), r, font=rf, fill=ruby_fill)
        if orange:
            d.text((bx, y + size * .42), t, font=f, fill=ORANGE, stroke_width=max(3, size // 22), stroke_fill=OUTLINE)
        else:
            d.text((bx, y + size * .42), t, font=f, fill=fill)
    return total, size


def kana_with_romaji(d, x, y, kana, size):
    """orange outlined kana line with romaji above each mora (the page-3 orange line, made correct)"""
    f = font(size); rf = font(max(18, int(size * .36)), "rm")
    morae = []; i = 0; k = kana.replace(" ", "")
    while i < len(k):
        c = k[i]
        if i + 1 < len(k) and k[i + 1] in "ゃゅょャュョぁぃぅぇぉァィゥェォ": c += k[i + 1]; i += 1
        elif i + 1 < len(k) and k[i + 1] == "ー": c += "ー"; i += 1
        morae.append(c); i += 1
    widths = [max(tw(d, m, f), tw(d, L.romaji(m, macrons=False) if m not in "っッ" else "·", rf)) + 6 for m in morae]
    total = sum(widths)
    if total > W - 200:
        return kana_with_romaji(d, x, y, kana, int(size * .85))
    if x == "c": x = (W - total) / 2
    for m, cw in zip(morae, widths):
        r = "·" if m in "っッ" else L.romaji(m, macrons=False)
        d.text((x + (cw - tw(d, r, rf)) / 2, y), r, font=rf, fill=INK)
        d.text((x + (cw - tw(d, m, f)) / 2, y + size * .45), m, font=f, fill=ORANGE, stroke_width=max(3, size // 22), stroke_fill=OUTLINE)
        x += cw
    return total


# ---------------------------------------------------------------------------- page kinds
def header(d, en, jp):
    center(d, 112, jp, font(44), BROWN)
    center(d, 168, en.upper(), font(30, "rm"), BROWN)
    d.line((380, 214, 820, 214), fill=(150, 110, 80), width=2)


def learning_page(markup, romaji, english, orange=True, n=None, tag=None, brush=None):
    """the page-3 look: big word with furigana, orange kana line, romaji + English"""
    im = parchment(); d = ImageDraw.Draw(im)
    if tag: center(d, 112, tag, font(30, "rm"), BROWN)
    draw_ruby(d, "c", 300, markup, 190, max_w=980)
    if orange:
        kana = L.reading(markup).replace("、", "").replace("。", "")
        kana_with_romaji(d, "c", 720, kana, 150)
    center(d, 1110, romaji, font(64, "rm"), INK)
    f = font(56)
    lines = wrap(d, english, f, 960)
    for i, ln in enumerate(lines[:4]): center(d, 1230 + i * 78, ln, f, BROWN)
    if brush is not None: im.paste(brush, (0, 0), brush)
    footer(d, n)
    return im, [(100, 260, 1100, 1060, ("say", L.plain(markup)))]


def wrap(d, s, f, w):
    out = []; cur = ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if tw(d, t, f) > w and cur: out.append(cur); cur = word
        else: cur = t
    return out + ([cur] if cur else [])


def word_page(cat, jp, items, n):
    im = parchment(); d = ImageDraw.Draw(im); hs = []
    header(d, cat, jp)
    y = 250
    for mk, rm, en in items:
        draw_ruby(d, 130, y, mk, 108, max_w=560)
        d.text((720, y + 54), rm, font=font(44, "rm"), fill=INK)
        for i, ln in enumerate(wrap(d, en, font(34), 380)[:2]): d.text((720, y + 112 + i * 44), ln, font=font(34), fill=BROWN)
        d.text((1050, y + 66), "♪", font=font(40), fill=(160, 110, 70))
        hs.append((110, y, 1100, y + 250, ("say", L.plain(mk))))
        d.line((160, y + 262, 1040, y + 262), fill=(190, 160, 130), width=2)
        y += 280
    footer(d, n)
    return im, hs


def kana_chart(katakana, n):
    im = parchment(); d = ImageDraw.Draw(im); hs = []
    header(d, "Katakana chart" if katakana else "Hiragana chart", "カタカナ" if katakana else "ひらがな")
    cw, ch = 188, 124; x0, y0 = (W - 5 * cw) // 2, 240
    fk, fr = font(76), font(34, "rm")
    for r, row in enumerate(D.GOJUON):
        for c, cell in enumerate(row):
            if not cell: continue
            k, rm = cell; k = D.kata(k) if katakana else k
            x, y = x0 + c * cw, y0 + r * ch
            d.rounded_rectangle((x + 8, y + 6, x + cw - 8, y + ch - 6), 14, outline=(196, 164, 130), width=2)
            d.text((x + 22, y + 8), k, font=fk, fill=ORANGE if r % 2 == 0 else INK, stroke_width=3 if r % 2 == 0 else 0, stroke_fill=OUTLINE)
            d.text((x + cw - 18 - tw(d, rm, fr), y + ch - 52), rm, font=fr, fill=BROWN)
            hs.append((x, y, x + cw, y + ch, ("say", k)))
    footer(d, n)
    return im, hs


GREY = (128, 121, 112); GREY_INK = (24, 22, 20)


def grey_frame(title, sub):
    im = Image.new("RGB", (W, H), GREY); d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for _ in range(9000):  # paper grain
        x, y = rnd.randrange(W), rnd.randrange(H); v = rnd.randint(-10, 10)
        d.point((x, y), fill=tuple(max(0, min(255, c + v)) for c in GREY))
    d.rectangle((40, 40, W - 40, H - 40), outline=GREY_INK, width=5)
    d.rectangle((52, 52, W - 52, H - 52), outline=GREY_INK, width=1)
    center(d, 70, title, font(46), GREY_INK); center(d, 128, sub, font(26, "rm"), GREY_INK)
    d.line((52, 176, W - 52, 176), fill=GREY_INK, width=3)
    return im, d


def kana_reference(n):
    """grey vertical page: gojuon read top-to-bottom, columns right-to-left, hiragana big, katakana above, romaji below"""
    im, d = grey_frame("五十音 ごじゅうおん — Kana reference", "Columns top to bottom, right to left · big: hiragana · above: katakana · below: romaji")
    hs = []; cols = len(D.GOJUON); cw = (W - 140) / cols; ch = 290; y0 = 200
    fb, fs, fr = font(84), font(30), font(24, "rm")
    for c, row in enumerate(D.GOJUON):
        x = W - 70 - (c + 1) * cw
        for r, cell in enumerate(row):
            if not cell: continue
            k, rm = cell; y = y0 + r * ch
            cx = x + cw / 2
            d.text((cx - tw(d, D.kata(k), fs) / 2, y + 8), D.kata(k), font=fs, fill=GREY_INK)
            d.text((cx - tw(d, k, fb) / 2, y + 44), k, font=fb, fill=GREY_INK)
            rr = rm.split(" ")[0]
            d.text((cx - tw(d, rr, fr) / 2, y + 168), rr, font=fr, fill=GREY_INK)
            hs.append((x, y, x + cw, y + ch - 60, ("say", k)))
        if c: d.line((x + cw, 196, x + cw, 1640), fill=(70, 66, 60), width=1)
    d.line((52, 1650, W - 52, 1650), fill=GREY_INK, width=3)
    center(d, 1668, "ん (n) stands alone.  を is read \"o\" as a particle.  Add ゛ for g/z/d/b and ゜ for p: か→が, は→ば→ぱ", font(24, "rm"), GREY_INK)
    center(d, 1708, "— %d —   %s" % (n, COPY), font(20, "rm"), GREY_INK)
    return im, hs


def kanji_reference(n):
    im, d = grey_frame("漢字 かんじ — Beginner kanji", "Columns right to left · above: kun・ON reading (ON in katakana) · below: meaning")
    hs = []; per_col = 4; ncol = 6; cw = (W - 140) / ncol; ch = 300; y0 = 200
    fb, fs, fr = font(110), font(28), font(26, "rm")
    for i, (k, rd, en) in enumerate(D.KANJI):
        c, r = divmod(i, per_col)
        x = W - 70 - (c + 1) * cw; y = y0 + r * ch; cx = x + cw / 2
        d.text((cx - tw(d, rd, fs) / 2, y + 6), rd, font=fs, fill=GREY_INK)
        d.text((cx - tw(d, k, fb) / 2, y + 40), k, font=fb, fill=GREY_INK)
        d.text((cx - tw(d, en, fr) / 2, y + 196), en, font=fr, fill=GREY_INK)
        hs.append((x, y, x + cw, y + ch - 40, ("say", "kanji:" + k)))
    for c in range(1, ncol): d.line((W - 70 - c * cw, 196, W - 70 - c * cw, 1400), fill=(70, 66, 60), width=1)
    d.line((52, 1410, W - 52, 1410), fill=GREY_INK, width=3)
    center(d, 1428, "Words made from these kanji", font(28, "rm"), GREY_INK)
    x = 110
    for mk, rm, en in D.KANJI_WORDS:
        y = 1480; wdt, _ = draw_ruby(d, x, y, mk, 58, fill=GREY_INK, ruby_fill=GREY_INK)
        d.text((x, y + 128), rm + " · " + en, font=font(20, "rm"), fill=GREY_INK)
        hs.append((x, y, x + max(wdt, 180), y + 160, ("say", L.plain(mk))))
        x += max(wdt, 170) + 34
    center(d, 1708, "— %d —   %s" % (n, COPY), font(20, "rm"), GREY_INK)
    return im, hs


def quiz_page(title, qs, n, key):
    """qs: list of (prompt_markup_or_text, options[4], correct_index, hint)"""
    im = parchment(); d = ImageDraw.Draw(im); hs = []
    header(d, title, "クイズ")
    y = 250
    for qi, (prompt, opts, ok, hint) in enumerate(qs):
        d.text((120, y + 10), "%d." % (qi + 1), font=font(44, "rm"), fill=BROWN)
        draw_ruby(d, 200, y - 10, prompt, 96, max_w=860)
        d.text((200, y + 150), hint, font=font(28, "rm"), fill=BROWN)
        bw = 228; bx = 130
        for oi, o in enumerate(opts):
            x = bx + oi * (bw + 14); r = (x, y + 200, x + bw, y + 280)
            d.rounded_rectangle(r, 18, fill=(240, 228, 206), outline=(150, 110, 80), width=3)
            f = font(36 if len(o) < 10 else 28)
            d.text((x + (bw - tw(d, o, f)) / 2, y + 218), o, font=f, fill=INK)
            hs.append(r + (("quiz", "%s.%d" % (key, qi), oi, oi == ok),))
        y += 345
    center(d, 1630, "Tap an answer.  ○ = correct,  × = try again.", font(28), BROWN)
    footer(d, n)
    return im, hs


def make_quizzes():
    rnd = random.Random(2026); kana = [c for row in D.GOJUON for c in row if c]
    def opts(right, pool):
        o = rnd.sample([p for p in pool if p != right], 3) + [right]; rnd.shuffle(o); return o, o.index(right)
    q1 = []
    for k, rm in rnd.sample(kana, 4):
        o, i = opts(rm.split(" ")[0], [r.split(" ")[0] for _, r in kana]); q1.append((k, o, i, "Which romaji is this hiragana?"))
    q2 = []
    for k, rm in rnd.sample(kana, 4):
        o, i = opts(D.kata(k), [D.kata(x) for x, _ in kana]); q2.append((k, o, i, "Pick the katakana for the same sound."))
    words = [w for _, _, ws in D.WORDS for w in ws]
    q3 = []
    for mk, rm, en in rnd.sample(words, 4):
        o, i = opts(en.split(" /")[0][:18], [e.split(" /")[0][:18] for _, _, e in words]); q3.append((mk, o, i, "What does it mean?"))
    return [("Quiz 1 · Hiragana", q1), ("Quiz 2 · Katakana", q2), ("Quiz 3 · Words", q3)]


def art(name):
    im = Image.open(A(name)).convert("RGB")
    return im.resize((W, H), Image.LANCZOS), []


def title_page(n):
    im = parchment(); d = ImageDraw.Draw(im)
    draw_ruby(d, "c", 360, "簡単[かんたん]に 日本語[にほんご]を 学[まな]ぶ", 112, max_w=1000)
    center(d, 640, "learn japanese easy", font(78, "rm"), BROWN)
    center(d, 820, "How to use this book", font(44, "rm"), INK)
    tips = ["Small kana above a kanji is furigana: it tells you how to read it.",
            "The orange line spells the word in kana, with romaji above each sound.",
            "Tap a word or a character to hear it (needs a Japanese voice in Windows).",
            "Make your own pages in the Maker and keep them under My Pages."]
    y = 910
    for t in tips:
        for ln in wrap(d, t, font(36), 900): center(d, y, ln, font(36), BROWN); y += 52
        y += 26
    center(d, 1520, "EX Inc.", font(40, "rm"), INK)
    footer(d, n)
    return im, [(200, 340, 1000, 620, ("say", "簡単に日本語を学ぶ"))]


def build_book(my_pages=()):
    """list of (title, section, factory)"""
    P = []
    add = lambda t, s, fn: P.append((t, s, fn))
    add("Front cover", "Covers", lambda n: art("cover.jpg"))
    add("Title & how to use", "Start", title_page)
    add("Kanji & kana art (decorative page)", "Characters", lambda n: art("page2_kanji_art.jpg"))
    add("Kana reference (gojūon)", "Characters", kana_reference)
    add("Kanji reference", "Characters", kanji_reference)
    add("Hiragana chart", "Characters", lambda n: kana_chart(False, n))
    add("Katakana chart", "Characters", lambda n: kana_chart(True, n))
    add("Learning page art (decorative page)", "Words", lambda n: art("page3_learning_art.jpg"))
    for cat, jp, ws in D.WORDS:
        feat = ws[1] if cat == "Greetings" else ws[0]
        add("%s · %s" % (cat, L.plain(feat[0])), "Words", lambda n, f=feat, c=cat: learning_page(f[0], f[1], f[2], n=n, tag=c.upper()))
        add("%s 1-5" % cat, "Words", lambda n, c=cat, j=jp, w=ws[:5]: word_page(c, j, w, n))
        add("%s 6-10" % cat, "Words", lambda n, c=cat, j=jp, w=ws[5:]: word_page(c, j, w, n))
    for i, (t, qs) in enumerate(make_quizzes()):
        add(t, "Quizzes", lambda n, t=t, q=qs, i=i: quiz_page(t, q, n, "q%d" % i))
    for mp in my_pages:
        add("My page · " + (mp.get("english") or L.plain(mp.get("markup", "")) or "untitled")[:28], "My Pages", mp["factory"])
    add("Back cover", "Covers", lambda n: art("back_cover.jpg"))
    return P
