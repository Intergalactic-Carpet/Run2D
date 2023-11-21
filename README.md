# Run2D
Run2D is a basic game I made, the objective is to continue without stopping, stopping for too long will result in your death.
It has a range of difficulties, Easy, Normal, Hard, and Impossible. The names should represent how playable it is.

# How to play Run2D
Download Run2D.exe, go into Properties > General, tick unblock and click Apply.
Windows automatically blocks unkown .exe files downloaded from the web from running, this is to give permission.
Next, open it and the game should run.

Or, if you dont trust it, run the following script in terminal to create your own .exe file

``
pip install pyinstaller
``

``
pyinstaller --name=Run2D --onefile --distpath=. main.py
``

Note: You will need to have pip installed, or use a different installer to install pyinstaller. Methods may vary between operating systems. Run2D.exe is only compatible with Windows (As far as I know).

# Usage
Feel free to use my code anywhere you like, however could you credit me if you do so.

