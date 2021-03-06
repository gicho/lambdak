# lambdak.py - functional programming with continuations in Python
from __future__ import print_function

class lambdak(object):
  '''A lambda with a continuation, to allow extended calculations.'''
  def __init__(self, k, x = ()):
    self.k = k
    self.x = x if x == () else (x,)

  def __call__(self, *args, **kwargs):
    k, x = self.k, self.x

    while k is not None:
      if args != () and kwargs != {}:
        l = k(*args, **kwargs)
        args = ()
        kwargs = {}
      elif args != ():
        l = k(*args)
        args = ()
      # If x is empty tuple, *x will be expanded into no arguments.
      else: l = k(*x)

      # If we didn't get back a lambdak, then we've reached the end of
      # the lambdak chain, and it's time to stop.
      if not isinstance(l, lambdak): return l
      k, x = l.k, l.x

    # If the lambdak we got back didn't have a continuation function,
    # then it's also time to stop.
    return None if x == () else x[0]

class continue_(object): pass
class break_(object): pass

def call_(k, *args): return None if k is None else k(*args)

def return_(x): return x

def const_(x): return lambda _: x

def given_(k): return lambdak(k)

def do_(expr_k, k = None):
  def act():
    expr_k()
    return call_(k)

  return lambdak(act)

def print_(x, k = None):
  def act():
    print(x)
    return call_(k)

  return lambdak(act)

def assert_(expr, k = None):
  def act():
    assert expr
    return call_(k)

  return lambdak(act)

def raise_(ex_type = None, ex_val = None, tb_val = None):
  def act():
    if ex_type is None: raise
    else: raise ex_type, ex_val, tb_val

  return lambdak(act)

def cond_(test_pairs, default_expr, k = None):
  for (test_expr, then_expr) in test_pairs:
    if test_expr(): return lambdak(k, then_expr())
  else: return lambdak(k, call_(default_expr))

def import_(mod_name, k):
  def act():
    m = __import__(mod_name)
    return call_(k, m)

  return lambdak(act)

def try_(expr_k, except_, else_ = None, finally_ = None):
  def act():
    try: y = lambdak(expr_k)()
    except: y = lambdak(except_)()
    else: lambdak(else_)()
    finally: return lambdak(finally_, y)

  return lambdak(act)

def for_else_(seq, act_k, else_, k = None):
  def act():
    for x in seq:
      y = lambdak(act_k, x)()
      if y == continue_: continue
      if y == break_: break
    else: lambdak(else_)()
    return call_(k)

  return lambdak(act)

def for_(seq, act_k, k = None): return for_else_(seq, act_k, None, k)

def while_else_(expr_k, act_k, else_, k = None):
  def act():
    while expr_k():
      y = lambdak(act_k)()
      if y == continue_: continue
      if y == break_: break
    else: lambdak(else_)()
    return call_(k)

  return lambdak(act)

def while_(expr_k, act_k, k = None):
  return while_else_(expr_k, act_k, None, k)

def setattr_(x, attr_name, attr_val, k = None):
  return do_(lambda: setattr(x, attr_name, attr_val), k)

def delattr_(x, attr_name, k = None):
  return do_(lambda: delattr(x, attr_name), k)

def modattr_(x, attr_name, f, k = None):
  def act():
    setattr(x, attr_name, f(getattr(x, attr_name)))
    return call_(k)

  return lambdak(act)

def with_(expr_k, act_k, k = None):
  def act():
    with expr_k() as x:
      if x is None: lambdak(act_k)()
      else: lambdak(act_k, x)()
    return call_(k)

  return lambdak(act)

def assign_(nm, v, d, k = None):
  def act():
    d[nm] = v
    return call_(k)

  return lambdak(act)

def get_(nm, d): return d[nm]

def del_(nm, d, k = None):
  def act():
    del d[nm]
    return call_(k)

  return lambdak(act)

def mod_(nm, f, d, k = None):
  def act():
    d[nm] = f(d[nm])
    return call_(k)

  return lambdak(act)

