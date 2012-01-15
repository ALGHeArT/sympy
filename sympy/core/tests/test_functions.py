from sympy import (Lambda, Symbol, Function, Derivative, Subs, sqrt,
        log, exp, Rational, Float, sin, cos, acos, diff, I, re, im,
        E, expand, pi, O, Sum, S, polygamma, loggamma,
        Tuple, Dummy, Eq, Expr, symbols)
from sympy.utilities.pytest import XFAIL, raises
from sympy.abc import t, w, x, y, z
from sympy.core.function import PoleError
from sympy.utilities.iterables import subsets, variations

f, g, h = symbols('f g h', cls=Function)

def test_f_expand_complex():
    x = Symbol('x', real=True)

    assert f(x).expand(complex=True)        == I*im(f(x)) + re(f(x))
    assert exp(x).expand(complex=True)      == exp(x)
    assert exp(I*x).expand(complex=True)    == cos(x) + I*sin(x)
    assert exp(z).expand(complex=True)      == cos(im(z))*exp(re(z)) + \
                                             I*sin(im(z))*exp(re(z))

def test_bug1():
    e = sqrt(-log(w))
    assert e.subs(log(w),-x) == sqrt(x)

    e = sqrt(-5*log(w))
    assert e.subs(log(w),-x) == sqrt(5*x)

def test_general_function():
    nu = Function('nu')

    e = nu(x)
    edx = e.diff(x)
    edy = e.diff(y)
    edxdx = e.diff(x).diff(x)
    edxdy = e.diff(x).diff(y)
    assert e == nu(x)
    assert edx != nu(x)
    assert edx == diff(nu(x), x)
    assert edy == 0
    assert edxdx == diff(diff(nu(x), x), x)
    assert edxdy == 0

def test_derivative_subs_bug():
    l = Function('l')
    n = Function('n')

    e = diff(n(x), x)
    assert e.subs(n(x), l(x)) != e
    assert e.subs(n(x), l(x)) == Derivative(l(x), x)
    assert e.subs(n(x), -l(x)) == Derivative(-l(x), x)

    assert e.subs(x, y) == Derivative(n(y), y)

def test_derivative_subs_self_bug():
    d = diff(f(x), x)

    assert d.subs(d, y) == y


def test_derivative_linearity():
    n = Function('n')

    assert diff(-n(x), x) == -diff(n(x), x)
    assert diff(8*n(x), x) == 8*diff(n(x), x)
    assert diff(8*n(x), x) != 7*diff(n(x), x)
    assert diff(8*n(x)*x, x) == 8*n(x) + 8*x*diff(n(x), x)
    assert diff(8*n(x)*y*x, x) == 8*y*n(x) + 8*y*x*diff(n(x), x)

def test_derivative_evaluate():
    assert Derivative(sin(x), x) != diff(sin(x), x)
    assert Derivative(sin(x), x).doit() == diff(sin(x), x)

    assert Derivative(Derivative(f(x), x), x) == diff(f(x), x, x)
    assert Derivative(sin(x), x, 0) == sin(x)

def test_diff_symbols():
    assert diff(f(x, y, z), x, y, z) == Derivative(f(x, y, z), x, y, z)
    assert diff(f(x, y, z), x, x, x) == Derivative(f(x, y, z), x, x, x)
    assert diff(f(x, y, z), x, 3) == Derivative(f(x, y, z), x, 3)

    # issue 1929
    assert [diff(-z + x/y, sym) for sym in (z, x, y)] == [-1, 1/y, -x/y**2]
    assert diff(f(x, y, z), x, y, z, 2) == Derivative(f(x, y, z), x, y, z, z)
    assert diff(f(x, y, z), x, y, z, 2, evaluate=False) == \
        Derivative(f(x, y, z), x, y, z, z)
    assert Derivative(f(x, y, z), x, y, z)._eval_derivative(z) == \
        Derivative(f(x, y, z), x, y, z, z)
    assert Derivative(Derivative(f(x, y, z), x), y)._eval_derivative(z) == \
        Derivative(f(x, y, z), x, y, z)

