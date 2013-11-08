# Sublime Text - InsertNums
Sublime Text plugin, that inserts consecutive numbers across multiple selections.

## Compatibility
After quick testing, InsertNums is compatible with ST2 and ST3!

## Installation
You can install InsertNums via [Package Control](http://wbond.net/sublime_packages/package_control), by searching for **Insert Sequences**.

Optionally you can download the Zip and copy it to your Sublime Text Packages folder, or use `git clone`. I'll make a pull request shortly to add it to Package Control.

## Usage
- **Windows**: <kbd>CTRL+Alt+N</kbd>
- **OSX**: <kbd>Super+Alt+N</kbd>
- **Linux**: <kbd>CTRL+Alt+N</kbd>

As you change the values in the prompt, InsertNums will refresh your selections.

By default, InsertNums will use `1 1 0` as the default settings. These values relate to:

- Starting number - where to start the iterator at
- Step - how much to increment each iteration by
- Padding - will prepend a `0` to the number in the iteration.

Some times you may want to use InsertNums without the automatic insertion. You can use <kbd>Shift</kbd> as a modifier key to the same shortcuts above to prevent the insertion, just hit enter to confirm your pattern.

### Generating the alphabet
InsertNums can also insert the alphabet! Just use `a 1 1` as your values, or change `a` to whatever character you'd like to start from! One of the great side effects of introducing alpha sequences is that you can generate seemingly (but definitely not) random sequences. For instance, using `a 12345 0` will generate the following across three selections:

    a
	rfv
	ajmq

All that's happening there is that the next letter in the sequence is shunted across by the step amount.

### Generating Hex
Hex can also be inserted using only a slight change to the input format, `xn 1 0` where `n` is the starting number. So for instance, `x1 1 0` will generate the same as `1 1 0` since we're starting at 1 anywhere. The true magic of this format starts to shine when we increase the starting number to 7 or above.

`x9 1 0` will produce:
	
	9
	a
	b
	c

And we can still make use of the step value, `x9 3 0` will generate:

	9
	c
	f
	12

## Contributors
- [James Brooks](http://james.brooks.so), [@jbrooksuk](https://twitter.com/jbrooksuk)
- Marco Novaro, [@MarcoNovaro](https://github.com/MarcoNovaro)
- Oleg Geier, [@relikd](https://twitter.com/relikd)
- Arthur Comben, [@anthillape](https://twitter.com/anthillape)

# License
MIT - [http://jbrooksuk.mit-license.org](http://jbrooksuk.mit-license.org)