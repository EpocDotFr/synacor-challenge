# Synacor Challenge

<img src="/logo.png?raw=true" align="right">

Source code of my solution to the [Synacor Challenge](https://challenge.synacor.com/).

I've put myself a personal challenge: do not use any third-party packages (only use built-in Python features).

## Prerequisites

Python >= 3.8.

## Installation

Clone this repo.

## Usage

````shell
$ python run.py materials/challenge.bin
````

Press <kbd>CTRL+C</kbd> to stop.

## Codes

> [!IMPORTANT]
> Spoilers below.

You have to find 8 codes scattered along the challenge, and submit each of them on the [challenge website](https://challenge.synacor.com/)
to validate your progress.

Begin by implementing a virtual machine able to execute the challenge's binary file: follow the [architecture specs](/materials/arch-spec).

### First code

Found in the architecture specs.

### Second code

Found once you implemented all the basic opcodes mentioned in the specs (0, 19, and 21).

### Third code

Found once all the opcodes have been implemented and self-tests have passed.

### Fourth code

Found in the text adventure game by using the tablet at the very beginning.

### Fifth code

Found in the text adventure game on a wall in a twisty passage by walking in the caverns.

At this point of the challenge, I made it so I am able to [automate all the actions](/solutions/text_adventure_game.txt)
instead of manually typing: `python run.py materials/challenge.bin --actions=solutions/text_adventure_game.txt`

### Sixth code

Found in the text adventure game by using the teleporter device.

The teleporter device can be found after [solving the equation](/solutions/coins.py) of the strange monument in the
central hall after collecting all the five coins (red, blue, shiny, concave and corroded): `_ + _ * _^2 + _^3 - _ = 399`.

### Seventh code

> [!NOTE]
> WIP: I am here.

The teleporter device must be used a second time, but not before setting register #8 to some very specific number.

At this point of the challenge, I had to implement a debugger. It's hooked to the virtual machine's input system. The
following commands are available:

  - `!dump example.dump` dumps the current state of the virtual machine to a file using a custom binary format. This
  file can be loaded back (the format is automatically recognized by the virtual machine): `python run.py example.dump`
  - `!reg` displays the registers state
    - `!reg <a> <b>` sets register's `<a>` value to `<b>`
  - `!sta` displays the stack state
  - `!mem` displays the memory state at the current address pointer
    - `!mem <a>` displays the memory state at the given address `<a>`

### Eighth code

I don't know yet.
