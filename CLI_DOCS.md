# `bmaingret-obfuscator`

C Code Obfuscator

**Usage**:

```console
$ bmaingret-obfuscator [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `demo`: Run test function through available...
* `obfuscate`: Obfuscate passed c_file (as path).
* `parser`: Simply show identified function applying...

## `bmaingret-obfuscator demo`

Run test function through available obfuscator, print resulting
 obfuscated code
and run the function using the passed arguments if any. When passing
arguments, the example name MUST be passed to the command.

**Usage**:

```console
$ bmaingret-obfuscator demo [OPTIONS] [FUNCTION] [ARGS]...
```

**Arguments**:

* `[FUNCTION]`: Specify the test function to use.

Available functions:

sum42.c: uint8_t f(uint32_t a, uint32_t b, uint32_t c);
pi.c: float pi_approx(int n);
  [default: sum42.c]
* `[ARGS]...`: Specify the arguments to pass to the function.

**Options**:

* `--help`: Show this message and exit.

## `bmaingret-obfuscator obfuscate`

Obfuscate passed c_file (as path). If ARGS are passed to the command,
the function will be ran before and after obfuscation using passed
arguments.

If --output-file is not used, obfuscated code will output in terminal.

**Usage**:

```console
$ bmaingret-obfuscator obfuscate [OPTIONS] C_FILE [ARGS]...
```

**Arguments**:

* `C_FILE`: Path to a C file that you want to obfuscate  [required]
* `[ARGS]...`: Specify the arguments to pass to the function.

**Options**:

* `-l, --level INTEGER`: 

Specify the level of obfuscation.
Available:
Level (0) uses (PassthroughObfuscator)
Level (5) uses (HarderToRead)
Level (10) uses (ReplacementObfuscator)


  [default: 0]
* `--output-file PATH`: Specify a directory to save the obfuscated code.
* `--help`: Show this message and exit.

## `bmaingret-obfuscator parser`

Simply show identified function applying cpyparser to a test function.

**Usage**:

```console
$ bmaingret-obfuscator parser [OPTIONS]
```

**Options**:

* `--show-ast`: Additionnaly show AST for the test function  [default: False]
* `--help`: Show this message and exit.
