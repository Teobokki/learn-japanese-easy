"""Japanese audio: bundled Open JTalk clips first, then a Windows Japanese voice (SAPI5 or OneCore), offline.
(c)2026 EX Inc./HYPERION DIGITAL (c)2026"""
import json, os, sys, threading, subprocess, shutil
from lje_render import A
import lje_lang as L

_index = None
_voice = {"checked": False, "ok": False, "name": ""}


def index():
    global _index
    if _index is None:
        try: _index = json.load(open(A("audio", "index.json"), encoding="utf-8"))
        except Exception: _index = {}
    return _index


def clip(text):
    n = index().get(text) or index().get(text.replace(" ", ""))
    return A("audio", n) if n else None


def _play_wav(path):
    if os.name == "nt":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    elif shutil.which("aplay"):
        subprocess.Popen(["aplay", "-q", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _sapi_ja():
    for dyn in (False, True):
        try:
            r = _sapi_ja1(dyn)
            if r[1] is not None: return r
        except Exception as e:
            _voice["err"] = str(e)
    return None, None


PS_JA = ("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
         "$v=$s.GetInstalledVoices()|?{$_.VoiceInfo.Culture.Name -eq 'ja-JP'}|select -First 1; ")


def _ps(script, timeout=30):
    exe = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), r"System32\WindowsPowerShell\v1.0\powershell.exe")
    return subprocess.run([exe, "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, timeout=timeout,
                          creationflags=0x08000000).stdout.decode("utf-8", "ignore")


def _sapi_ja1(dyn):
    """-> (SpVoice, token) for a Japanese voice or (None, None)"""
    import comtypes.client
    sp = comtypes.client.CreateObject("SAPI.SpVoice", dynamic=dyn)
    def ja(toks):
        for i in range(toks.Count):
            t = toks.Item(i)
            try: lang = t.GetAttribute("Language")
            except Exception: lang = ""
            if "411" in str(lang).lower().split(";") or "japan" in t.GetDescription().lower(): return t
    t = ja(sp.GetVoices())
    if t is not None: return sp, t
    try:  # Windows 10/11 OneCore voices (Haruka, Ayumi, Ichiro, Sayaka) are visible through this category
        cat = comtypes.client.CreateObject("SAPI.SpObjectTokenCategory", dynamic=dyn)
        cat.SetId(r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices", False)
        t = ja(cat.EnumerateTokens())
        if t is not None: return sp, t
    except Exception:
        pass
    return None, None


def windows_voice():
    if not _voice["checked"]:
        _voice["checked"] = True
        if os.name == "nt":
            try:
                import comtypes
                comtypes.CoInitialize()
                sp, tok = _sapi_ja()
                if tok is not None: _voice.update(ok=True, name=tok.GetDescription(), via="sapi")
            except Exception as e:
                _voice["err"] = str(e)
            if not _voice["ok"]:
                try:
                    n = _ps(PS_JA + "if($v){$v.VoiceInfo.Name}").strip()
                    if n: _voice.update(ok=True, name=n, via="ps")
                except Exception as e:
                    _voice["err2"] = str(e)
    return _voice["ok"]


def say(text, done=None):
    """-> 'clip' | 'voice' | None (no audio available)"""
    text = text.strip()
    if not text: return None
    c = clip(text)
    if c:
        _play_wav(c); return "clip"
    if text.startswith("kanji:"): text = text[6:]
    if os.name == "nt" and windows_voice():
        def run():
            try:
                if _voice.get("via") == "ps":
                    _ps(PS_JA + "$s.SelectVoice($v.VoiceInfo.Name); $s.Speak('%s')" % text.replace("'", "''"), 60); return
                import comtypes; comtypes.CoInitialize()
                sp, tok = _sapi_ja(); sp.Voice = tok; sp.Speak(text, 0)
            except Exception:
                pass
        threading.Thread(target=run, daemon=True).start()
        return "voice"
    return None


NO_AUDIO = ("No audio for this text yet. Book words have built-in audio; for your own sentences add a Japanese voice: "
            "Windows Settings › Time & language › Language › Add Japanese (with Speech).")
