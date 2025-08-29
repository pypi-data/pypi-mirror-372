# Monocular Camera Path Prediction for Exosuits
The Python modules use a monocular camera to predict the user's movements to better inform the control algorithm.

<img src="docs/exosuit_anticipation.png" alt="Description" width="600"/>

## Install
To install the library run: `pip install monocular-path-prediction`

Download the pre-trained models from [Depth-Anything-V2](https://github.com/DepthAnything/Depth-Anything-V2?tab=readme-ov-file#pre-trained-models).

## Development
0. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
1. `make init` to create the virtual environment and install dependencies
2. `make format` to format the code and check for errors
3. `make test` to run the test suite
4. `make clean` to delete the temporary files and directories
5. `poetry publish --build` to build and publish to https://pypi.org/project/monocular-path-prediction


## Usage
```
# example usage of the module
 python src/main.py --help
```


## Microcontrollers
The microcontroller code can be found inside /src/microcontroller.