def test_Lambda():
    e = Lambda(x, x**2)
    assert e(4) == 16
    assert e(x) == x**2
    assert e(y) == y**2

    assert Lambda(x, x**2) == Lambda(x, x**2)
    assert Lambda(x, x**2) == Lambda(y, y**2)
    assert Lambda(x, x**2) != Lambda(y, y**2+1)
    assert Lambda((x, y), x**y) == Lambda((y, x), y**x)
    assert Lambda((x, y), x**y) != Lambda((x, y), y**x)

    assert Lambda((x, y), x**y)(x, y) == x**y
    assert Lambda((x, y), x**y)(3, 3) == 3**3
    assert Lambda((x, y), x**y)(x, 3) == x**3
    assert Lambda((x, y), x**y)(3, y) == 3**y
    assert Lambda(x, f(x))(x) == f(x)
    assert Lambda(x, x**2)(e(x)) == x**4
    assert e(e(x)) == x**4

    assert Lambda((x, y), x+y).nargs == 2

    p = x, y, z, t
    assert Lambda(p, t*(x+y+z))(*p) == t * (x + y + z)

    assert Lambda(x, 2*x) + Lambda(y, 2*y) == 2*Lambda(x, 2*x)
    assert Lambda(x, 2*x) not in [ Lambda(x, x) ]

def test_IdentityFunction():
    assert Lambda(x, x) is Lambda(y, y) is S.IdentityFunction
    assert Lambda(x, 2*x) is not S.IdentityFunction
    assert Lambda((x, y), x) is not S.IdentityFunction

def test_Lambda_symbols():
    assert Lambda(x, 2*x).free_symbols == set()
    assert Lambda(x, x*y).free_symbols == set([y])

def test_Lambda_arguments():
    raises(TypeError, 'Lambda(x, 2*x)(x, y)')
    raises(TypeError, 'Lambda((x, y), x+y)(x)')

def test_Lambda_equality():
    assert Lambda(x, 2*x) != Lambda((x,y), 2*x)
    assert (Lambda(x, 2*x) == Lambda((x,y), 2*x)) is False
    assert Lambda((x, y), 2*x) == Lambda((x, y), 2*x)
    assert (Lambda((x, y), 2*x) != Lambda((x, y), 2*x)) is False
    assert Lambda(x, 2*x) != 2*x
    assert (Lambda(x, 2*x) == 2*x) is False

