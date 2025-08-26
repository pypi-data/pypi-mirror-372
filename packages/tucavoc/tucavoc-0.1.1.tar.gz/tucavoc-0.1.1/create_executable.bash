
# Install the current version as normal (not editable otherwise it wont find tucavoc package in the exe)
pip uninstall tucavoc
pip install .

cd tucavoc\widgets
#pyinstaller --onefile --windowed main.py 
pyinstaller --noconfirm  main.spec 


cd ..
cd ..

# Reinstall at the end
pip uninstall tucavoc
pip install -e .

