"""簡単に日本語を学ぶ — learn japanese easy.  An ebook by EX Inc.
(c)2026 EX Inc./HYPERION DIGITAL (c)2026"""
import json, math, os, sys, time, threading
_V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if os.path.isdir(_V) and not getattr(sys, "frozen", False): sys.path.append(_V)
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFilter
import lje_render as R
import lje_lang as L
import lje_audio as AU

APP = "簡単に日本語を学ぶ — learn japanese easy"
VERSION = "1.0.0"
PAPER, PANEL, PANEL2, INK, OCHRE, RED, LINE = "#efe6d4", "#e2d5bb", "#d6c6a6", "#3a2516", "#b8722f", "#9e2f26", "#b9a37f"
BRUSH_COLOURS = [("Ochre", (196, 126, 52)), ("Brown", (110, 62, 30)), ("Black", (28, 22, 18)), ("Red", (168, 40, 32))]


def data_dir():
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    d = os.path.join(base, "EX Inc", "LearnJapaneseEasy"); os.makedirs(os.path.join(d, "mypages"), exist_ok=True)
    return d


def load_font_windows():
    if os.name != "nt": return
    try:
        import ctypes
        ctypes.windll.gdi32.AddFontResourceExW(R.A("NotoSansJP-Bold-subset.otf"), 0x10, 0)
    except Exception:
        pass