def test_Subs():
    assert Subs(f(x), x, 0).doit() == f(0)
    assert Subs(f(x**2), x**2, 0).doit() == f(0)
    assert Subs(f(x, y), (x, y), (0, 1)).doit() == f(0, 1)
    assert Subs(Subs(f(x, y), x, 0), y, 1).doit() == f(0, 1)
    raises(ValueError, 'Subs(f(x, y), (x, y), (0, 0, 1))')
    raises(ValueError, 'Subs(f(x, y), (x, x, y), (0, 0, 1))')

    assert len(Subs(f(x, y), (x, y), (0, 1)).variables) == 2
    assert all(isinstance(v, Dummy) for v in Subs(f(x, y),
        (x, y), (0, 1)).variables)
    assert Subs(f(x, y), (x, y), (0, 1)).point == Tuple(0, 1)

    assert Subs(f(x), x, 0) == Subs(f(y), y, 0)
    assert Subs(f(x, y), (x, y), (0, 1)) == Subs(f(x, y), (y, x), (1, 0))
    assert Subs(f(x)*y, (x, y), (0, 1)) == Subs(f(y)*x, (y, x), (0, 1))
    assert Subs(f(x)*y, (x, y), (1, 1)) == Subs(f(y)*x, (x, y), (1, 1))

    assert Subs(f(x), x, 0).subs(x, 1) == Subs(f(x), x, 0)
    assert Subs(f(x), x, 0).subs(x, 1).doit() == f(0)
    assert Subs(f(x), x, y).subs(y, 0) == Subs(f(x), x, 0)
    assert Subs(y*f(x), x, y).subs(y, 2) == Subs(2*f(x), x, 2)
    assert (2 * Subs(f(x), x, 0)).subs(Subs(f(x), x, 0), y) == 2*y

    assert Subs(f(x), x, 0).free_symbols == set([])
    assert Subs(f(x, y), x, z).free_symbols == set([y, z])

    assert Subs(f(x).diff(x), x, 0).doit() == Subs(f(x).diff(x), x, 0)
    assert Subs(1+f(x).diff(x), x, 0).doit() == 1 + Subs(f(x).diff(x), x, 0)
    assert Subs(y*f(x, y).diff(x), (x, y), (0, 2)).doit() == \
            2*Subs(Derivative(f(x, 2), x), x, 0)
    assert Subs(y**2*f(x), x, 0).diff(y) == 2*y*f(0)

    e = Subs(y**2*f(x), x, y)
    assert e.diff(y) == e.doit().diff(y) == y**2*Derivative(f(y), y) + 2*y*f(y)

    assert Subs(f(x), x, 0) + Subs(f(x), x, 0) == 2*Subs(f(x), x, 0)
    e1 = Subs(z*f(x), x, 1)
    e2 = Subs(z*f(y), y, 1)
    assert e1 + e2 == 2*e1
    assert e1.__hash__() == e2.__hash__()
    assert Subs(z*f(x+1), x, 1) not in [ e1, e2 ]
    assert Derivative(f(x),x).subs(x,g(x)) == Derivative(f(g(x)),g(x))


@XFAIL
def test_Subs2():
    # this reflects a limitation of subs(), probably won't fix
    assert Subs(f(x), x**2, x).doit() == f(sqrt(x))


def test_expand_function():
    assert expand(x+y) == x + y
    assert expand(x+y, complex=True) == I*im(x) + I*im(y) + re(x) + re(y)
    assert expand((x + y)**11, modulus=11) == x**11 + y**11

def test_function_comparable():
    assert sin(x).is_comparable == False
    assert cos(x).is_comparable == False

    assert sin(Float('0.1')).is_comparable   == True
    assert cos(Float('0.1')).is_comparable   == True

    assert sin(E).is_comparable     == True
    assert cos(E).is_comparable     == True

    assert sin(Rational(1,3)).is_comparable == True
    assert cos(Rational(1,3)).is_comparable == True

@XFAIL
def test_function_comparable_infinities():
    assert sin(oo).is_comparable    == False
    assert sin(-oo).is_comparable   == False
    assert sin(zoo).is_comparable   == False
    assert sin(nan).is_comparable   == False

def test_deriv1():
    # These all requre derivatives evaluated at a point (issue 1620) to work.
    # See issue 1525
    assert f(2*x).diff(x) == 2*Subs(Derivative(f(x), x), Tuple(x), Tuple(2*x))
    assert (f(x)**3).diff(x) == 3*f(x)**2*f(x).diff(x)
    assert (f(2*x)**3).diff(x) == 6*f(2*x)**2*Subs(Derivative(f(x), x), Tuple(x),
            Tuple(2*x))

    assert f(2+x).diff(x) == Subs(Derivative(f(x), x), Tuple(x), Tuple(x + 2))
    assert f(2+3*x).diff(x) == 3*Subs(Derivative(f(x), x), Tuple(x),
            Tuple(3*x + 2))
    assert f(3*sin(x)).diff(x) == 3*cos(x)*Subs(Derivative(f(x), x),
            Tuple(x), Tuple(3*sin(x)))

