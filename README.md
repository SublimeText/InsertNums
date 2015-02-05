# Insert Nums for Sublime Text 2 and 3.

A **Sublime Text 2 and 3** plugin, that inserts (consecutive) numbers across multiple selections or modifies the selections' contents with expressions. Huge configurability.

## Installation

You can install *Insert Nums* via [Package Control][pkgctrl] by searching for **Insert Nums**.

Alternatively, you can download the Zip and copy it to your Sublime Text Packages folder, or use `git clone`.

## Usage

- **Windows** and **Linux**: <kbd>Ctrl+Alt+N</kbd>
- **OSX**: <kbd>⌘+⎇+N</kbd>

An input panel opens which live-previews your current format string. If you close the panel (e.g. by pressing <kbd>Esc</kbd>), the changes will be undone. 
If you prefer to not have this live preview, you can disable it by also pressing the <kbd>Shift</kbd> key.

Insert a string in the format `<start>:<step>` and press enter. Both can be omitted and default to `1` (meaning `1:1`).

For every selected region the inserted number (starting with *start*) will then be increased by *step*. But there is more!

### Commands

- **`prompt_insert_nums`**

    Opens an input panel with live preview as explained above. The parameter `preview` can specify if *Insert Nums* should show a live preview when editing the format string. Defaults to `true`.

- **`insert_nums`**

    This is the basic command. Call this with a `format` parameter and bind it to a keyboard shortcut if you find yourself using a query very often.

### Usage with numbers

*Insert Nums* supports both, integers and floating numbers, as *start* and *step* values respectively, also negative numbers. This means you can use `1:.4` on 4 selections and get this:

    1.0
    1.4
    1.8
    2.2

