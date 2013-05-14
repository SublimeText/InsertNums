# Sublime Text - InsertNums
Sublime Text plugin, that inserts consecutive numbers across multiple selections.

## Compatibility
After quick testing, InsertNums is compatible with ST2 and ST3!

## Installation
For now, download the Zip and copy it to your Sublime Text Packages folder, or use `git clone`. I'll make a pull request shortly to add it to Package Control.

## Usage

- **Windows**: CTRL+Alt+N
- **OSX**: Super+Alt+N
- **Linux**: CTRL+Alt+N

As you change the values in the prompt, InsertNums will refresh your selections.

By default, InsertNums will use `1 1 1` as the default settings. These values relate to:

- Starting number - where to start the iterator at
- Step - how much to increment each iteration by
- Padding - will prepend a `0` to the number in the iteration.

InsertNums can also insert the alphabet! Just use `a 1 0` as your values, or change `a` to whatever character you'd like to start from! One of the great side effects of introducing alpha sequences is that you can generate seemingly (but definitely not) random sequences. For instance, using `a 12345 0` will generate the following across three selections:

    a
	rfv
	ajmq

All that's happening there is that the next letter in the sequence is shunted across by the step amount.

# License
MIT - [http://jbrooksuk.mit-license.org](http://jbrooksuk.mit-license.org)