class Btn(tk.Label):
    """flat paper button: no glow, a darker paper tone on hover"""
    def __init__(self, master, text, cmd, bg=PANEL, fg=INK, font=None, padx=12, pady=5, **kw):
        super().__init__(master, text=text, bg=bg, fg=fg, font=font or (UIF, 10, "bold"), padx=padx, pady=pady,
                         cursor="hand2", bd=1, relief="solid", highlightthickness=0, **kw)
        self._bg = bg; self.cmd = cmd
        self.bind("<Enter>", lambda e: self.config(bg=PANEL2)); self.bind("<Leave>", lambda e: self.config(bg=self._bg))
        self.bind("<Button-1>", lambda e: self.cmd())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        load_font_windows()
        self.title(APP); self.configure(bg=PAPER); self.geometry("1180x860"); self.minsize(900, 640)
        try: self.iconbitmap(R.A("icon.ico"))
        except Exception: pass
        self.dir = data_dir(); self.state_path = os.path.join(self.dir, "state.json")
        try: self.st = json.load(open(self.state_path, encoding="utf-8"))
        except Exception: self.st = {}
        self.st.setdefault("page", 0); self.st.setdefault("bookmarks", []); self.st.setdefault("quiz", {})
        global UIF
        fams = set(tkfont.families(self)); fam = next((f for f in ("Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic UI", "Meiryo UI", "MS UI Gothic")
                                                       if f in fams), "TkDefaultFont")
        UIF = fam
        self.F = (fam, 10, "bold"); self.FB = (fam, 13, "bold")
        self.cache = {}; self.vcache = {}; self.cur = 0; self.zoom = 1.0; self.pan = [0, 0]
        self.anim = None; self.drag = None; self.status_after = None
        self.load_book()
        self._build()
        self.show_start()

    # ------------------------------------------------------------------ book
    def my_pages(self):
        out = []; root = os.path.join(self.dir, "mypages")
        for pid in sorted(os.listdir(root)):
            p = os.path.join(root, pid, "page.json")
            try: d = json.load(open(p, encoding="utf-8"))
            except Exception: continue
            d["id"] = pid; d["path"] = os.path.join(root, pid)
            d["factory"] = (lambda n, d=d: self.render_my_page(d, n)); out.append(d)
        return out

    def render_my_page(self, d, n):
        try: brush = Image.open(os.path.join(d["path"], "brush.png")).convert("RGBA")
        except Exception: brush = None
        return R.learning_page(d.get("markup", ""), d.get("romaji", ""), d.get("english", ""), d.get("orange", True), n=n,
                               tag="MY PAGE", brush=brush)

    def load_book(self):
        self.mine = self.my_pages()
        self.book = R.build_book(self.mine); self.cache.clear(); self.vcache.clear()

    def page(self, i):
        if i not in self.cache:
            if len(self.cache) > 14: self.cache.pop(next(iter(self.cache)))
            self.cache[i] = self.book[i][2](i + 1)
        return self.cache[i]

    def view(self, i, w, h):
        k = (i, w, h)
        if k not in self.vcache:
            if len(self.vcache) > 24: self.vcache.pop(next(iter(self.vcache)))
            self.vcache[k] = self.page(i)[0].resize((w, h), Image.LANCZOS)
        return self.vcache[k]

    # ------------------------------------------------------------------ UI
    def _build(self):
        self.bar = tk.Frame(self, bg=PANEL, height=46); self.bar.pack(fill="x")
        tk.Frame(self, bg=LINE, height=1).pack(fill="x")
        self.body = tk.Frame(self, bg=PAPER); self.body.pack(fill="both", expand=True)
        self.status = tk.Label(self, text="", bg=PANEL, fg=INK, font=self.F, anchor="w", padx=12); self.status.pack(fill="x", side="bottom")
        # start
        self.start = tk.Canvas(self.body, bg=PAPER, highlightthickness=0)
        self.start.bind("<Configure>", lambda e: self.draw_start())
        # reader
        self.reader = tk.Frame(self.body, bg=PAPER)
        self.toc = tk.Frame(self.reader, bg=PANEL, width=300)
        tk.Label(self.toc, text="Contents  目次", bg=PANEL, fg=INK, font=self.FB, anchor="w", padx=12, pady=8).pack(fill="x")
        self.toc_list = tk.Listbox(self.toc, bg=PAPER, fg=INK, font=self.F, bd=0, highlightthickness=0, activestyle="none",
                                   selectbackground=OCHRE, selectforeground="white", width=34)
        self.toc_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.toc_list.bind("<<ListboxSelect>>", self.toc_pick)
        self.cv = tk.Canvas(self.reader, bg=PAPER, highlightthickness=0); self.cv.pack(side="right", fill="both", expand=True)
        self.cv.bind("<Configure>", lambda e: self.redraw())
        self.cv.bind("<ButtonPress-1>", self.down); self.cv.bind("<B1-Motion>", self.move); self.cv.bind("<ButtonRelease-1>", self.up)
        self.cv.bind("<MouseWheel>", self.wheel); self.cv.bind("<Button-4>", lambda e: self.wheel(e, 120)); self.cv.bind("<Button-5>", lambda e: self.wheel(e, -120))
        for k, f in (("<Left>", lambda e: self.turn(-1)), ("<Right>", lambda e: self.turn(1)), ("<Prior>", lambda e: self.turn(-1)),
                     ("<Next>", lambda e: self.turn(1)), ("<space>", lambda e: self.turn(1)), ("<Home>", lambda e: self.goto(0)),
                     ("<End>", lambda e: self.goto(len(self.book) - 1)), ("<plus>", lambda e: self.set_zoom(self.zoom * 1.25)),
                     ("<equal>", lambda e: self.set_zoom(self.zoom * 1.25)), ("<minus>", lambda e: self.set_zoom(self.zoom / 1.25)),
                     ("<Key-0>", lambda e: self.set_zoom(1)), ("<Key-b>", lambda e: self.toggle_bookmark()), ("<Key-c>", lambda e: self.toggle_toc()),
                     ("<Return>", lambda e: self.start_pressed() if self.mode == "start" else None), ("<Escape>", lambda e: self.escape())):
            self.bind(k, lambda e, f=f: f(e) if self.mode in ("reader", "start") or e.keysym == "Escape" else None)
        self.toc_open = False
        # maker
        self.maker = Maker(self.body, self)

    def bar_set(self, items):
        for w in self.bar.winfo_children(): w.destroy()
        for it in items:
            if it == "|": tk.Frame(self.bar, bg=LINE, width=1, height=28).pack(side="left", padx=6, pady=8); continue
            if it == "<>": tk.Frame(self.bar, bg=PANEL).pack(side="left", expand=True, fill="x"); continue
            if isinstance(it, str): tk.Label(self.bar, text=it, bg=PANEL, fg=INK, font=self.F).pack(side="left", padx=8); continue
            t, c = it[:2]; b = Btn(self.bar, t, c, font=self.F); b.pack(side="left", padx=3, pady=7)
            if len(it) > 2: setattr(self, it[2], b)
        self.page_lbl = None

    def say_status(self, msg, ms=6000):
        self.status.config(text=msg)
        if self.status_after: self.after_cancel(self.status_after)
        self.status_after = self.after(ms, lambda: self.status.config(text=COPYLINE))

    def save_state(self):
        try: json.dump(self.st, open(self.state_path, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception: pass

    def escape(self):
        if self.mode == "reader":
            if self.zoom > 1: self.set_zoom(1)
            else: self.show_start()
        elif self.mode == "maker": self.show_reader()

    # ------------------------------------------------------------------ start screen
    def show_start(self):
        self.mode = "start"
        for f in (self.reader, self.maker): f.pack_forget()
        self.start.pack(fill="both", expand=True)
        self.bar_set(["  EX Inc.  ·  簡単に日本語を学ぶ", "<>", ("Contents", lambda: (self.show_reader(), self.toggle_toc(True))),
                      ("Maker  作る", self.show_maker), ("Read  読む", self.start_pressed)])
        self.status.config(text=COPYLINE); self.draw_start()

    def draw_start(self):
        c = self.start; w, h = max(200, c.winfo_width()), max(200, c.winfo_height())
        bg = R.parchment().resize((w, h)).filter(ImageFilter.GaussianBlur(2))
        ch = int(h * .78); cw = ch * 2 // 3
        cov = Image.open(R.A("cover.jpg")).convert("RGB").resize((cw, ch), Image.LANCZOS)
        bh = int(ch * .62); bw = int(bh * 963 / 1462)
        back = Image.open(R.A("back_cover.jpg")).convert("RGB").resize((bw, bh), Image.LANCZOS)
        x = max(30, w // 2 - cw - 60); y = (h - ch) // 2
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        d.rectangle((x + 10, y + 12, x + cw + 10, y + ch + 12), fill=(40, 24, 10, 90))
        d.rectangle((x + cw + 70 + 8, y + 10, x + cw + 70 + bw + 8, y + bh + 10), fill=(40, 24, 10, 70))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); bg = bg.convert("RGBA"); bg.alpha_composite(sh)
        bg.paste(cov, (x, y)); bg.paste(back, (x + cw + 70, y))
        dd = ImageDraw.Draw(bg); tx = x + cw + 70
        R.draw_ruby(dd, tx, y + bh + 26, "簡単[かんたん]に 日本語[にほんご]を 学[まな]ぶ", max(30, h // 22), max_w=w - tx - 30)
        dd.text((tx, y + bh + 26 + h // 14), "learn japanese easy", font=R.font(max(22, h // 30), "rm"), fill=(96, 58, 34))
        dd.text((tx, y + bh + 26 + h // 14 + h // 22), "A Book of True Value · by EX Inc.", font=R.font(max(16, h // 48), "rm"), fill=(96, 58, 34))
        self._start_img = ImageTk.PhotoImage(bg.convert("RGB"))
        c.delete("all"); c.create_image(0, 0, anchor="nw", image=self._start_img)
        bx, by = tx, y + ch - 56
        c.create_rectangle(bx, by, bx + 260, by + 56, fill=INK, outline=INK, tags="go")
        c.create_text(bx + 130, by + 28, text="PRESS START", fill="#f3e9d6", font=(UIF, 16, "bold"), tags="go")
        last = self.st.get("page", 0)
        if last: c.create_text(bx, by - 18, text="continues at page %d" % (last + 1), anchor="w", fill=INK, font=self.F)
        c.create_text(bx + 280, by + 28, anchor="w", text="Enter ↵", fill=INK, font=self.F)
        c.tag_bind("go", "<Button-1>", lambda e: self.start_pressed()); c.tag_bind("go", "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind("go", "<Leave>", lambda e: c.config(cursor=""))

    def start_pressed(self):
        self.show_reader(); self.goto(min(self.st.get("page", 0), len(self.book) - 1), anim=False)

    # ------------------------------------------------------------------ reader
    def show_reader(self):
        self.mode = "reader"
        for f in (self.start, self.maker): f.pack_forget()
        self.reader.pack(fill="both", expand=True)
        self.bar_set([("← Library", self.show_start), ("☰ Contents", self.toggle_toc), ("☆ Bookmark", self.toggle_bookmark, "bm_btn"), "|",
                      ("−", lambda: self.set_zoom(self.zoom / 1.25)), ("Fit", lambda: self.set_zoom(1)), ("+", lambda: self.set_zoom(self.zoom * 1.25)),
                      "|", ("♪ Play", self.play_page), "<>", ("Edit page", self.edit_my_page, "edit_btn"), ("✎ Maker", self.show_maker)])
        self.page_lbl = tk.Label(self.bar, text="", bg=PANEL, fg=INK, font=self.F); self.page_lbl.pack(side="left", padx=12)
        self.fill_toc(); self.redraw(); self.status.config(text=COPYLINE)

    def fill_toc(self):
        L_ = self.toc_list; L_.delete(0, "end"); self.toc_map = []; sec = None
        bms = [i for i, p in enumerate(self.book) if p[0] in self.st["bookmarks"]]
        if bms:
            L_.insert("end", "★ BOOKMARKS"); L_.itemconfig("end", fg=OCHRE); self.toc_map.append(None)
            for i in bms: L_.insert("end", "   %2d   %s" % (i + 1, self.book[i][0])); self.toc_map.append(i)
        for i, (t, s, _) in enumerate(self.book):
            if s != sec:
                sec = s; L_.insert("end", ""); self.toc_map.append(None)
                L_.insert("end", s.upper()); L_.itemconfig("end", fg=OCHRE); self.toc_map.append(None)
            L_.insert("end", "   %2d   %s" % (i + 1, t)); self.toc_map.append(i)

    def toc_pick(self, e):
        sel = self.toc_list.curselection()
        if not sel: return
        i = self.toc_map[sel[0]]
        if i is not None: self.goto(i)

    def toggle_toc(self, force=None):
        self.toc_open = (not self.toc_open) if force is None else force
        if self.toc_open: self.toc.pack(side="left", fill="y", before=self.cv); self.fill_toc()
        else: self.toc.pack_forget()

    def toggle_bookmark(self):
        t = self.book[self.cur][0]; b = self.st["bookmarks"]
        if t in b: b.remove(t); self.say_status("Bookmark removed.")
        else: b.append(t); self.say_status("Bookmarked page %d." % (self.cur + 1))
        self.save_state(); self.update_bar()
        if self.toc_open: self.fill_toc()

    def update_bar(self):
        if self.mode != "reader": return
        t, s, _ = self.book[self.cur]
        if self.page_lbl: self.page_lbl.config(text="%d / %d   %s" % (self.cur + 1, len(self.book), t))
        if hasattr(self, "bm_btn"): self.bm_btn.config(text="★ Bookmarked" if t in self.st["bookmarks"] else "☆ Bookmark")
        if hasattr(self, "edit_btn"):
            if s == "My Pages": self.edit_btn.pack(side="left", padx=3, before=self.page_lbl) if False else self.edit_btn.config(state="normal", fg=INK)
            else: self.edit_btn.config(fg=LINE)

    def geom(self):
        w, h = max(100, self.cv.winfo_width()), max(100, self.cv.winfo_height())
        ph = max(90, int(min(h - 40, (w - 160) * 1.5))); pw = ph * 2 // 3
        return w, h, pw, ph

    def redraw(self, img=None):
        if self.mode != "reader": return
        w, h, pw, ph = self.geom(); c = self.cv; c.delete("all")
        if img is None:
            if self.zoom > 1.001:
                zw, zh = int(pw * self.zoom), int(ph * self.zoom)
                k = ("z", self.cur, zw)
                if k not in self.vcache: self.vcache[k] = self.page(self.cur)[0].resize((zw, zh), Image.LANCZOS)
                img = self.vcache[k]
                self.pan[0] = max(-(zw - pw) / 2 - 60, min((zw - pw) / 2 + 60, self.pan[0]))
                self.pan[1] = max(-(zh - h) / 2 - 20, min((zh - h) / 2 + 20, self.pan[1])) if zh > h else 0
            else:
                img = self.view(self.cur, pw, ph); self.pan = [0, 0]
        self._ph = ImageTk.PhotoImage(img)
        ox = (w - img.width) / 2 + self.pan[0]; oy = (h - img.height) / 2 + self.pan[1]
        c.create_rectangle(ox + 6, oy + 8, ox + img.width + 6, oy + img.height + 8, fill="#d4c4a4", outline="")
        c.create_image(ox, oy, anchor="nw", image=self._ph)
        self.org = (ox, oy, img.width / R.W)
        self.draw_quiz_marks()
        # side arrows
        for side, sym, en in ((0, "‹", self.cur > 0), (1, "›", self.cur < len(self.book) - 1)):
            x = 40 if side == 0 else w - 40; col = INK if en else LINE
            c.create_oval(x - 24, h / 2 - 24, x + 24, h / 2 + 24, outline=col, width=2, fill=PAPER, tags="arr%d" % side)
            c.create_text(x, h / 2 - 3, text=sym, fill=col, font=(UIF, 24, "bold"), tags="arr%d" % side)
            c.tag_bind("arr%d" % side, "<Button-1>", lambda e, s=side: (self.turn(1 if s else -1), "break")[1])
        self.update_bar()

    def draw_quiz_marks(self):
        ox, oy, s = self.org
        for x0, y0, x1, y1, act in self.page(self.cur)[1]:
            if act[0] != "quiz": continue
            a = self.st["quiz"].get(act[1])
            if a is None or a[0] != act[2]: continue
            col = "#2f7a3a" if act[3] else RED
            self.cv.create_rectangle(ox + x0 * s, oy + y0 * s, ox + x1 * s, oy + y1 * s, outline=col, width=3)
            self.cv.create_text(ox + (x1 - 20) * s, oy + (y0 + 40) * s, text="○" if act[3] else "×", fill=col,
                                font=(UIF, max(10, int(40 * s)), "bold"))

    def set_zoom(self, z):
        if self.mode != "reader": return
        self.zoom = max(1.0, min(3.0, z)); self.redraw()
        self.say_status("Zoom %d%%  (drag to move, 0 = fit)" % round(self.zoom * 100) if self.zoom > 1 else "Fit page", 2500)

    def wheel(self, e, delta=None):
        d = delta if delta is not None else e.delta
        if e.state & 0x4: self.set_zoom(self.zoom * (1.15 if d > 0 else 1 / 1.15)); return
        if self.zoom > 1: self.pan[1] += 80 if d > 0 else -80; self.redraw(); return
        self.turn(-1 if d > 0 else 1)

    def goto(self, i, anim=True):
        i = max(0, min(len(self.book) - 1, i))
        if i == self.cur or not anim or self.mode != "reader":
            self.cur = i; self.st["page"] = i; self.save_state(); self.redraw(); return
        self.flip(i)

    def turn(self, d):
        if self.mode != "reader" or self.anim: return
        n = self.cur + d
        if 0 <= n < len(self.book): self.zoom = 1.0; self.flip(n)
        elif n >= len(self.book): self.say_status("That was the back cover - the end of the book.  お疲れさまでした！")

    def flip_frame(self, a, b, t, forward):
        """page turning on its left spine. forward: a (old) folds away revealing b. back: b unfolds over a."""
        top, under = (a, b) if forward else (b, a)
        k = (1 - t) if forward else t
        pw, ph = top.size; lw = max(1, int(pw * math.sin(k * math.pi / 2)))
        frame = under.copy().convert("RGB")
        leaf = top.resize((lw, ph), Image.BILINEAR)
        shade = int(150 * (1 - k))
        if shade: leaf = Image.blend(leaf, Image.new("RGB", leaf.size, (40, 26, 14)), shade / 255 * .55)
        frame.paste(leaf, (0, 0))
        sw = min(70, pw - lw)
        if sw > 2:
            g = Image.linear_gradient("L").rotate(90).resize((sw, ph)); g = g.point(lambda v: int(v * .5 * math.sin(k * math.pi)))
            frame.paste(Image.new("RGB", (sw, ph), (30, 18, 8)), (lw, 0), g)
        return frame

    def flip(self, n):
        w, h, pw, ph = self.geom(); fwd = n > self.cur
        a, b = self.view(self.cur, pw, ph), self.view(n, pw, ph)
        t0 = time.time(); dur = .34; self.anim = True

        def step():
            t = min(1, (time.time() - t0) / dur); e = t * t * (3 - 2 * t)
            self.redraw(self.flip_frame(a, b, e, fwd))
            if t < 1: self.after(12, step)
            else:
                self.anim = None; self.cur = n; self.st["page"] = n; self.save_state(); self.redraw()
                if self.toc_open: self.fill_toc()
        step()

    # drag: swipe to turn (fit) or pan (zoomed); click = hotspot
    def down(self, e):
        self.drag = [e.x, e.y, list(self.pan), False]

    def move(self, e):
        if not self.drag or self.anim: return
        dx, dy = e.x - self.drag[0], e.y - self.drag[1]
        if abs(dx) + abs(dy) > 6: self.drag[3] = True
        if not self.drag[3]: return
        if self.zoom > 1:
            self.pan = [self.drag[2][0] + dx, self.drag[2][1] + dy]; self.redraw(); return
        w, h, pw, ph = self.geom(); n = self.cur + (1 if dx < 0 else -1)
        if not 0 <= n < len(self.book): return
        t = min(1, abs(dx) / pw)
        self.redraw(self.flip_frame(self.view(self.cur, pw, ph), self.view(n, pw, ph), t, dx < 0)); self.drag.append((n, t))

    def up(self, e):
        d, self.drag = self.drag, None
        if not d or self.anim: return
        if not d[3]:
            return self.click(e)
        if self.zoom > 1: return
        if len(d) > 4:
            n, t = d[-1]
            if t > .22: self.finish_drag(n, t)
            else: self.redraw()

    def finish_drag(self, n, t):
        w, h, pw, ph = self.geom(); fwd = n > self.cur
        a, b = self.view(self.cur, pw, ph), self.view(n, pw, ph); self.anim = True; t0 = time.time()
        def step():
            k = min(1, t + (time.time() - t0) / .2)
            self.redraw(self.flip_frame(a, b, k, fwd))
            if k < 1: self.after(12, step)
            else: self.anim = None; self.cur = n; self.st["page"] = n; self.save_state(); self.redraw()
        step()

    def click(self, e):
        ox, oy, s = self.org; px, py = (e.x - ox) / s, (e.y - oy) / s
        if not (0 <= px < R.W and 0 <= py < R.H):
            return
        for x0, y0, x1, y1, act in self.page(self.cur)[1]:
            if x0 <= px <= x1 and y0 <= py <= y1:
                if act[0] == "say": self.play(act[1])
                elif act[0] == "quiz":
                    self.st["quiz"][act[1]] = [act[2], act[3]]; self.save_state(); self.redraw()
                    self.say_status("○  正解！ Correct!" if act[3] else "×  Not quite - try again.")
                return
        # tap on the left/right third of the page turns it
        if px < R.W * .18: self.turn(-1)
        elif px > R.W * .82: self.turn(1)

    def play(self, text):
        r = AU.say(text)
        shown = text[6:] if text.startswith("kanji:") else text
        if r: self.say_status("♪  %s   %s" % (shown, L.romaji_markup(L.auto_markup(shown)) if not all(ord(c) < 128 for c in shown) else ""), 4000)
        else: self.say_status(AU.NO_AUDIO, 9000)
        return r

    def play_page(self):
        hs = [a for *_, a in self.page(self.cur)[1] if a[0] == "say"]
        if hs: self.play(hs[0][1])
        else: self.say_status("This page has no audio. Tap a word or a character on a lesson page to hear it.")

    def edit_my_page(self):
        t, s, _ = self.book[self.cur]
        if s != "My Pages": self.say_status("Only your own pages (My Pages) can be edited. Open the Maker to make one."); return
        idx = [i for i, p in enumerate(self.book) if p[1] == "My Pages"].index(self.cur)
        self.show_maker(); self.maker.open_page(self.mine[idx])

    # ------------------------------------------------------------------ maker
    def show_maker(self):
        self.mode = "maker"
        for f in (self.start, self.reader): f.pack_forget()
        self.maker.pack(fill="both", expand=True)
        self.bar_set([("← Book", self.show_reader), "  ページ作り · Page Maker", "<>", ("New page", self.maker.new_page),
                      ("Save to My Pages", self.maker.save), ("Export PNG", self.maker.export_png), ("Export PDF", self.maker.export_pdf)])
        self.maker.after(30, self.maker.refresh)

    def take_screenshot(self, path):
        from PIL import ImageGrab
        self.update(); x, y = self.winfo_rootx(), self.winfo_rooty()
        ImageGrab.grab((x, y, x + self.winfo_width(), y + self.winfo_height())).save(path)


UIF = "Noto Sans CJK JP"
COPYLINE = "©2026 EX Inc./HYPERION DIGITAL ©2026   ·   ← → or swipe to turn · C contents · B bookmark · +/− zoom"


def wheel_image(n=150):
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); px = im.load(); r = n / 2
    import colorsys
    for y in range(n):
        for x in range(n):
            dx, dy = x - r, y - r; d = math.hypot(dx, dy)
            if d <= r - 1:
                h = (math.atan2(dy, dx) / (2 * math.pi)) % 1; s = d / r
                px[x, y] = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, 1)) + (255,)
    return im


class Maker(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=PAPER); self.app = app; F = app.F
        self.left = tk.Frame(self, bg=PANEL, width=400); self.left.pack(side="left", fill="y"); self.left.pack_propagate(False)
        self.cv = tk.Canvas(self, bg=PAPER, highlightthickness=0, cursor="pencil"); self.cv.pack(side="right", fill="both", expand=True)
        self.cv.bind("<Configure>", lambda e: self.refresh())
        self.cv.bind("<ButtonPress-1>", self.b_down); self.cv.bind("<B1-Motion>", self.b_move); self.cv.bind("<ButtonRelease-1>", self.b_up)
        def head(t): tk.Label(self.left, text=t, bg=PANEL, fg=OCHRE, font=app.FB, anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        def entry(var, jp=False):
            e = tk.Entry(self.left, textvariable=var, font=(UIF, 12 if jp else 11), bg=PAPER, fg=INK, relief="solid", bd=1,
                         insertbackground=INK); e.pack(fill="x", padx=14, pady=2); return e
        def lab(t): tk.Label(self.left, text=t, bg=PANEL, fg=INK, font=(UIF, 9), anchor="w").pack(fill="x", padx=14)
        self.en, self.jp, self.mk, self.rm, self.cap = (tk.StringVar() for _ in range(5))
        self.orange = tk.BooleanVar(value=True)
        head("1 · English  →  日本語")
        self.e_en = entry(self.en); self.e_en.bind("<Return>", lambda e: self.translate())
        row = tk.Frame(self.left, bg=PANEL); row.pack(fill="x", padx=14, pady=3)
        Btn(row, "Translate  翻訳", self.translate, font=F).pack(side="left")
        Btn(row, "♪ Play", self.play, font=F).pack(side="left", padx=6)
        self.note = tk.Label(self.left, text="Offline phrase book. Edit any result below.", bg=PANEL, fg=INK, font=(UIF, 9),
                             anchor="w", justify="left", wraplength=360); self.note.pack(fill="x", padx=14)
        head("2 · Page text (editable)")
        lab("Japanese"); self.e_jp = entry(self.jp, True)
        self.e_jp.bind("<Return>", lambda e: self.from_japanese()); self.e_jp.bind("<FocusOut>", lambda e: self.from_japanese(quiet=True))
        lab("Furigana  (kanji[reading], e.g. 日本[にほん]が)"); self.e_mk = entry(self.mk, True)
        self.e_mk.bind("<Return>", lambda e: self.from_markup()); self.e_mk.bind("<FocusOut>", lambda e: self.from_markup())
        lab("Romaji"); e = entry(self.rm); e.bind("<Return>", lambda e: self.render()); e.bind("<FocusOut>", lambda e: self.render())
        lab("English caption"); e = entry(self.cap); e.bind("<Return>", lambda e: self.render()); e.bind("<FocusOut>", lambda e: self.render())
        tk.Checkbutton(self.left, text="Orange kana line with romaji", variable=self.orange, command=self.render, bg=PANEL, fg=INK,
                       activebackground=PANEL, selectcolor=PAPER, font=F).pack(anchor="w", padx=10)
        head("3 · Brush  筆")
        row = tk.Frame(self.left, bg=PANEL); row.pack(fill="x", padx=14)
        self.colour = BRUSH_COLOURS[0][1]; self.tool = "brush"; self.sw = {}
        for name, rgb in BRUSH_COLOURS:
            b = tk.Label(row, bg="#%02x%02x%02x" % rgb, width=3, height=1, relief="solid", bd=1, cursor="hand2")
            b.pack(side="left", padx=2); b.bind("<Button-1>", lambda e, c=rgb: self.set_colour(c)); self.sw[rgb] = b
        self.cur_sw = tk.Label(row, text=" now ", bg="#%02x%02x%02x" % self.colour, fg="white", font=(UIF, 8, "bold"), relief="solid", bd=1)
        self.cur_sw.pack(side="left", padx=8)
        row2 = tk.Frame(self.left, bg=PANEL); row2.pack(fill="x", padx=14, pady=4)
        self.wheel = tk.Canvas(row2, width=110, height=110, bg=PANEL, highlightthickness=0, cursor="crosshair"); self.wheel.pack(side="left")
        self._wimg = ImageTk.PhotoImage(wheel_image(110)); self.wheel.create_image(0, 0, anchor="nw", image=self._wimg)
        self.wheel.bind("<Button-1>", self.pick_wheel); self.wheel.bind("<B1-Motion>", self.pick_wheel)
        col = tk.Frame(row2, bg=PANEL); col.pack(side="left", fill="both", expand=True, padx=8)
        self.val = tk.Scale(col, from_=100, to=10, orient="horizontal", label="brightness", bg=PANEL, fg=INK, highlightthickness=0,
                            troughcolor=PAPER, font=(UIF, 8), command=lambda v: self.pick_wheel(None)); self.val.set(70); self.val.pack(fill="x")
        self.size = tk.Scale(col, from_=4, to=90, orient="horizontal", label="size", bg=PANEL, fg=INK, highlightthickness=0,
                             troughcolor=PAPER, font=(UIF, 8)); self.size.set(28); self.size.pack(fill="x")
        row3 = tk.Frame(self.left, bg=PANEL); row3.pack(fill="x", padx=14, pady=4)
        self.tb = Btn(row3, "Brush", lambda: self.set_tool("brush"), font=F); self.tb.pack(side="left")
        self.te = Btn(row3, "Eraser", lambda: self.set_tool("eraser"), font=F); self.te.pack(side="left", padx=4)
        Btn(row3, "Undo", self.undo, font=F).pack(side="left", padx=4); Btn(row3, "Clear", self.clear, font=F).pack(side="left")
        self.bind_all("<Control-z>", lambda e: self.undo() if app.mode == "maker" else None)
        self.info = tk.Label(self.left, text="", bg=PANEL, fg=INK, font=(UIF, 9), anchor="w", justify="left", wraplength=360)
        self.info.pack(fill="x", padx=14, pady=6)
        self.layer = Image.new("RGBA", (R.W, R.H), (0, 0, 0, 0)); self.undo_stack = []; self.page_img = None; self.editing = None
        self.vs = .4; self.org = (0, 0); self.pts = []
        self.set_tool("brush"); self.new_page(quiet=True)

    # text
    def translate(self):
        m, note = L.translate(self.en.get())
        if m is None:
            self.note.config(text=note or "Type an English word or sentence first.", fg=RED); return
        self.note.config(text="✓ %s  —  edit the Japanese if you like" % note, fg=INK)
        self.jp.set(L.plain(m)); self.mk.set(m); self.rm.set(L.romaji_markup(m))
        e = self.en.get().strip(); self.cap.set(e[:1].upper() + e[1:]); self.render()

    def from_japanese(self, quiet=False):
        t = self.jp.get().strip()
        if not t or (quiet and L.plain(self.mk.get()) == t): return
        m = L.auto_markup(t); self.mk.set(m); self.rm.set(L.romaji_markup(m)); self.render()

    def from_markup(self):
        m = self.mk.get().strip()
        if not m: return
        if L.plain(m) != self.jp.get().strip(): self.jp.set(L.plain(m))
        self.rm.set(L.romaji_markup(m)); self.render()

    def play(self):
        t = self.jp.get().strip()
        if t: self.app.play(t)

    def render(self):
        self.page_img = R.learning_page(self.mk.get().strip() or "　", self.rm.get().strip(), self.cap.get().strip(), self.orange.get(),
                                        tag="MY PAGE")[0].convert("RGBA")
        self.refresh(full=True)

    # canvas
    def refresh(self, full=True):
        if self.page_img is None: return
        w, h = max(100, self.cv.winfo_width()), max(100, self.cv.winfo_height())
        vh = h - 30; self.vs = vh / R.H; vw = int(R.W * self.vs)
        if full or getattr(self, "_vsize", None) != (vw, vh):
            self._vsize = (vw, vh); self.vbg = self.page_img.resize((vw, vh), Image.LANCZOS)
            self.vlayer = self.layer.resize((vw, vh), Image.LANCZOS)
        self.org = ((w - vw) // 2, 15); self.show()

    def show(self):
        im = self.vbg.copy(); im.alpha_composite(self.vlayer)
        self._ph = ImageTk.PhotoImage(im); self.cv.delete("all")
        ox, oy = self.org
        self.cv.create_rectangle(ox + 5, oy + 6, ox + im.width + 5, oy + im.height + 6, fill="#d4c4a4", outline="")
        self.cv.create_image(ox, oy, anchor="nw", image=self._ph)

    def set_colour(self, rgb):
        self.colour = tuple(rgb); self.cur_sw.config(bg="#%02x%02x%02x" % self.colour); self.set_tool("brush")

    def pick_wheel(self, e):
        import colorsys
        if e is not None: self._wxy = (e.x, e.y)
        x, y = getattr(self, "_wxy", (55, 55)); dx, dy = x - 55, y - 55
        s = min(1, math.hypot(dx, dy) / 55); h = (math.atan2(dy, dx) / (2 * math.pi)) % 1
        if e is None and not hasattr(self, "_wxy"): return
        self.set_colour(tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, self.val.get() / 100)))

    def set_tool(self, t):
        self.tool = t
        self.tb.config(bg=PANEL2 if t == "brush" else PANEL); self.tb._bg = PANEL2 if t == "brush" else PANEL
        self.te.config(bg=PANEL2 if t == "eraser" else PANEL); self.te._bg = PANEL2 if t == "eraser" else PANEL

    def to_page(self, e):
        return ((e.x - self.org[0]) / self.vs, (e.y - self.org[1]) / self.vs)

    def b_down(self, e):
        self.undo_stack.append(self.layer.copy()); self.undo_stack[:] = self.undo_stack[-25:]
        self.pts = [self.to_page(e) + (time.time(),)]; self._last_r = None

    def radius(self, i, pts):
        """speed-thinned width with an ink-brush taper at both ends"""
        base = self.size.get() / 2
        if self.tool == "eraser": return base
        x, y, t = pts[i]; px, py, pt = pts[max(0, i - 1)]
        sp = math.hypot(x - px, y - py) / max(1e-3, t - pt)
        r = base * (1.15 - min(.55, sp / 4000))
        n = len(pts); a = min(1, (i + 1) / 6); b = min(1, (n - i) / 8) if self._final else 1
        return max(1.0, r * (.35 + .65 * a) * (.25 + .75 * b))

    def stamp(self, d, pts, sc, fill, upto=None):
        for i in range(1 if len(pts) > 1 else 0, len(pts) if upto is None else upto):
            x0, y0, _ = pts[max(0, i - 1)]; x1, y1, _ = pts[i]
            r0, r1 = self.radius(max(0, i - 1), pts), self.radius(i, pts)
            dist = math.hypot(x1 - x0, y1 - y0); n = max(1, int(dist / max(1, min(r0, r1) * .35)))
            for k in range(n + 1):
                f = k / n; x, y, r = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, (r0 + (r1 - r0) * f) * sc
                d.ellipse((x * sc - r, y * sc - r, x * sc + r, y * sc + r), fill=fill)

    def b_move(self, e):
        if not self.pts: return
        p = self.to_page(e) + (time.time(),)
        if math.hypot(p[0] - self.pts[-1][0], p[1] - self.pts[-1][1]) < 2: return
        self.pts.append(p); self._final = False
        fill = (0, 0, 0, 0) if self.tool == "eraser" else self.colour + (255,)
        seg = self.pts[-2:]
        d = ImageDraw.Draw(self.vlayer); self.stamp(d, self.pts, self.vs, fill, None) if len(self.pts) < 3 else self.stamp_last(d, fill)
        if self.tool == "eraser": self.stamp(ImageDraw.Draw(self.layer), self.pts[-2:], 1, fill)
        self.show()

    def stamp_last(self, d, fill):
        pts = self.pts; i = len(pts) - 1
        x0, y0, _ = pts[i - 1]; x1, y1, _ = pts[i]; r0, r1 = self.radius(i - 1, pts), self.radius(i, pts)
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / max(1, min(r0, r1) * .35)))
        for k in range(n + 1):
            f = k / n; x, y, r = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, (r0 + (r1 - r0) * f) * self.vs
            d.ellipse((x * self.vs - r, y * self.vs - r, x * self.vs + r, y * self.vs + r), fill=fill)

    def b_up(self, e):
        if not self.pts: return
        if self.tool == "brush":
            if len(self.pts) == 1: self.pts.append((self.pts[0][0] + .5, self.pts[0][1], self.pts[0][2] + .05))
            self._final = True
            self.stamp(ImageDraw.Draw(self.layer), self.pts, 1, self.colour + (255,))
        self.pts = []; self.vlayer = self.layer.resize(self.vbg.size, Image.LANCZOS); self.show()

    # brush programmatic (tests)
    def stroke(self, pts, colour=None, size=None, eraser=False):
        if colour: self.set_colour(colour)
        if size: self.size.set(size)
        self.set_tool("eraser" if eraser else "brush")
        self.undo_stack.append(self.layer.copy()); t = time.time()
        self.pts = [(x, y, t + i * .016) for i, (x, y) in enumerate(pts)]; self._final = True
        self.stamp(ImageDraw.Draw(self.layer), self.pts, 1, (0, 0, 0, 0) if eraser else self.colour + (255,))
        self.pts = []; self.refresh()

    def undo(self):
        if self.undo_stack: self.layer = self.undo_stack.pop(); self.refresh()

    def clear(self):
        self.undo_stack.append(self.layer.copy()); self.layer = Image.new("RGBA", (R.W, R.H), (0, 0, 0, 0)); self.refresh()

    # pages
    def new_page(self, quiet=False):
        self.editing = None
        for v in (self.en, self.jp, self.mk, self.rm, self.cap): v.set("")
        self.layer = Image.new("RGBA", (R.W, R.H), (0, 0, 0, 0)); self.undo_stack = []
        self.note.config(text="Offline phrase book. Try: hello · I love Japan · good morning teacher", fg=INK)
        self.render()
        self.info.config(text="Draw on the page with the brush. Your pages go under My Pages in the book.")

    def open_page(self, d):
        self.editing = d
        self.en.set(d.get("source", "")); self.mk.set(d.get("markup", "")); self.jp.set(L.plain(d.get("markup", "")))
        self.rm.set(d.get("romaji", "")); self.cap.set(d.get("english", "")); self.orange.set(d.get("orange", True))
        try: self.layer = Image.open(os.path.join(d["path"], "brush.png")).convert("RGBA")
        except Exception: self.layer = Image.new("RGBA", (R.W, R.H), (0, 0, 0, 0))
        self.undo_stack = []; self.render(); self.info.config(text="Editing your page. Save to keep the changes.")

    def composite(self):
        im = self.page_img.copy(); im.alpha_composite(self.layer); return im.convert("RGB")

    def save(self):
        if not self.mk.get().strip() and not self.layer.getbbox():
            self.info.config(text="The page is empty - translate something or draw first.", fg=RED); return None
        pid = self.editing["id"] if self.editing else time.strftime("%Y%m%d-%H%M%S")
        p = os.path.join(self.app.dir, "mypages", pid); os.makedirs(p, exist_ok=True)
        json.dump({"markup": self.mk.get().strip(), "romaji": self.rm.get().strip(), "english": self.cap.get().strip(),
                   "orange": self.orange.get(), "source": self.en.get().strip(), "saved": time.strftime("%Y-%m-%d %H:%M")},
                  open(os.path.join(p, "page.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        self.layer.save(os.path.join(p, "brush.png")); self.composite().save(os.path.join(p, "page.png"))
        self.app.load_book(); self.editing = next((d for d in self.app.mine if d["id"] == pid), None)
        n = [i for i, b in enumerate(self.app.book) if b[1] == "My Pages"][[d["id"] for d in self.app.mine].index(pid)] + 1
        self.info.config(text="✓ Saved to My Pages - page %d of the book." % n, fg=INK)
        return n

    def export_png(self, path=None):
        path = path or filedialog.asksaveasfilename(title="Export page as PNG", defaultextension=".png", initialfile="my_japanese_page.png",
                                                    filetypes=[("PNG image", "*.png")])
        if not path: return None
        self.composite().save(path); self.info.config(text="✓ Exported %s" % path, fg=INK); return path

    def export_pdf(self, path=None, all_pages=None):
        if all_pages is None and self.app.mine and path is None:
            all_pages = messagebox.askyesno("Export PDF", "Export ALL My Pages into one PDF?\n(No = only this page)")
        path = path or filedialog.asksaveasfilename(title="Export PDF", defaultextension=".pdf", initialfile="my_japanese_pages.pdf",
                                                    filetypes=[("PDF document", "*.pdf")])
        if not path: return None
        if all_pages:
            ims = [self.app.render_my_page(d, None)[0] for d in self.app.mine]
        else:
            ims = [self.composite()]
        ims[0].save(path, "PDF", resolution=150, save_all=True, append_images=ims[1:])
        self.info.config(text="✓ Exported %d page(s) to %s" % (len(ims), path), fg=INK); return path


def selftest(app, out):
    """LJE_SELFTEST=<folder>: exercise the frozen build (furigana, translator, audio, export) and quit"""
    os.makedirs(out, exist_ok=True); lines = []
    try:
        app.start_pressed(); app.turn(1); app.update()
        app.show_maker(); mk = app.maker
        for en in ("hello", "I love Japan", "good morning teacher"):
            mk.en.set(en); mk.translate(); lines.append("%s -> %s | %s | %s" % (en, mk.jp.get(), mk.mk.get(), mk.rm.get()))
        mk.jp.set("今日は日本語を勉強します"); mk.from_japanese(); lines.append("furigana: %s | %s" % (mk.mk.get(), mk.rm.get()))
        mk.stroke([(150 + i * 8, 1550) for i in range(100)], (196, 126, 52), 40)
        lines.append("png " + str(mk.export_png(os.path.join(out, "selftest.png"))))
        lines.append("pdf " + str(mk.export_pdf(os.path.join(out, "selftest.pdf"), all_pages=False)))
        lines.append("audio clip: %s  windows ja voice: %s %s" % (AU.say("こんにちは"), AU.windows_voice(), AU._voice))
        lines.append("pages %d  font %s" % (len(app.book), UIF)); lines.append("SELFTEST OK")
    except Exception:
        import traceback; lines.append(traceback.format_exc())
    open(os.path.join(out, "selftest.txt"), "w", encoding="utf-8").write("\n".join(lines))
    app.after(1500, app.destroy)


def main():
    app = App()
    if os.environ.get("LJE_SELFTEST"): app.after(1500, lambda: selftest(app, os.environ["LJE_SELFTEST"]))
    app.mainloop()


if __name__ == "__main__":
    main()
