set -e
export WINEPREFIX=/workspace/exwifi/.wine WINEDEBUG=-all
cd /workspace/lje
PY='C:\Python311\python.exe'
wine "$PY" -m PyInstaller --noconfirm "learn japanese easy.spec" > /workspace/lje_pyi.log 2>&1
echo DIR_DONE
wine "C:\\InnoSetup\\ISCC.exe" installer.iss > /workspace/lje_iss.log 2>&1
echo ISS_DONE
cd dist && rm -f learn.japanese.easy.1.0.0.Windows.x64.zip && python3 -c "import shutil;shutil.make_archive('learn.japanese.easy.1.0.0.Windows.x64','zip','.','learn japanese easy')" && echo ZIP_DONE && sha256sum learn.japanese.easy.Setup.1.0.0.exe learn.japanese.easy.1.0.0.Windows.x64.zip