def test_deriv2():
    assert (x**3).diff(x) == 3*x**2
    assert (x**3).diff(x, evaluate=False) != 3*x**2
    assert (x**3).diff(x, evaluate=False) == Derivative(x**3, x)

    assert diff(x**3, x) == 3*x**2
    assert diff(x**3, x, evaluate=False) != 3*x**2
    assert diff(x**3, x, evaluate=False) == Derivative(x**3, x)

def test_func_deriv():
    assert f(x).diff(x) == Derivative(f(x), x)
    # issue 1435
    assert f(x, y).diff(x, y) - f(x, y).diff(y, x) == 0
    assert Derivative(f(x, y), x, y).args[1:] == (x, y)
    assert Derivative(f(x, y), y, x).args[1:] == (y, x)
    assert (Derivative(f(x, y), x, y) - Derivative(f(x, y), y, x)).doit() == 0

def test_suppressed_evaluation():
    a = sin(0, evaluate=False)
    assert a != 0
    assert a.func is sin
    assert a.args == (0,)

def test_function_evalf():
    def eq(a,b,eps):
        return abs(a-b) < eps
    assert eq(sin(1).evalf(15), Float("0.841470984807897"), 1e-13)
    assert eq(sin(2).evalf(25), Float("0.9092974268256816953960199",25), 1e-23)
    assert eq(sin(1+I).evalf(15), Float("1.29845758141598") + Float("0.634963914784736")*I, 1e-13)
    assert eq(exp(1+I).evalf(15), Float("1.46869393991588") + Float("2.28735528717884239")*I, 1e-13)
    assert eq(exp(-0.5+1.5*I).evalf(15), Float("0.0429042815937374") + Float("0.605011292285002")*I, 1e-13)
    assert eq(log(pi+sqrt(2)*I).evalf(15), Float("1.23699044022052") + Float("0.422985442737893")*I, 1e-13)
    assert eq(cos(100).evalf(15), Float("0.86231887228768"), 1e-13)

def test_extensibility_eval():
    class MyFunc(Function):
        @classmethod
        def eval(cls, *args):
            return (0,0,0)
    assert MyFunc(0) == (0,0,0)

def test_function_non_commutative():
    x = Symbol('x', commutative=False)
    assert f(x).is_commutative == False
    assert sin(x).is_commutative == False
    assert exp(x).is_commutative == False
    assert log(x).is_commutative == False

def test_function__eval_nseries():
    n = Symbol('n')

    assert sin(x)._eval_nseries(x,2,None) == x + O(x**2)
    assert sin(x+1)._eval_nseries(x,2,None) == x*cos(1) + sin(1) + O(x**2)
    assert sin(pi*(1-x))._eval_nseries(x,2,None) == pi*x + O(x**2)
    assert acos(1-x**2)._eval_nseries(x,2,None) == sqrt(2)*x + O(x**2)
    assert polygamma(n,x+1)._eval_nseries(x,2,None) == \
                   polygamma(n,1) + polygamma(n+1,1)*x + O(x**2)
    raises(PoleError, 'sin(1/x)._eval_nseries(x,2,None)')
    raises(PoleError, 'acos(1-x)._eval_nseries(x,2,None)')
    raises(PoleError, 'acos(1+x)._eval_nseries(x,2,None)')
    assert loggamma(1/x)._eval_nseries(x,0,None) \
           == log(x)/2 - log(x)/x - 1/x + O(1, x)
    assert loggamma(log(1/x)).nseries(x,n=1,logx=y) == loggamma(-y)

def test_doit():
    n = Symbol('n', integer=True)
    f = Sum(2 * n * x, (n, 1, 3))
    d = Derivative(f, x)
    assert d.doit() == 12
    assert d.doit(deep = False) == Sum(2*n, (n, 1, 3))

def test_evalf_default():
    from sympy.functions.special.gamma_functions import polygamma
    assert type(sin(4.0)) == Float
    assert type(re(sin(I + 1.0))) == Float
    assert type(im(sin(I + 1.0))) == Float
    assert type(sin(4)) == sin
    assert type(polygamma(2.0,4.0)) == Float
    assert type(sin(Rational(1,4))) == sin

