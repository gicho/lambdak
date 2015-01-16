# lambdak

Expressive functional programming in Python with continuations

Lambdak is pronounced 'lambda-k'.

The goal is to wrap up all Python statements inside functions so that
they can be run in places which require expressions, e.g. the body of a
`lambda` expression. And, using continuations lets us build expressions
which are effectively composed of multiple statements.

This lets us create the [Holy Grail of
Python](http://en.wikipedia.org/wiki/Monty_Python_and_the_Holy_Grail),
_multi-line lambdas._ Some examples:

```python
actions = {
  "hello":
    print_("Hello, World!", lambda:

    import_("math", lambda m:
    print_("The area of my circle is:", lambda:
    print_(m.pi * 5 * 5)))),

  "goodbye":
    print_("Goodbye, Cruel World!", lambda:

    try_(lambda:
      1 / 0, lambda:
      print_("Danger, Will Robinson!"))) }

actions["hello"]()
actions["goodbye"]()

circumference = given_(lambda r:
  import_("math", lambda m:
  2 * m.pi * r))

print circumference(5)
```

(Note: I highly recommend using an editor extension like
[vim-cute-python](https://github.com/yawaramin/vim-cute-python) to
prettify the code for readability. For example, it would represent the
keyword `lambda` with the symbol 'λ', without changing the underlying
source code.)

Anyway, what's with all the lambdas?

We can't escape the fact that Python allows only one expression inside a
lambda block. So, we use _more_ lambdas inside that one expression to
'continue' our computations for as long as we want. Internally, the
functions are designed to conserve stack space and avoid stack overflow.
With this one last construct in Python, all the pieces are in place and
you can fully express your code in _exactly_ the way you want.

## News

  - 2015-01-12: just published a
    [tutorial](https://github.com/yawaramin/lambdak/wiki/Unbounded-Tail-Recursion-with-Lambdak)
    on how to take advantage of lambdak's support for nested function
    calls to do unlimited tail recursion in Python. It's even cooler
    than it sounds, check it out.

## Overview

The central concept in this module is the `lambdak`. This is a callable
type which behaves like a normal Python lambda, except that it can be
composed with more `lambdak`s (or with normal lambdas!) to be extended
so that it can execute an unlimited number of statements and
expressions. And it does so in a way that preserves memory.

The implementation details of the `lambdak` type are not important,
because the functions detailed below work like a set of combinators to
let you compose together a `lambdak` that does exactly what you want
(with some restrictions).

You can think of `lambdak` as a
[DSL](https://en.wikipedia.org/wiki/Domain-specific_language) on top of
normal Python which extends basic lambdas into more powerful multi-line
lambdas. Another way to think about it is as composing lots of little
anonymous functions together to make a single, powerful anonymous
function.

## Reference

The `lambdak` module is designed to be 'star-imported' (`from lambdak
import *`): the functions below have all been named with an underscore
character ('_') as the last character.

### Contents

  - [`call_(k)`](#call_)

  - [`given_(k)`](#given_)

  - [`do_(expr_k, k = None)`](#do_)

  - [`print_(x, k = None)`](#print_)

  - [`assert_(expr, k = None)`](#assert_)

  - [`raise_(ex_type = None, ex_val = None, tb_val = None)`](#raise_)

  - [`with_(expr_k, act_k, k = None)`](#with_)

  - [`cond_(test_pairs, default_expr, k = None)`](#cond_)

  - [`assign_(nm, v, d, k = None)`](#assign_)

  - [`get_(nm, d)`](#get_)

  - [`del_(nm, d, k = None)`](#del_)

  - More (both pending documentation and implementation)

### `call_`

Call the given function with no arguments.

#### Arguments

  - `k`. The function to call. It will be called with no arguments.

#### Returns

The result returned by `k`, or `None` if `k` is `None`.

### `given_`

Receive arguments at the beginning of a lambdak chain so you can call
the lambdak with those arguments. These arguments can also have default
values, which effectively lets you bind names to values for the duration
of the `k` closure's scope.

#### Arguments

  - `k`. A callable (usually a lambda) that takes any number of
    arguments and returns either a final value or another lambdak (to
    continue the computation).

#### Returns

A lambdak that can be called with the same number of arguments that are
accepted by the `k` parameter. If the lambdak is called with no
arguments, it will call `k` with no arguments.

#### Example

This example shows both uses of `given_`: providing a way to pass in
arguments to call the outermost lambdak with, and also providing a way
to bind names to values inside a lambdak.

```python
f = given_(lambda x:
  given_(lambda y = 2 * x:
    print_(y)))

f(2)
```

Output:

    4

You can think of this as, 'Given `x`, let `y` be twice `x`; print `y`'.

### `do_`

Meant to be used when you just want to evaluate an expression which has
a side effect, and then optionally carry on with other actions or
calculations.

#### Arguments

  - `expr_k`. Any expression that we want to evaluate for its side
    effects. Must be a callable (usually a lambda expression wrapping a
    value or function call). Will be called (evaluated) when the `do_`
    lambdak is eventually run. We want to delay evaluation because the
    expression may have side effects, so we want to keep them in
    sequence.

  - `k`. Optional (default `None`). If supplied, must be a callable
    which does not accept any arguments and returns any value. This
    contains the rest of the computation (i.e. the rest of the lambdak
    chain).

#### Returns

The same as `given_` would return.

#### Example

```python
def hello(): print "Hello!"
def hi(): print "Hi!"

test = (
  do_(lambda: hello(), lambda:
  do_(lambda: hi())))
```

Output: nothing yet.

```python
test()
```

Output:

    Hello!
    Hi!

### `print_`

Print a single expression and optionally carry on the computation.

#### Arguments

  - `x`. The expression to print. This is passed to [Python's `print`
    statement](https://docs.python.org/2/reference/simple_stmts.html#the-print-statement).

  - `k`. Optional (default `None`). The same as `do_`.

#### Returns

The same as `given_`.

### `assert_`

#### Arguments

  - `expr`. The expression to assert. This is passed to [Python's
    `assert`
    statement](https://docs.python.org/2/reference/simple_stmts.html#the-assert-statement).

  - `k`. Optional. The same as `do_`.

#### Returns

The same as `given_`.

#### Example

```python
f = (
  assert_(True, lambda:
  print_("OK!")))

f()
```

Output:

    OK!

### `raise_`

Behaves the same way as Python's
[`raise`](https://docs.python.org/2/reference/simple_stmts.html#the-raise-statement)
statement. For details on the arguments below, see the documentation
linked.

#### Arguments

  - `ex_type`. Optional.

  - `ex_val`. Optional.

  - `tb_val`. Optional.

#### Returns

Theoretically `None`, but actually never returns because the `raise`
statement jumps control flow to whichever `except: ...` block is
closest, or failing that it crashes the program.

### `with_`

Wraps Python's
[with](https://docs.python.org/2/reference/compound_stmts.html#with)
statement, but is limited to only a single context binding at a time.

#### Arguments

  - `expr_k`. Something that can be called with no arguments to get the
    context manager.

  - `act_k`. Something that will be called with either one argument, or
    none, depending on whether context manager binds a value or not.

    If the context manager doesn't bind a value, i.e. if the equivalent
    `with` block in normal Python would have been `with x: ...` instead
    of `with x as y: ...`, then `act_k` will be called without any
    arguments.

    If the context manager _does_ bind a value, then `act_k` will be
    called with that value as the argument.

  - `k`. Optional (default `None`). The same as for `do_`.

#### Returns

The same as for `given_`.

#### Example

First, the imports.

```python
from contextlib import closing, contextmanager
from lambdak import *
import StringIO
```

The example of a context manager not binding a value. Here we define a
spurious context manager that just prints some text at the start and
finish.

```python
@contextmanager
def ctx():
  print "Start!"
  yield
  print "End!"

with_(ctx, lambda: None)()
```

Output:

    Start!
    End!

The example of a context manager binding a value. Here we show a more
real-world scenario, of opening a resource within the context manager,
doing something to it, and then getting its final value before the
context manager automatically closes it.

```python
with_(lambda: closing(StringIO.StringIO()), lambda s:
  do_(lambda: s.write("Hello, World!"), lambda:
  print_(s.getvalue())))()
```

Output:

    Hello, World!

### `cond_`

Evaluate a list of tests one by one until one of them evaluates to
`True`, and evaluate and return its corresponding value expression.

Short-circuiting: if one of the condition tests evaluates to `True`, it
won't try to evaluate any of the other tests and value expressions after
that one.

Should be used in the same way as Python's `if: ... elif: ... else:`
statement would be, or a switch statement in some other language.

#### Arguments

  - `test_pairs`. Must be a sequence (i.e. iterable, like a list) of
    tuples of (`test_expr`, `then_expr`).

    `test_expr` will be called with no arguments to get a boolean value
    to be tested.

    If the value is `True`, `then_expr` will be called with no arguments
    and the result will be passed on to the `k` function (see below).

    If the value is `False`, the next `test_expr` in the sequence will
    be called, and so on.

  - `default_expr`. If none of the `test_expr`s evaluated to `True`,
    then this expression will be called with no arguments and the result
    passed on to the `k` function. This argument is required as a way to
    force the developer to think about all possible cases. But as a
    convenience, you can pass in `None` and it will do the right thing.

  - `k`. Optional (default `None`). This must be a function which takes
    no arguments and returns either a lambdak (to indicate a continuing
    computation), or anything else (to indicate stopping).

    If you have effectful code in your `then_expr`s, you won't
    necessarily return a meaningful value from them; rather you will be
    returning the actions (lambdaks) themselves. As a convenience, you
    can use the handy `return_` function as this argument in those cases
    to just pass along that lambdak and carry out the action. See the
    second example below.

#### Returns

The same as `given_`. You can think of this as a let binding where one
binding will ultimately be chosen out of multiple possible bindings.

#### Example

A 'pure' value calculated and returned:

```python
cond_(
  [ (lambda: False, lambda: 0),
    (lambda: True, lambda: 1) ],
  None, # Default
  lambda val: # The computed value.
print_(val))()
```

Output:

    1

An 'effectful' action (lambdak) computed and returned:

```python
cond_(
  [ (lambda: False, lambda: print_(0)),
    (lambda: True, lambda: print_(1)) ],
  None,
return_)()
```

Output:

    1

The `return_` function works because it's the exact same thing as
`lambda x: x`, which is what we need as the last argument of `cond_` to
pass on the computed lambdak (action).

### `assign_`

Assign a value to a dict object given its key. This function can
be used to manipulate the module's global variables. Example shown
below.

#### Arguments

  - `nm`. The key to look up in the dict.

  - `v`. The value to assign to the corresponding object.

  - `d`. The dictto look in.

  - `k`. Optional (default `None`). Same as for `do_`.

#### Returns

The same as `given_`.

#### Example

To potentially change a global variable `x` to some value:

```python
test = assign_("x", 1, globals())
```

To actually change the value:

```python
test()
```

### `get_`

Get the value of an object in a dict given its key. Note that this
function doesn't have a continuation. It's a pure function with no side
effects (unless someone has changed the very mechanism of dict
lookups themselves), so it doesn't need one.

#### Arguments

  - `nm`. The key to look for.

  - `d`. The dictto look in.

#### Returns

The value corresponding to the given key `nm`.

#### Example

```python
x = get_("x", { "x": 1 })
print x
```

Output:

    1

### `del_`

Delete a key-value pair from a dict. This can also be used to delete a
global variable. See example below.

#### Arguments

  - `nm`. The key to look for.

  - `d`. The dict to look in.

  - `k`. Optional (default `None`). Same as for `do_`.

#### Returns

The same as `given_`.

#### Example

To immediately delete a global variable:

```python
# In global scope
x = 1

del_("x", globals())()
print x
```

Output:

    NameError: name 'x' is not defined

<!--
### `x_`
#### Arguments
#### Returns
#### Example

-->

