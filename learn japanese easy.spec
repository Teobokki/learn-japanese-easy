# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
a = Analysis(['learn_japanese_easy.py'], pathex=['vendor'], datas=[('assets', 'assets')] + [('vendor/pykakasi/data', 'pykakasi/data')],
             hiddenimports=['pykakasi', 'jaconv', 'comtypes', 'comtypes.client', 'winsound', 'PIL.ImageTk', 'lje_render', 'lje_lang', 'lje_audio', 'lje_data'],
             excludes=['matplotlib', 'scipy', 'pandas', 'IPython', 'pytest', 'cv2', 'numpy', 'imageio', 'imageio_ffmpeg', 'webview'],
             noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='learn japanese easy', console=False, upx=False,
          version='version.txt', icon=['assets/icon.ico'])
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name='learn japanese easy')