def test_issue2300():
    args = [x, y, S(2), S.Half]
    def ok(a):
        """Return True if the input args for diff are ok"""
        if not a: return False
        if a[0].is_Symbol is False: return False
        s_at = [i for i in range(len(a)) if a[i].is_Symbol]
        n_at = [i for i in range(len(a)) if not a[i].is_Symbol]
        # every symbol is followed by symbol or int
        # every number is followed by a symbol
        return (all(a[i+1].is_Symbol or a[i+1].is_Integer
            for i in s_at if i+1<len(a)) and
            all(a[i+1].is_Symbol
            for i in n_at if i+1<len(a)))
    eq = x**10*y**8
    for a in subsets(args):
        for v in variations(a, len(a)):
            if ok(v):
                noraise = eq.diff(*v)
            else:
                raises(ValueError, 'eq.diff(*v)')

def test_derivative_numerically():
    from random import random
    z0 = random() + I*random()
    assert abs(Derivative(sin(x), x).doit_numerically(z0) - cos(z0)) < 1e-15

def test_fdiff_argument_index_error():
    from sympy.core.function import ArgumentIndexError
    class myfunc(Function):
        nargs = 1
        def fdiff(self, idx):
            raise ArgumentIndexError
    mf = myfunc(x)
    assert mf.diff(x) == Derivative(mf, x)
    raises(TypeError, 'myfunc(x, x)')

def test_deriv_wrt_function():
    xfunc = Function('x')
    yfunc = Function('y')
    x = xfunc(t)
    xd = diff(x, t)
    xdd = diff(xd, t)
    y = yfunc(t)
    yd = diff(y, t)

    assert diff(x, t) == xd
    assert diff(2 * x + 4, t) == 2 * xd
    assert diff(2 * x + 4 + y, t) == 2 * xd + yd
    assert diff(2 * x + 4 + y * x, t) == 2 * xd + x * yd + xd * y
    assert diff(2 * x + 4 + y * x, x) == 2 + y
    assert (diff(4 * x**2 + 3 * x + x * y, t) == 3 * xd + x * yd + xd * y +
            8 * x * xd)
    assert (diff(4 * x**2 + 3 * xd + x * y, t) ==  3 * xdd + x * yd + xd * y +
            8 * x * xd)
    assert diff(4 * x**2 + 3 * xd + x * y, xd) == 3
    assert diff(4 * x**2 + 3 * xd + x * y, xdd) == 0
    assert diff(sin(x), t) == xd * cos(x)
    assert diff(exp(x), t) == xd * exp(x)
    assert diff(sqrt(x), t) == xd / (2 * sqrt(x))

def test_diff_wrt_value():
    assert Expr()._diff_wrt == False
    assert x._diff_wrt == True
    assert f(x)._diff_wrt == True
    assert Derivative(f(x),x)._diff_wrt == True
    assert Derivative(x**2,x)._diff_wrt == False

