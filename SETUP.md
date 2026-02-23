# Setup Instructions
## Prerequisites
* Developed on Python 3.12.3 (Should be forward compatible up till Python 3.14 as it only requires NumPy and Pillow)
* Bash shown is for Unix. Windows... Lazy... Google the equivalent...
#### Repository Cloning
```bash
#Cd into your preferred path
git clone https://github.com/yeoshuyi/Python-Maze-Encoder-and-Solver
cd ./Python-Maze-Encoder-and-Solver
```
#### Libraries
```bash
#Optional venv setup
python3 -m venv ./.venv
source ./.venv/bin/activate

#Libraries
python3 -m pip install -r requirements.txt
```
## Maze.png Generation
* Using your preferred photo editor, generate a .png file that is of 30x30 dimension (Smaller maps supported through filling the unused area with walls.)
* Color code the blocks based on the RGB values:
```python
STARTPOINT = (0, 183, 239)
ENDPOINT = (237, 28, 36)
HEART = (34, 177, 80)
GEM = (255, 242, 0)
MONSTER = (111, 49, 152)
MONSTER_FACING = (181, 165, 213)
```
> Alternatively, change the values shown above within maze_encoderv2.py

## Maze.bin Generation
#### Path Setup
* Edit as necessary within maze_encoderv2.py
```python
IMAGE_PATH = 'maze.png'
BITSTREAM_PATH = 'maze_v2.bin'
```
#### Run
```bash
cd src
python3 -m maze_encoderv2
```

## Maze.gif Generation
#### Path Setup
* Edit as necessary within maze_solverv2.py
```python
IMAGE_PATH = 'maze.png'
BITSTREAM_PATH = 'maze_v2.bin'
```

#### Run
```bash
cd src
python3 -m maze_solver2
```

## Last but not least...
> Take this project with a pinch of salt haha... Not much input validation implemented as the main focus was just on algorithm development for education.