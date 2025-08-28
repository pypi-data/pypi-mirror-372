# Adding accessibility to Sphinx

Sphinx extension that provides accessibility features.

## Introduction

This Sphinx extension provides various accessibility features to enhance the usability of Sphinx-generated books. Features include:

- Support for dyslexic-friendly fonts
- High contrast mode

## Installation
To install the Sphinx-Accessibility extension, follow these steps:

**Step 1: Install the Package**

Install the `Sphinx-Accessibility` package using `pip`:
```
pip install sphinx-accessibility
```

**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
sphinx-accessibility
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of Sphinx extra extensions:
```
sphinx: 
    extra_extensions:
        - sphinx_accessibility
```

## Features

### Accessibility Menu

The accessibility menu provides a centralized location for users to adjust various accessibility settings, including font size, contrast, and more. The icon for this menu is <img src="./svgs/Accessibility.svg" style="height:1em;vertical-align:text-bottom;">.

### Support for dyslexic-friendly fonts

This feature allows users to switch to the dyslexic-friendly font [OpenDyslexic](https://opendyslexic.org/), improving readability for individuals with dyslexia. The font can be toggled on and off using the button <img src="./svgs/Font.svg" style="height:1em;vertical-align:text-bottom;"> in the accessibility menu <img src="./svgs/Accessibility.svg" style="height:1em;vertical-align:text-bottom;">.

### High contrast mode

This feature allows users to switch to a high contrast mode, improving visibility for individuals with visual impairments. The mode can be toggled on and off using the button <img src="./svgs/Contrast.svg" style="height:1em;vertical-align:text-bottom;"> in the accessibility menu <img src="./svgs/Accessibility.svg" style="height:1em;vertical-align:text-bottom;">.

The high-contrast mode tries to apply the following changes to the CSS:

- Change text and border colors to black in light-mode and white in dark-mode.
- Change background colors to white in light-mode and black in dark-mode.
- Makes all colors twice as intense.
- In dark-mode only: increases contrast with factor 1.5.

## Example

You can see how the accessibility features work in [this example book](https://teachbooks.io/TU-Delft-Theme-Example/).