Furthermore, you can use arbitrary Python expressions to generate your numbers, e.g. for bitflags. An example can be found in the [Examples](#examples).

See the [Advanced usage](#advaced-usage) section for information about using a specific formatting.

### Usage with the alphabet

*Insert Nums* can also insert the alphabet. Just use `a` as *start* value, or change `a` to whatever character you'd like to start from. *step* only accepts integers because there are obviously no fractions of the characters in the alphabet.

One of the side effects of introducing alpha sequences is that you can generate seemingly (but definitely not) random sequences. For instance, using `a:12345` will generate the following across three selections:

    a
	rfv
	ajmq

All that's happening there is that the next letter in the sequence is shunted across by the step amount.

If you'd rather like *Insert Nums* to wrap when the last character (`z`) is reached, you can append `~w`. Thus, `a:12345~w` will generate this:

    a
    v
    q

For more options see the following [Advanced usage](#advaced-usage) section.

### Expression Mode

Other than inserting numbers or alphas this mode takes the value of a selection and allows you to modify it with a Python expression. This will be explained in detail further below.

### Advanced usage (insert)

The complete syntax is: `<start>:<step>~<format>::<expr>@<stopexpr><reverse>`, the corresponding separator is only required if you actually supply the following part. Every part itself is optional (defaulting to `1:1`), but if you want the alpha mode you have to supply the alphabetical start value.

Below is an abstract example showing the syntax with all optional parts (indicated by `[]`):

    numbers: [<start>][:<step>][~<format>][::<expr>][@<stopexpr>][!]
    alpha:   <start>[:<step>][~<format>][@<stopexpr>][!]

Detailed syntax definition: [format_syntax.txt](format_syntax.txt)

- **start**

    + *with numbers* (optional): A [*[decimalinteger]*][decimalinteger] or [*[floatnumber]*][floatnumber] according to Python's syntax specifications with an optional leading sign (`-` or `+`). Default: `1`

    + *with alphabet* (required): A sequence of either lower- or uppercase ASCII characters from the alphabet (`a` to `z` and `A` to `Z`).

- **step** (optional)

    + *with numbers*: A [*[decimalinteger]*][decimalinteger] or [*[floatnumber]*][floatnumber] according to Python's syntax specifications with an optional leading sign (`-` or `+`). Default: `1`

    + *with alphabet*: A [*[decimalinteger]*][decimalinteger] with an optional leading sign (`-` or `+`).

- **format** (optional)

    + *with numbers*: A format string in Python's [Format Specific Mini-Language][fmtlang] (with small and unimportant adjustments for allowed types).

    + *with alphabet*: Similar to *with numbers* but a stripped-down version only for strings. This only includes the `[[fill]align][width]` syntax and additionally accepts a `w` character at the end (see above).

- **expr** (optional)

    + *numbers only*: A valid Python expression which modifies the value as you please. If specified, the *format string* is applied afterwards. Here is a list of available variables:

        - `s`: The value of `step` (specified in the format query and defaults to `1`)
        - `n`: The number of selections
        - `i`: Just an integer holding the counter for the iteration; starts at `0` and is increased by `1` in every loop
        - `_`: The current value before the expression (`start + i * step`)
        - `p`: The result of the previously evaluated value (without formatting); `0` for the first value
        - `math`, `random` and `re`: Useful modules that are pre-imported for you

        *Note*: The return value does not have to be a number type, you can also generate strings, tuples or booleans.

- **stopexpr** (optional)

    A valid Python expression which returns a value that translates to true or false (in a boolean context). Theoretically this can be any value. You can use the same values as in **expr** with addition of the following:

    - `c`: The current evaluated value by the expression (without formatting) or just the same as `_` if there was no expression specified

    This ignores the number of selections which means that you can also have more or less values than selections. Especially useful when generating numbers from a single selection.

    - If there is more selections than numbers generated when processing the stop expression, all the remaining selections' text will be deleted.
    - If there is more numbers generated than selections, all further numbers are joining by newlines (`"\n"`) and added to the last selection made. This can be the first selection if there is only one.

- **reverse** (optional)

    Must be `!` and results in the regions being filled in reversed order.

### Advanced usage (Expression)

In addition to the insert mode *Insert Nums* also specifies a way to **modify** the current selection(s). The syntax is as follows:

    [<cast>]|[~<format>::]<expr>[@<stopexpr>][!]

Again, for the detailed syntax specification, see: [format_syntax.txt](format_syntax.txt).

The `|` pipe is used to show the meaning of piping the current selection to the following expression. `stopexpr` behaves a bit different than in insert mode and the current value `_` is adjusted.


- **cast** (optional)

    Can be one of `s`, `i`, `f` or `b` and means that the string in the selection will be converted to the corresponding type, if possible. An error message is shown otherwise.

    - `s`: `str` or `unicode` (in ST2) (default)
    - `i`: `int`
    - `f`: `float`
    - `b`: `bool`

- **format** (optional)

    Same as in insert mode.

- **expr**

    Same as in insert mode, except that `_` represents the (converted) value of the current selection.

- **stopexpr** (optional)

    Usage is the same as in insert mode and the `_` for expression mode, but the effects are a bit different:

    - You can not generate more values than there are selections.
    - If you generate less values than there are selections, the remaining selections will be untouched. Return `""` in the expression if you want to clear them.

- **reverse** (optional)

    Must be `!` and results in both the selections being parsed **and** the regions being filled in reversed order.


## Examples

### Basic insert

- `1` or ` `

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

### Insert with format

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

### Expression Insert

- `0~#06x::1<<_`

    ```
    0x0001
    0x0002
    0x0004
    0x0008
    0x0010
    0x0020
    0x0040
    0x0080
    0x0100
    ```

- `::i**2`

    ```
    1
    4
    9
    16
    25
    36
    ```

### Alpha insert

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

### Stop expressions

**Note**: Assuming everything in *Before* has been selected with one selection spanning each line.

- Before:

    ```
    1
    2
    3
    4
    5
    ```

    `@_>3`

    ```
    1
    2
    3


    ```

- Before:

    ```
    1
    ```

    `~02@p==10` or `~02@_>10` or `~02@i==10`

    ```
    01
    02
    03
    04
    05
    06
    07
    08
    09
    10
    ```

### Expression mode

**Note**: Assuming everything in *Before* has been selected with one selection spanning each line.

- Before:

    ```
    1
    2
    3
    4
    5
    ```

    `i|_+p`

    ```
    1
    3
    6
    10
    15
    ```

    `i|p+3 if i!= 0 else _!`

    ```
    27
    24
    21
    18
    15
    ```

- Before:

    ```
    pointfloat    ::=  {integer}? \. \d+ | {integer} \.
    exponentfloat ::=  (?:{integer} | {pointfloat}) [eE] [+-]? \d+
    float         ::=  {pointfloat} | {exponentfloat}
    numeric       ::=  {integer} | {float}
    signednum     ::=  [+-]? {numeric}
    ```

    `|re.sub(r' +', ' ', _)`

    ```
    pointfloat ::= {integer}? \. \d+ | {integer} \.
    exponentfloat ::= (?:{integer} | {pointfloat}) [eE] [+-]? \d+
    float ::= {pointfloat} | {exponentfloat}
    numeric ::= {integer} | {float}
    signednum ::= [+-]? {numeric}
    ```

And many more ...

## Contributors

- [James Brooks](http://james.brooks.so), Twitter: [@jbrooksuk](https://twitter.com/jbrooksuk)
- [@FichteFoll](https://github.com/FichteFoll), Twitter: [@FichteFoll](https://twitter.com/FichteFoll)
- Marco Novaro, [@MarcoNovaro](https://github.com/MarcoNovaro)
- Oleg Geier, Twitter: [@relikd](https://twitter.com/relikd)
- Arthur Comben, Twitter: [@anthillape](https://twitter.com/anthillape)

# License

MIT - <http://jbrooksuk.mit-license.org>

[pkgctrl]: http://wbond.net/sublime_packages/package_control
[decimalinteger]: http://docs.python.org/2.6/reference/lexical_analysis.html#grammar-token-decimalinteger
[floatnumber]: http://docs.python.org/2.6/reference/lexical_analysis.html#grammar-token-floatnumber
[fmtlang]: http://docs.python.org/2.6/library/string.html#format-specification-mini-language
