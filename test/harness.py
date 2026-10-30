import os, sys, time, json, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/lje_shots"; os.makedirs(OUT, exist_ok=True)
import learn_japanese_easy as M
log = open(os.path.join(OUT, "log.txt"), "w", encoding="utf-8")
def P(*a):
    print(*a, file=log, flush=True); print(*a, flush=True)
app = M.App(); app.geometry("1280x900+0+0")
def pump(t=.4):
    end = time.time() + t
    while time.time() < end: app.update(); time.sleep(.01)
def shot(name):
    pump(.3)
    try:
        if os.name == "nt": app.take_screenshot(os.path.join(OUT, name + ".png"))
        else:
            from PIL import ImageGrab
            app.update(); x, y = app.winfo_rootx(), app.winfo_rooty()
            ImageGrab.grab((x, y, x + app.winfo_width(), y + app.winfo_height())).save(os.path.join(OUT, name + ".png"))
    except Exception as e: P("shot fail", name, e)
def run():
    try:
        pump(1); shot("01_start")
        app.start_pressed(); app.goto(0, anim=False); pump(.5); shot("02_cover")
        t0 = time.time(); app.turn(1); pump(.15); shot("03_flipping"); pump(.6); P("flip ok cur=", app.cur, "%.2fs" % (time.time() - t0))
        # drag swipe
        w = app.cv.winfo_width(); h = app.cv.winfo_height()
        class E: pass
        def ev(x, y): e = E(); e.x, e.y, e.state = x, y, 0; return e
        app.down(ev(w * .7, h / 2))
        for k in range(1, 12): app.move(ev(w * .7 - k * 30, h / 2)); pump(.02)
        shot("04_swipe_mid"); app.up(ev(w * .7 - 330, h / 2)); pump(.6); P("swipe -> page", app.cur + 1)
        for i, t in enumerate(app.book):
            if t[0].startswith("Kana reference"): kref = i
            if t[0].startswith("Kanji reference"): kj = i
            if t[0].startswith("Greetings 1-5"): gw = i
            if t[0].startswith("Quiz 1"): q1 = i
        app.goto(2, anim=False); shot("05_page2_art")
        app.goto(kref, anim=False); shot("06_kana_ref")
        # tap あ (rightmost column, first cell)
        ox, oy, s = app.org; hs = app.page(kref)[1][0]
        r = app.click(ev(ox + (hs[0] + 20) * s, oy + (hs[1] + 60) * s)); P("tap kana ->", app.status.cget("text"))
        app.goto(kj, anim=False); shot("07_kanji_ref")
        app.goto(5, anim=False); shot("08_hiragana")
        app.goto(gw - 1, anim=False); shot("09_learning_page")
        app.goto(gw, anim=False); shot("10_words")
        app.goto(q1, anim=False); ox, oy, s = app.org
        qs = [h for h in app.page(q1)[1] if h[4][0] == "quiz"]
        right = [h for h in qs if h[4][3]][0]; wrong = [h for h in qs if not h[4][3] and h[4][1] != right[4][1]][0]
        for hh in (right, wrong): app.click(ev(ox + (hh[0] + 30) * s, oy + (hh[1] + 30) * s))
        shot("11_quiz"); P("quiz state", app.st["quiz"])
        app.toggle_bookmark(); app.toggle_toc(True); pump(.3); shot("12_contents_bookmark"); app.toggle_toc(False)
        app.set_zoom(2); app.pan = [200, -300]; app.redraw(); shot("13_zoom"); app.set_zoom(1)
        app.goto(len(app.book) - 1, anim=False); shot("14_back_cover")
        # maker
        app.show_maker(); pump(.5); mk = app.maker
        for en in ["hello", "I love Japan", "good morning teacher"]:
            mk.en.set(en); mk.translate(); pump(.2)
            P("translate %r -> %s | %s | %s | %s" % (en, mk.jp.get(), mk.mk.get(), mk.rm.get(), mk.note.cget("text")))
        shot("15_maker_text")
        mk.jp.set("今日は日本語を勉強します"); mk.from_japanese(); P("auto furigana:", mk.mk.get(), "|", mk.rm.get())
        mk.en.set("good morning teacher"); mk.translate()
        import math
        pts = [(140 + i * 9, 1560 - 60 * math.sin(i / 10)) for i in range(100)]
        mk.stroke(pts, (196, 126, 52), 46)
        mk.stroke([(1000 + 40 * math.cos(a / 20), 250 + 40 * math.sin(a / 20) + a * 2) for a in range(120)], (168, 40, 32), 30)
        mk.stroke([(200 + i * 4, 1450) for i in range(80)], (28, 22, 18), 20)
        mk.undo(); mk.stroke([(150 + i * 6, 1480 + (i % 20)) for i in range(120)], (110, 62, 30), 18)
        mk.stroke([(500 + i * 3, 1540) for i in range(60)], eraser=True, size=30)
        P("layer bbox", mk.layer.getbbox())
        shot("16_maker_brush")
        n = mk.save(); P("saved my page ->", n, len(app.mine))
        P("png", mk.export_png(os.path.join(OUT, "export_page.png")))
        P("pdf", mk.export_pdf(os.path.join(OUT, "export_pages.pdf"), all_pages=True))
        app.show_reader(); app.goto(n - 1, anim=False); shot("17_my_page_in_book"); P("page title", app.book[app.cur][0])
        P("ALL OK")
    except Exception:
        P(traceback.format_exc())
    app.after(100, app.destroy)
app.after(300, run); app.mainloop()
