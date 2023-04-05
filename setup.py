# setup.py

from cx_Freeze import setup, Executable

build_options = {
    'packages': ['flask', 'requests', 'PIL'],
    'include_files': ['templates/', 'static/']
}

exe = Executable(
    script='app.py',
    target_name='app.exe',
    base=None,
    icon=None
)

setup(
    name='AiratsApp',
    version='0.1',
    description='Airats Ascii Art App',
    options={'build_exe': build_options},
    executables=[exe]
)
