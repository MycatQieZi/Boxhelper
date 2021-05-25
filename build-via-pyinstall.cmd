conda activate box-helper
create-version-file version.yml --outfile version.yml
pyinstaller main.py -F --windowed --uac-admin --icon=tool-box-64.ico --version-file=version.txt
pause