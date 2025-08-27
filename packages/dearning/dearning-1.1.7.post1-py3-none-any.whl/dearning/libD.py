# libD.py

# === NumPy replacement alias ===
import numpy as np

class nd:
    array       = staticmethod(np.array)
    zeros       = staticmethod(np.zeros)
    ones        = staticmethod(np.ones)
    arange      = staticmethod(np.arange)
    reshape     = staticmethod(np.reshape)
    dot         = staticmethod(np.dot)
    mean        = staticmethod(np.mean)
    sum         = staticmethod(np.sum)
    clip        = staticmethod(np.clip)
    argmax      = staticmethod(np.argmax)
    argmin      = staticmethod(np.argmin)
    max         = staticmethod(np.max)
    min         = staticmethod(np.min)
    std         = staticmethod(np.std)
    var         = staticmethod(np.var)
    sqrt        = staticmethod(np.sqrt)
    exp         = staticmethod(np.exp)
    log         = staticmethod(np.log)
    log10       = staticmethod(np.log10)
    abs         = staticmethod(np.abs)
    sin         = staticmethod(np.sin)
    cos         = staticmethod(np.cos)
    tan         = staticmethod(np.tan)
    concatenate = staticmethod(np.concatenate)
    stack       = staticmethod(np.stack)
    vstack      = staticmethod(np.vstack)
    hstack      = staticmethod(np.hstack)
    eye         = staticmethod(np.eye)
    identity    = staticmethod(np.identity)
    rand        = staticmethod(np.random.rand)
    randn       = staticmethod(np.random.randn)
    randint     = staticmethod(np.random.randint)
    choice      = staticmethod(np.random.choice)
    shuffle     = staticmethod(np.random.shuffle)
    transpose   = staticmethod(np.transpose)
    where       = staticmethod(np.where)
    round       = staticmethod(np.round)
    floor       = staticmethod(np.floor)
    ceil        = staticmethod(np.ceil)
    linspace    = staticmethod(np.linspace)
    unique      = staticmethod(np.unique)
    argsort     = staticmethod(np.argsort)
    sort        = staticmethod(np.sort)
    repeat      = staticmethod(np.repeat)
    tile        = staticmethod(np.tile)
    all         = staticmethod(np.all)
    any         = staticmethod(np.any)

    # Linear algebra
    inv         = staticmethod(np.linalg.inv)
    det         = staticmethod(np.linalg.det)
    norm        = staticmethod(np.linalg.norm)
    svd         = staticmethod(np.linalg.svd)
    eig         = staticmethod(np.linalg.eig)

    # Data type conversion
    astype      = staticmethod(lambda x, dtype: x.astype(dtype))

    # Shape and size
    shape       = staticmethod(lambda x: x.shape)
    size        = staticmethod(lambda x: x.size)
    ndim        = staticmethod(lambda x: x.ndim)

# === Scipy Aliases ===
try:
    import scipy
    from scipy import optimize, stats, signal, special, spatial, integrate

    class sciD:
        optimize = optimize
        stats    = stats
        signal   = signal
        special  = special
        spatial  = spatial
        integrate = integrate

except ImportError:
    class sciD:
        optimize = None
        stats    = None
        signal   = None
        special  = None
        spatial  = None
        integrate = None

# === Python's math module alias ===
import math as pymath

class Domath:
    pi        = pymath.pi
    e         = pymath.e
    tau       = pymath.tau
    inf       = pymath.inf
    nan       = pymath.nan

    # Fungsi dasar
    sqrt      = staticmethod(pymath.sqrt)
    exp       = staticmethod(pymath.exp)
    log       = staticmethod(pymath.log)
    log10     = staticmethod(pymath.log10)
    log2      = staticmethod(pymath.log2)
    pow       = staticmethod(pymath.pow)

    # Trigonometri
    sin       = staticmethod(pymath.sin)
    cos       = staticmethod(pymath.cos)
    tan       = staticmethod(pymath.tan)
    asin      = staticmethod(pymath.asin)
    acos      = staticmethod(pymath.acos)
    atan      = staticmethod(pymath.atan)
    degrees   = staticmethod(pymath.degrees)
    radians   = staticmethod(pymath.radians)

    # Operasi pembulatan dan absolut
    floor     = staticmethod(pymath.floor)
    ceil      = staticmethod(pymath.ceil)
    trunc     = staticmethod(pymath.trunc)
    fabs      = staticmethod(pymath.fabs)

    # Fungsi lainnya
    copysign  = staticmethod(pymath.copysign)
    isfinite  = staticmethod(pymath.isfinite)
    isinf     = staticmethod(pymath.isinf)
    isnan     = staticmethod(pymath.isnan)
    gcd       = staticmethod(pymath.gcd)
    lcm       = staticmethod(pymath.lcm if hasattr(pymath, 'lcm') else lambda a, b: abs(a * b) // pymath.gcd(a, b))
    factorial = staticmethod(pymath.factorial)
    comb      = staticmethod(pymath.comb)
    perm      = staticmethod(pymath.perm)
