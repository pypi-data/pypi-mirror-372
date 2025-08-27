# py4D-browser-transform

`py4D-browser-transform` is a plugin for [py4D-browser](https://github.com/sezelt/py4D-browser) that provides utility functions for transforming the datacube, currently including flipping, transposing, permuting axes. Other functions like cropping, resampling, and adjusting intensity offsets or scaling might be added in the future.

## Installation 
You can install `py4D-browser-transform` directly from GitHub using pip and git (assuming you have git avaialble):
```bash
pip install git+https://github.com/chiahao3/py4D-browser-transform
```

> 💡 **Note:** 
> - If you install into a fresh Python environment, `py4D-browser` and `py4DSTEM` will be automatically installed as dependencies so you don't need to install them first.
> - If you already have `py4D-browser` installed, you can install this plugin into the same Python environment.

## Usage

After installation, you should see the "Transform" submenu appear under the **"Plugins"** menu.  
From here, you can:

- Flip or transpose the diffraction pattern.  
- Permute dataset axes if your 4D dataset is not in the expected order.
![Demo of py4D-browser-transform](assets/demo.gif)

These operations would direcly modify the loaded datacube, but will not affect the raw file stored on disk. You can export the transformed datacube to disk using **File > Export Datacube**.

> 💡 **Note:** 
> - The order of flipping and permutation matters so if you mix these two operations, you'll have to reverse the operaitons in the exact opposite order to get back to the original state. For example, if you permute and then flip/transpose, you'll have to undo the flip/transpose and then reset the permute.

## License

GNU GPLv3

**py4D-browser-transform** is open source software distributed under a GPLv3 license.
It is free to use, alter, or build on, provided that any work derived from **py4D-browser-transform** is also kept free and open.
