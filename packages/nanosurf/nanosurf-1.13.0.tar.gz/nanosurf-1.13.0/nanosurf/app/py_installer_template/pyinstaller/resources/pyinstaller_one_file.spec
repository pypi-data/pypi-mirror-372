# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [ 
  ('./app_icon.ico', 'app'),
  ('./app_stylesheet.qss', 'app')
]

a = Analysis(
    ['./../../main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=['./resources'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
			 
splash = Splash(
    './SplashScreen.bmp',
    binaries=a.binaries,
    datas=a.datas,                
    text_pos=(70, 264),
    text_size=7,
    text_color='black'
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,  
    splash,                   
    splash.binaries,                   
    [],
    name='Python_App',
    icon='./app_icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None 
)
