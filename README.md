## american bunny hop.

a slim wrapper for `lldb` that prioritizes the use case of reverse engineering.

### running it

no mean feat, i'm afraid. the easy part is cloning the repo and running something like the following (i'm using `uv` here, but you can use whatever you like):

```sh
uv venv -p 3.9 ./venv
source ./venv/bin/activate # or whatever your shell uses
uv pip sync requirements.txt
venv/bin/python src/abh.py
deactivate
```

should get the app up and running. if not, then you're in the hard part; trying to import the `lldb` module. `lldb` isn't downloadable via `pip`; you'll have to pull it from your own computer.

if you don't have it, try installing `Xcode`; also make sure that the python installation your `venv` uses is the one from `Xcode` if you're doing this.

for instance, my python installation ended up at

```sh
/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9
```

and my lldb framework was at

```sh
/Applications/Xcode.app/Contents/SharedFrameworks/LLDB.framework/Resources/Python
```

to get the app working, you'll need to export the path to your lldb framework to your `PYTHONPATH` environment variable.

```sh
export PYTHONPATH=/Applications/Xcode.app/Contents/SharedFrameworks/LLDB.framework/Resources/Python
```

that should do the trick. it's really unfortunate the `lldb` crew hasn't managed to bundle this up into some kind of homebrewable package yet, but i bet there's perhaps no package on earth for which that'd be harder to do than lldb, so oh well.