def test_diff_wrt():
    fx = f(x)
    dfx = diff(f(x),x)
    ddfx = diff(f(x),x,x)

    assert diff(sin(fx)+fx**2, fx) == cos(fx)+2*fx
    assert diff(sin(dfx)+dfx**2, dfx) == cos(dfx)+2*dfx
    assert diff(sin(ddfx)+ddfx**2, ddfx) == cos(ddfx)+2*ddfx
    assert diff(fx**2, dfx) == 0
    assert diff(fx**2, ddfx) == 0
    assert diff(dfx**2, fx) == 0
    assert diff(dfx**2, ddfx) == 0
    assert diff(ddfx**2, dfx) == 0

    assert diff(fx*dfx*ddfx, fx) == dfx*ddfx
    assert diff(fx*dfx*ddfx, dfx) == fx*ddfx
    assert diff(fx*dfx*ddfx, ddfx) == fx*dfx

    assert diff(f(x), x).diff(f(x)) == 0
    assert (sin(f(x)) - cos(diff(f(x), x))).diff(f(x)) == cos(f(x))

    assert diff(sin(fx), fx, x) == diff(sin(fx), x, fx)

    # Chain rule cases
    assert f(g(x)).diff(x) ==\
        Derivative(f(g(x)),g(x))*Derivative(g(x),x)
    assert diff(f(g(x),h(x)),x) ==\
        Derivative(f(g(x), h(x)), g(x))*Derivative(g(x), x) +\
        Derivative(f(g(x), h(x)), h(x))*Derivative(h(x), x)
    assert f(sin(x)).diff(x) == Derivative(f(sin(x)),sin(x))*cos(x)

    assert diff(f(g(x)),g(x)) == Derivative(f(g(x)),g(x))

def test_diff_wrt_not_allowed():
    raises(ValueError, 'diff(sin(x**2),x**2)')
    raises(ValueError, 'diff(exp(x*y)),x*y')
    raises(ValueError, 'diff(1+x,1+x)')

def test_klein_gordon_lagrangian():
    m = Symbol('m')
    phi = Function('phi')(x,t)

    L = -(diff(phi,t)**2 - diff(phi,x)**2 - m**2*phi**2)/2
    eqna = Eq(diff(L,phi) - diff(L,diff(phi,x),x) - diff(L,diff(phi,t),t), 0)
    eqnb = Eq(diff(phi,t,t) - diff(phi,x,x) + m**2*phi, 0)
    assert eqna == eqnb

def test_sho_lagrangian():
    m = Symbol('m')
    k = Symbol('k')
    x = Function('x')(t)

    L = m*diff(x,t)**2/2 - k*x**2/2
    eqna = Eq(diff(L,x), diff(L,diff(x,t),t))
    eqnb = Eq(-k*x, m*diff(x,t,t))
    assert eqna == eqnb

    assert diff(L,x,t) == diff(L,t,x)
    assert diff(L,diff(x,t),t) == m*diff(x,t,2)
    assert diff(L,t,diff(x,t)) == -k*x + m*diff(x,t,2)

def test_straight_line():
    f = Function('f')(x)

    L = sqrt(1 + diff(f,x)**2)
    assert diff(L,f) == 0
    assert diff(L, diff(f,x)) == diff(f,x)/sqrt(1 + diff(f,x)**2)

def test_sort_variable():
    vsort = Derivative._sort_variables

    assert vsort((x,y,z)) == [x, y, z]
    assert vsort((h(x),g(x),f(x))) == [f(x), g(x), h(x)]
    assert vsort((z,y,x,h(x),g(x),f(x))) == [x, y, z, f(x), g(x), h(x)]
    assert vsort((x,f(x),y,f(y))) == [x, f(x), y, f(y)]
    assert vsort((y,x,g(x),f(x),z,h(x),y,x)) ==\
        [x, y, f(x), g(x), z, h(x), x, y]
    assert vsort((z,y,f(x),x,f(x),g(x))) == [y, z, f(x), x, f(x), g(x)]
    assert vsort((z,y,f(x),x,f(x),g(x),z,z,y,x)) ==\
        [y, z, f(x), x, f(x), g(x), x, y, z, z]

def test_unhandled():
    class MyExpr(Expr):
        def _eval_derivative(self, s):
            if not s.name.startswith('diff_wrt'):
                return self
            else:
                return None

    expr = MyExpr(x,y,z)
    assert diff(expr,x,y,f(x),z) == Derivative(expr,f(x),z)
    assert diff(expr,f(x),x) == Derivative(expr,f(x),x)
    
@XFAIL
def test_issue_1612() :
   x= Symbol("x")
   assert Symbol('f')(x) == Function('f')(x)
