1. Install python3
2. Install uv (`python3 -m ensurepip` and `python3 -m pip install uv`)
3. `git clone https://github.com/maddinkunze/handcode`
4. `cd handcode`
5. `python3 -m uv venv --python 3.7`
6. Activate venv (`source .venv/bin/activate` on macOS and Linux, `.venv\Scripts\activate` on Windows)
7. `cd build/convertmodels`
8. `python -m ensurepip`
9. `python -m pip install -r requirements_c2p.txt`
10. `python checkpoint2proto.py`
11. `python -m pip install -r requirements_p2t.txt`
12. `python proto2tflite.py`

Voila, you should now have a working `model.tflite` file. Note that it requires flex delegates, so a default tflite runtime wont work. If you want to use it in an Android app, you can add `org.tensorflow:tensorflow-lite-select-tf-ops` to your dependencies. For all other cases I am currently trying to figure out how to do it.
If step 12 fails, try to nuke your venv and reset it (i.e. delete the .venv folder in the project root and redo steps 4-8, skip 9-10 and continue from step 11)