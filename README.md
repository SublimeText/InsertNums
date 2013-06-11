# Sublime Text - InsertNums

**Sublime Text 2 and 3** plugin, that inserts consecutive numbers across multiple selections.


## Installation

This package is available on [Package Control][pkgctrl] as "InsertNums".

Alternatively, you can download the Zip and copy it to your Sublime Text Packages folder, or use `git clone`.


## Usage

- **Windows** and **Linux**: <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>N</kbd>
- **OSX**: <kbd>⌘⌃N</kbd>

Insert a string in the format `<start>:<step>` and press enter. *start* is required, while *step* can be omitted and defaults to `1`.

For every selected region the inserted number (starting with *start*) will then be increased by *step*.

### Usage with numbers

InsertNums supports both, integers and floating numbers, as *start* and *step* values respectively, also negative numbers. This means you can use `1:.4` on 4 selections and get this:

    1.0
    1.4
    1.8
    2.2

See the [Advanced usage](#advaced-usage) section for information about using a specific formatting.

### Usage with the alphabet

InsertNums can also insert the alphabet. Just use `a` as *start* value, or change `a` to whatever character you'd like to start from. *step* only accepts integers because there are obviously no fractions of the characters in the alphabet.

One of the side effects of introducing alpha sequences is that you can generate seemingly (but definitely not) random sequences. For instance, using `a:12345` will generate the following across three selections:

    a
	rfv
	ajmq

All that's happening there is that the next letter in the sequence is shunted across by the step amount.

If you'd rather like InsertNums to wrap when the last character (`z`) is reached, you can append `~w`. Thus, `a:12345~w` will generate this:

    a
    v
    q

For more options see the following [Advanced usage](#advaced-usage) section.

### Advanced usage

The complete syntax is: `<start>:<step>~<format><reverse>`

Detailed Syntax definition: [format_syntax.txt](format_syntax.txt)

- **start**

    + *with numbers*: A *[decimalinteger]* or *[floatnumber]* according to Python's syntax specifications with an optional leading sign (`-` or `+`).

    + *with alphabet*: A sequence of either lower- or uppercase ASCII characters from the alphabet (`a` to `z` and `A` to `Z`).

- **step** (optional)

    + *with numbers*: A *[decimalinteger]* or *[floatnumber]* according to Python's syntax specifications with an optional leading sign (`-` or `+`).

    + *with alphabet*: A *[decimalinteger]* with an optional leading sign (`-` or `+`).

- **format** (optional)

    + *with numbers*: A fomat string in Python's [Format Specific Mini-Language][fmtlang] (with small and unimportant adjustments for allowed types).

    + *with alphabet*: Similar to with number but a stripped-down version only for strings. This only includes the `[[fill]align][width]` syntax and additionally accepts a `w` character at the end (see above).

- **reverse** (optional)

    + Must be `!` and results in the regions being filled in reversed order.


## Examples

- `1`

    ```
    1
    2
    3
    4
    5
    6
    ```

- `-10:2~3`

    ```
    -10
     -8
     -6
     -4
     -2
      0
      2
      4
    ```

- `11:11~+4`

    ```
     +11
     +22
     +33
     +44
     +55
     +66
     +77
     +88
     +99
    +110
    ```

- `0.2:.002~-<5` (see `g` type (default) in the [Python format docs][fmtlang])

    ```
    0.2--
    0.202
    0.204
    0.206
    0.208
    0.21-
    0.212
    ```

- `.2:2e-3~6.4f`

    ```
    0.2000
    0.2020
    0.2040
    0.2060
    0.2080
    0.2100
    0.2120
    ```

- `8:8~#010x!`

    ```
    0x00000038
    0x00000030
    0x00000028
    0x00000020
    0x00000018
    0x00000010
    0x00000008
    ```

- `z:25~w` or `z:-1~w`

    ```
    z
    y
    x
    w
    v
    u
    t
    ```

- `aa:10000~ ^6` (here, `|` represents the cursors to visualize trailing spaces)

    ```
      aa  |
     nuq  |
     acpg |
     arjw |
     bgem |
     buzc |
     cjts |
    ```

And many more ...

# License

MIT - <http://jbrooksuk.mit-license.org>


[pkgctrl]: http://wbond.net/sublime_packages/package_control
[decimalinteger]: http://docs.python.org/2.6/reference/lexical_analysis.html#grammar-token-decimalinteger
[floatnumber]: http://docs.python.org/2.6/reference/lexical_analysis.html#grammar-token-floatnumber
[fmtlang]: http://docs.python.org/2.6/library/string.html#format-specification-mini-language