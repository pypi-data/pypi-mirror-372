## \file cucomponents.py
# \brief This file contains the module to model complex uncertain values.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#          Thomas Reidemeister</a>

## \namespace scuq::cucomponents
# \brief This namespace contains the classes to evaluate the
#        uncertainty of complex-valued functions.

## \defgroup cucomponents The Complex Uncertainty Module
#
# This module contains classes to model complex uncertain values.
# \attention You should either use the module ucomponents or this module.
#            Do not use both modules at once!
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \addtogroup cucomponents 
# @{

# builtin modules
import numpy

# local modules
import scuq.arithmetic as arithmetic
import scuq.ucomponents as ucomponents
import scuq.quantities as quantities
import scuq.units as units


def complex_to_matrix(value):
    """! @brief This function transforms a complex value into a matrix.
    @param value The complex value.
    @return A 2x2-matrix containing the value."""
    value = complex(value)
    re = value.real
    im = value.imag
    return numpy.matrix([[re, -im], [im, re]])


class CUncertainComponent:
    """! @brief This is the abstract super class of all complex valued uncertain
    components. Despite defining the interface for complex valued uncertain
    components, it also provides a set of factory methods that act as an
    interface for <tt>numpy</tt>."""

    def depends_on(self):
        """! @brief This abstact method should return the set of CUncertainInput instances,
        on which this instance depends on.
        @param self
        @return A list of CUncertainInputs this instance depends on.
        @attention This method needs to be overriden to have an effect."""
        raise NotImplementedError

    def get_value(self):
        """! @brief This abstract method should return the complex value of this
        component.
        @param self
        @return The value of this component.
        @attention This method needs to be overriden to have an effect."""
        raise NotImplementedError

    def get_uncertainty(self, x):
        """! @brief This abstact method should return the partial derivate of this component
         with respect to the input <tt>x</tt>.
        @param self
        @param x An uncertain input.
        @return The uncertainty of this component with respect to the input."""
        raise NotImplementedError

    def get_a_value(self):
        """! @brief This method returns the value of this component as a 2x2-matrix.
        @param self
        @return The complex value of this component in matrix form."""
        return complex_to_matrix(self.get_value())

    def exp(self):
        """! @brief Get the exponential of this instance.
        Let this instance be \f$x\f$ then this method returns \f$e^x\f$.
        @param self
        @return The exponential value of this instance."""
        return Exp(self);

    def log(self):
        """! @brief Get the natural logarithm of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\ln(x)\f$.
        @param self
        @return The natural logarithm of this instance."""
        return Log(self, numpy.e)

    def log10(self):
        """! @brief Get the decadic logarithm of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\log_{10}(x)\f$.
        @param self
        @return The decadic logarithm of this instance."""
        return Log(self, 10.0)

    def log2(self):
        """! @brief Get the binary logarithm of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\log_{2}(x)\f$.
        @param self
        @return The binary logarithm of this instance."""
        return Log(self, 2.0)

    def sqrt(self):
        """! @brief Get the square-root of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\sqrt{x}\f$.
        @param self
        @return The square-root of this instance."""
        return Sqrt(self)

    def square(self):
        """! @brief Get the square of this instance.
        Let this instance be \f$x\f$ then this method returns \f$x \cdot x\f$.
        @param self
        @return The square of this instance."""
        return self * self

    def sin(self):
        """! @brief Get the sine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\sin(x)\f$.
        @param self
        @return The sine of this instance."""
        return Sin(self)

    def cos(self):
        """! @brief Get the cosine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\cos(x)\f$.
        @param self
        @return The cosine of this instance."""
        return Cos(self)

    def tan(self):
        """! @brief Get the tangent of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\tan(x)\f$.
        @param self
        @return The tangent of this instance."""
        return Tan(self)

    def arcsin(self):
        """! @brief Get the inverse sine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\sin^{-1}(x)\f$.
        @param self
        @return The inverse sine of this instance."""
        return ArcSin(self)

    def arccos(self):
        """! @brief Get the inverse cosine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\cos^{-1}(x)\f$.
        @param self
        @return The inverse cosine of this instance."""
        return ArcCos(self)

    def arctan(self):
        """! @brief Get the inverse tangent of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\tan^{-1}(x)\f$.
        @param self
        @return The inverse tangent of this instance."""
        return ArcTan(self)

    def arctan2(self, y):
        """! @brief Get the two-argument inverse tangent of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\tan^{-1}(x)\f$.
        @param self
        @param y Another component of uncertainty.
        @return The two-argument inverse tangent of this instance."""
        return ArcTan2(self, y)

    def sinh(self):
        """! @brief Get the hyperbolic sine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\sinh(x)\f$.
        @param self
        @return The hyperbolic sine of this instance."""
        return Sinh(self)

    def cosh(self):
        """! @brief Get the hyperbolic cosine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\cosh(x)\f$.
        @param self
        @return The hyperbolic cosine of this instance."""
        return Cosh(self)

    def tanh(self):
        """! @brief Get the hyperbolic tangent of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\tanh(x)\f$.
        @param self
        @return The hyperbolic cosine of this instance."""
        return Tanh(self)

    def arcsinh(self):
        """! @brief Get the inverse hyperbolic sine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\sinh^{-1}(x)\f$.
        @param self
        @return The inverse hyperbolic sine of this instance."""
        return ArcSinh(self)

    def arccosh(self):
        """! @brief Get the inverse hyperbolic cosine of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\cosh^{-1}(x)\f$.
        @param self
        @return The inverse hyperbolic cosine of this instance."""
        return ArcCosh(self)

    def arctanh(self):
        """! @brief Get the inverse hyperbolic tangent of this instance.
        Let this instance be \f$x\f$ then this method returns \f$\tanh^{-1}(x)\f$.
        @param self
        @return The inverse hyperbolic tangent of this instance."""
        return ArcTanh(self)

    def hypot(self, y):
        """! @brief Calculate the hypothenusis of this and another complex-valued
        argument.
        @param self
        @param y another component of uncertainty.
        @return \f$\sqrt{x^2 + y^2}\f$"""
        return Sqrt(self ** self + y ** y)

    def __abs__(self):
        """! @brief Return the absolute value of this instance.
        Let this instance be \f$\mathbf{z} = x + j y\f$ then this method returns 
        @f$\sqrt{x^2 + y^2}\f$.
        @param self
        @return The absolute value of this instance."""
        return Abs(self)

    def fabs(self):
        """! @brief Return the absolute value of this instance.
        Let this instance be \f$\mathbf{z} = x + j y\f$ then this method returns 
        @f$\sqrt{x^2 + y^2}\f$.
        @param self
        @return The absolute value of this instance."""
        return Abs(self)

    def __neg__(self):
        """! @brief Negate this instance.
        @param self
        @return The negative of this instance."""
        return Neg(self)

    def __invert__(self):
        """! @brief Get the inverse of this instance.
        Let this instance be \f$x\f$ then this method returns \f$x^{-1}\f$.
        @param self
        @return The inverse of this instance."""
        return Inv(self)

    def conjugate(self):
        """! @brief Get the conjuagte complex value of this instance.
        @param self
        @return the conjuagte complex value of this instance."""
        return Conjugate(self)

    def __add__(self, y):
        """! @brief Add another instance to this instance.
        @param self
        @param y Another uncertain value.
        @return The sum of this instance and the other instance."""
        return Add(self, y)

    def __sub__(self, y):
        """! @brief Subtract another instance from this instance.
        @param self
        @param y Another uncertain value.
        @return The difference of this instance and the other instance. """
        return Sub(self, y)

    def __mul__(self, y):
        """! @brief Multiply another instance with this instance.
        @param self
        @param y Another uncertain value.
        @return The product of this instance and the other instance."""
        return Mul(self, y)

    def __truediv__(self, y):
        """! @brief Divide this instance by another instance.
        @param self
        @param y Another uncertain value.
        @return The result of the respective operation."""
        return Div(self, y)

    def __pow__(self, y):
        """! @brief Raise this instance to the power of the argument.
        @param self
        @param y Another uncertain value.
        @return The result of the respective operation."""
        return Pow(self, y)

    def __radd__(self, y):
        """! @brief Add another instance to this instance.
        @param self
        @param y Another uncertain value.
        @return The sum of this instance and the other instance."""
        assert (isinstance(y, CUncertainComponent))
        return Add(y, self)

    def __rsub__(self, y):
        """! @brief Subtract another instance from this instance.
        @param self
        @param y Another uncertain value.
        @return The difference of this instance and the other instance. """
        assert (isinstance(y, CUncertainComponent))
        return Sub(y, self)

    def __rmul__(self, y):
        """! @brief Multiply another instance with this instance.
        @param self
        @param y Another uncertain value.
        @return The product of this instance and the other instance."""
        assert (isinstance(y, CUncertainComponent))
        return Mul(y, self)

    def __rtruediv__(self, y):
        """! @brief Divide this instance by another instance.
        @param self
        @param y Another uncertain value.
        @return The result of the respective operation."""
        assert (isinstance(y, CUncertainComponent))
        return Div(y, self)

    def __rpow__(self, y):
        """! @brief Raise this instance to the power of the argument.
        @param self
        @param y Another uncertain value.
        @return The result of the respective operation."""
        assert (isinstance(y, CUncertainComponent))
        return Pow(y, self)

    def value_of(value):
        """! @brief This factory method converts the argument to a
        complex uncertain value.
        @param value A numeric value.
        @return An instance of CUncertainComponent."""
        if (isinstance(value, CUncertainComponent)):
            return value
        else:
            return CUncertainInput(value, 0.0, 0.0, arithmetic.INFINITY)

    value_of = staticmethod(value_of)

    def set_context(self, c):
        """! @brief This assigns a context to the component.
        This context is only needed for evaluating __str__
        @param self
        @param c An instance of Context"""
        assert (isinstance(c, Context))
        self._context = c

    def get_context(self):
        """! @brief This returns the assigned context of the component.
        This context is only needed for evaluating __str__
        @return c The Context of the component or <tt>None</tt>."""
        try:
            context = self._context
            return context
        except AttributeError:
            return None

    def __str__(self):
        """! @brief This method prints the component of uncertainty.
        @param self
        @return A string describing this component"""
        try:
            context = self._context
            u = context.uncertainty(self)
            v = self.get_value()
            return "Value = " + str(v) + "; Uncertainty =\n " + str(u)
        except AttributeError:
            context = Context()
            u = context.uncertainty(self)
            v = self.get_value()
            return "Value = " + str(v) + " ; Uncertainty =\n " + str(u) + " [NC]"

    def __coerce__(self, other):
        """! @brief Implementation of coercion rules.
        \see Coercion - The page describing the coercion rules."""
        if (isinstance(other, CUncertainComponent)):
            return (self, other)
        elif (isinstance(other, quantities.Quantity)):
            new_self = quantities.Quantity.value_of(self)
            return (new_self, other)
        elif (isinstance(other, ucomponents.UncertainComponent)):
            raise NotImplementedError("You must not mix scalar and"
                                      + " complex-valued uncertain values")
        elif (isinstance(other, arithmetic.RationalNumber)
              or isinstance(other, int)
              or isinstance(other, int)
              or isinstance(other, float)
              or isinstance(other, complex)):
            other = CUncertainComponent.value_of(other)
            return (self, other)
        elif isinstance(other, units.Unit):
            raise NotImplementedError("You cannot declare a unit as uncertain." +
                                      " Please use the quantities module" +
                                      " for that!")
        else:
            raise NotImplementedError()


class CUncertainInput(CUncertainComponent):
    """! @brief This class models a complex-valued input of a function."""

    def __init__(self, value, u_real, u_imag, dof=arithmetic.INFINITY):
        """! @brief The default constructor.
        @param self
        @param value The value of this instance.
        @param u_real The uncertainty of the real part.
        @param u_imag The uncertainty of the imaginary part.
        @param dof The degrees of freedom of the input.
        @attention You must not declare instances of quantities.QuantityQuantity as
                    uncertain. Instead encapsulate an uncertain value inside
                    a quantity.
        @see UncertainQuantity.py"""

        if (isinstance(value, numpy.ndarray) and value.dtype == quantities.Quantity):
            raise TypeError("You cannot declare an array of quantities as uncertain")
        if (isinstance(value, quantities.Quantity)):
            raise TypeError("You cannot declare an instance of quantity as uncertain")

        value = complex(value)
        self._value = value
        self._avalue = complex_to_matrix(value)
        u_real = float(u_real)
        u_imag = float(u_imag)
        self._jac = numpy.matrix([[u_real, 0],
                                  [0, u_imag]])
        self._dof = dof

    def depends_on(self):
        """! @brief Returns a list that contains this instance only.
        @param self
        @return A list."""
        return [self]

    def get_value(self):
        """! @brief Get the value of this input.
        @param self
        @return The value of this input"""
        return self._value

    def get_a_value(self):
        """! @brief Get the value as array.
        @param self
        @return The value of this input as array."""
        return self._avalue

    def get_uncertainty(self, x):
        """! @brief If <tt>x == self</tt> get the uncertainty of the current node,
        otherwise return a matrix of zeros.
        @param self
        @param x Another instance of CUncertainInput
        @return The uncertainty of this instance with respect to the argument."""
        if (self is x):
            return self._jac
        else:
            return numpy.zeros((2, 2))

    def get_dof(self):
        """! @brief Get the degrees of freedom assigned to this input.
        @param self
        @return The degrees of freedom assigned to this input."""
        return self._dof

    def __setstate__(self, state):
        """! @brief This method provides an interface for deserializing objects using
        pickle.
        @param self
        @param state The state to be restored."""
        self._value, self._avalue, self._jac = state

    def __getstate__(self):
        """! @brief This method provides an interface for serializing objects using
        pickle.
        @param self
        @return The state of this component."""
        return (self._value, self._avalue, self._jac)


class CUnaryOperation(CUncertainComponent):
    """! @brief This abstract class models an unary operation. """

    def __init__(self, sibling):
        """! @brief The default constructor.
        @param self
        @param sibling The sibling of this operation."""
        self._sibling = CUncertainComponent.value_of(sibling)

    def get_sibling(self):
        """! @brief Get the sibling of this operation.
        @param self
        @return The sibling"""
        return self._sibling

    def depends_on(self):
        """! @brief Get the instances of CUncertainInput that this instance
        depends on.
        @param self
        @return A list containing the instances of CUncertainInput that this 
                 instance depends on."""
        # return [ u for u in self._sibling.depends_on() if u not in locals()['_[1]'] ]  #us.clearDuplicates(self._sibling.depends_on())
        return set([u for u in self._sibling.depends_on()])  # us.clearDuplicates(self._sibling.depends_on())


class CBinaryOperation(CUncertainComponent):
    """! @brief This abstract class models a binary operation. """

    def __init__(self, left, right):
        """! @brief The default constructor.
        @param self
        @param left The left sibling sibling of this operation.
        @param right The right sibling sibling of this operation."""
        self._left = CUncertainComponent.value_of(left)
        self._right = CUncertainComponent.value_of(right)

    def get_left(self):
        """! @brief Get the left sibling of this operation.
        @param self
        @return The sibling"""
        return self._left

    def get_right(self):
        """! @brief Get the right sibling of this operation.
        @param self
        @return The sibling"""
        return self._right

    def depends_on(self):
        """! @brief Get the instances of CUncertainInput that this instance
        depends on.
        @param self
        @return A list containing the instances of CUncertainInput that this 
                instance depends on."""
        #        return [ u for u in self._left.depends_on()+self._right.depends_on() if u not in locals()['_[1]'] ] #us.clearDuplicates(self._left.depends_on()+self._right.depends_on())
        return set(self._left.depends_on()).union(
            set(self._right.depends_on()))  # us.clearDuplicates(self._left.depends_on()+self._right.depends_on())


class Exp(CUnaryOperation):
    """! @brief @brief This class models the exponential function \f$e^x\f$.
     \f$x\f$ denotes the sibling of this instance. """

    def get_value(self):
        """! @brief Get the value of this component.
        @param self
        @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.exp(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
        @param self
        @param x The argument of the partial derivation.
        @return The partial derivate."""
        jac = self.get_a_value()
        return jac * self.get_sibling().get_uncertainty(x)


class Log(CUnaryOperation):
    """! @brief @brief This class models logarithms having a real base. 
     However, the base cannot be uncertain."""

    def __init__(self, sibling, base=numpy.e):
        """! @brief The default constructor.
        @param self
        @param sibling The sibling of this instance.
        @param base The base of the logarithm (must be a real number)."""
        CUnaryOperation.__init__(self, sibling)
        base = float(base)
        self._base = base

    def get_value(self):
        """! @brief Get the value of this component.
        @param self
        @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.log(x) / numpy.log(self._base)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
        @return The partial derivate."""

        # create the complex jacobi matrix
        z = self.get_sibling().get_value()
        diff_val = 1.0 / (z * numpy.log(self._base))
        # transform it, since it is analytical
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Sqrt(CUnaryOperation):
    """! @brief This class models taking the square root of an uncertain component."""

    def get_value(self):
        """! @brief Get the value of this component.
        @param self
        @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.sqrt(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
        @param self
        @param x The argument of the partial derivation.
        @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 0.5 / numpy.sqrt(z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Sin(CUnaryOperation):
    """! @brief This class models the sine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.sin(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = numpy.cos(z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Cos(CUnaryOperation):
    """! @brief This class models the cosine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.cos(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = -numpy.sin(z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Tan(CUnaryOperation):
    """! @brief This class models the tangent function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.tan(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 1.0 / (numpy.cos(z) * numpy.cos(z))
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class ArcSin(CUnaryOperation):
    """! @brief This class models the inverse sine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.arcsin(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 1.0 / numpy.sqrt(1.0 - (z * z))
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class ArcCos(CUnaryOperation):
    """! @brief This class models the inverse cosine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.arccos(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = -1.0 / numpy.sqrt(1.0 - (z * z))
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class ArcTan(CUnaryOperation):
    """! @brief This class models the inverse tangent function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.arctan(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = -1.0 / (1.0 + (z * z))
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Sinh(CUnaryOperation):
    """! @brief This class models the hyperbolic sine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.sinh(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = numpy.cosh(z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Cosh(CUnaryOperation):
    """! @brief This class models the hyperbolic cosine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.cosh(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = numpy.sinh(z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Tanh(CUnaryOperation):
    """! @brief This class models the hyperbolic tangent function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.tanh(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 1.0 / (numpy.cosh(z) * numpy.cosh(z))
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class ArcSinh(CUnaryOperation):
    """! @brief This class models the inverse hyperbolic sine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.arcsinh(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 1.0 / numpy.sqrt(1.0 + z * z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class ArcCosh(CUnaryOperation):
    """! @brief This class models the inverse hyperbolic cosine function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.arccosh(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 1.0 / (numpy.sqrt(z - 1) * numpy.sqrt(z + 1))
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class ArcTanh(CUnaryOperation):
    """! @brief This class models the inverse hyperbolic tangent function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.arctanh(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = 1.0 / (1 - z * z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Abs(CUnaryOperation):
    """! @brief This class models taking the absolute value of a complex function."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.abs(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        val = self.get_sibling().get_value()
        xr = val.real
        y = val.imag
        x_1 = xr / (xr * xr + y * y)
        x_2 = y / (xr * xr + y * y)
        jac = numpy.matrix([[x_1, x_2], [0, 0]])
        return jac * self.get_sibling().get_uncertainty(x)


class Conjugate(CUnaryOperation):
    """! @brief This class models taking the negative of a complex value."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return numpy.conjugate(x)

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        jac = numpy.matrix([[1, 0], [0, -1]])
        return jac * self.get_sibling().get_uncertainty(x)


class Neg(CUnaryOperation):
    """! @brief This class models taking the negative of a complex value."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return -x

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        jac = numpy.matrix([[-1, 0], [0, -1]])
        return jac * self.get_sibling().get_uncertainty(x)


class Inv(CUnaryOperation):
    """! @brief This class models inverting complex values. Let an instance of
     this class model the complex value @f$x@f$ then this class
     models @f$\frac{1}{x}@f$."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        x = self.get_sibling().get_value()
        return 1.0 / x

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        z = self.get_sibling().get_value()
        diff_val = -1.0 / (z * z)
        jac = complex_to_matrix(diff_val)
        return jac * self.get_sibling().get_uncertainty(x)


class Add(CBinaryOperation):
    """! @brief This class models adding two complex values."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        lhs = self.get_left().get_value()
        rhs = self.get_right().get_value()
        return lhs + rhs

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        lhs = self.get_left().get_uncertainty(x)
        rhs = self.get_right().get_uncertainty(x)
        return lhs + rhs


class Sub(CBinaryOperation):
    """! @brief This class models taking the difference of two complex values."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        lhs = self.get_left().get_value()
        rhs = self.get_right().get_value()
        return lhs - rhs

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        lhs = self.get_left().get_uncertainty(x)
        rhs = self.get_right().get_uncertainty(x)
        return lhs - rhs


class Mul(CBinaryOperation):
    """! @brief This class models multiplying two complex values."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        lhs = self.get_left().get_value()
        rhs = self.get_right().get_value()
        return lhs * rhs

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        lhs = self.get_left().get_uncertainty(x)
        lhs_val = self.get_left().get_a_value()
        rhs = self.get_right().get_uncertainty(x)
        rhs_val = self.get_right().get_a_value()
        return rhs_val * lhs + lhs_val * rhs


class Div(CBinaryOperation):
    """! @brief This class models dividing two complex values."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        lhs = self.get_left().get_value()
        rhs = self.get_right().get_value()
        return lhs / rhs

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        lhs = self.get_left().get_uncertainty(x)
        lhs_val = self.get_left().get_value()
        rhs = self.get_right().get_uncertainty(x)
        rhs_val = self.get_right().get_value()

        return complex_to_matrix(1.0 / rhs_val) * lhs + \
               complex_to_matrix(-lhs_val / (rhs_val * rhs_val)) * rhs


class Pow(CBinaryOperation):
    """! @brief This class models complex powers."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        lhs = self.get_left().get_value()
        rhs = self.get_right().get_value()
        return lhs ** rhs

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        lhs = self.get_left().get_uncertainty(x)
        lhs_val = self.get_left().get_value()
        rhs = self.get_right().get_uncertainty(x)
        rhs_val = self.get_right().get_value()

        return complex_to_matrix(rhs_val * lhs_val ** (rhs_val - 1.0)) * lhs + \
               complex_to_matrix(lhs_val ** rhs_val * numpy.log(lhs_val)) * rhs


class ArcTan2(CBinaryOperation):
    """! @brief This class models two-argument inverse tangent."""

    def get_value(self):
        """! @brief Get the value of this component.
         @param self
         @return The value of this component."""
        lhs = self.get_left().get_value()
        rhs = self.get_right().get_value()
        # since numpy doesn't provide arctan2 for complex values
        # we define it here
        return (0 - 1j) * numpy.log((lhs + (0 - 1j) * rhs) \
                                    / numpy.sqrt(lhs * lhs + rhs * rhs))

    def get_uncertainty(self, x):
        """! @brief Get the partial derivate of this component with respect to
         the given argument.
         @param self
         @param x The argument of the partial derivation.
         @return The partial derivate."""
        lhs = self.get_left().get_uncertainty(x)
        lhs_val = self.get_left().get_value()
        rhs = self.get_right().get_uncertainty(x)
        rhs_val = self.get_right().get_value()

        return complex_to_matrix(rhs_val / (rhs_val ** 2.0 + lhs_val ** 2.0)) * lhs + \
               complex_to_matrix(lhs_val / (rhs_val ** 2.0 + lhs_val ** 2.0)) * rhs


class Context:
    """! @brief \brief This class provides a context for complex-valued uncertainty
     evaluations. It manages the correlation coefficients and
     is able to evaluate the effective degrees of freedom."""

    def _check_cmatrix(matrix):
        """! @brief Helper function to verify matrices of corellation coefficients.
         @param matrix The matrix to check.
         \exception TypeError If the argument is invalid"""
        if (not isinstance(matrix, numpy.matrix)):
            raise TypeError("Expecting a 2x2 matrix of corelation coefficients")
        if (matrix.shape != (2, 2)):
            raise TypeError("Expecting a 2x2 matrix of corelation coefficients")
        # if(sum(matrix > 1.0)):
        #    raise TypeError("Expecting a matrix of corelation coefficients <= 1.0")

    _check_cmatrix = staticmethod(_check_cmatrix)

    def __init__(self):
        """! @brief The default constructor. It initializes the dictionary of
         correlation matrices.
         @param self"""

        self._correlation = dict()

    def gaussian(self, val, u_r, u_i, dof=arithmetic.INFINITY,
                 matrix=numpy.matrix([[1, 0], [0, 1]])):
        """! @brief This is a factory method for generating uncertain inputs that
         have a Gaussian distribution (i.e. bivariate Normal Distribution).
         @param self
         @param val The complex value of the input.
         @param u_r The uncertainty of the real part.
         @param u_i The uncertainty of the imaginary part.
         @param dof The degrees of freedom of the variable.
         @param matrix The matrix of correlation coefficients."""

        ui = CUncertainInput(val, u_r, u_i, dof)
        ui.set_context(self)
        self.set_correlation(ui, ui, matrix)
        return ui

    def constant(self, val):
        """! @brief This is a factory method for generating constans for uncertainty
         evaluations."""
        return self.gaussian(val, 0.0, 0.0, arithmetic.INFINITY,
                             numpy.matrix(numpy.zeros((2, 2))))

    def set_correlation(self, c1, c2, matrix):
        """! @brief This method sets the correlation coefficients of
         two input arguments.
         @param self
         @param c1 The first CUncertainInput
         @param c2 The second CUncertainInput
         @param matrix The matrix of correlation coefficients"""

        if (isinstance(c1, quantities.Quantity) or
                isinstance(c2, quantities.Quantity)):
            c1 = quantities.Quantity.value_of(c1)
            c2 = quantities.Quantity.value_of(c2)

            u1 = c1.get_default_unit()
            u2 = c2.get_default_unit()

            fc1 = c1.get_value(u1)
            fc2 = c2.get_value(u2)

            self.set_correlation(fc1, fc2, matrix)
            return

        matrix = numpy.matrix(matrix)
        Context._check_cmatrix(matrix)
        assert (isinstance(c1, CUncertainInput))
        assert (isinstance(c2, CUncertainInput))
        c1.set_context(self)
        c2.set_context(self)
        self._correlation[(c1, c2)] = matrix
        # ensure symmetry
        self._correlation[(c2, c1)] = matrix

    def get_correlation(self, c1, c2):
        """! @brief Get the correlation of two input arguments.
         @param self
         @param c1 The first CUncertainInput
         @param c2 The second CUncertainInput
         @return The matrix of correlation coefficients."""

        if (isinstance(c1, quantities.Quantity) or
                isinstance(c2, quantities.Quantity)):
            c1 = quantities.Quantity.value_of(c1)
            c2 = quantities.Quantity.value_of(c1)

            u1 = c1.get_default_unit()
            u2 = c2.get_default_unit()

            fc1 = c1.get_value(u1)
            fc2 = c2.get_value(u2)

            return self.get_correlation(fc1, fc2)

        try:
            result = self._correlation[(c1, c2)]
        except KeyError:
            if (c1 is c2):
                return numpy.matrix([[1, 0], [0, 1]])
            else:
                return numpy.zeros((2, 2))
        return result

    def uncertainty(self, c):
        """! @brief Get the combined standard uncertainty of a complex-valued
         component of uncertainty.
         @param self
         @param c The component of uncertainty.
         @return The matrix expressing the combined standard uncertainty.
         @attention If the argument is an instance of Quantitiy having the 
                unit [u] then the uncertainty, expressed as covariance matrix 
                has [u^2]."""

        if (isinstance(c, quantities.Quantity)):
            c1 = quantities.Quantity.value_of(c)
            u1 = c1.get_default_unit()
            fc1 = c1.get_value(u1)
            print(type(fc1))
            print(isinstance(fc1, CUncertainComponent))
            return quantities.Quantity(u1 * u1, self.uncertainty(fc1))

        inputs = c.depends_on()
        sum = numpy.zeros((2, 2))

        for i in inputs:
            for j in inputs:
                sum += c.get_uncertainty(i) * self.get_correlation(i, j) \
                       * (c.get_uncertainty(j)).T

        return sum

    def dof(self, c):
        """! @brief Calculate the effective degrees of freedom of the argument.
         @param self
         @param c The component of uncertainty.
         @return The number of effective degress of freedom.
         @attention The result may me infinite if any of the inputs has
                    an infinite DOF. In this case this method returns
                    <tt>arithmetic.INFINITY</tt>.
         @see arithmetic.INFINITY"""
        if (isinstance(c, quantities.Quantity)):
            c1 = quantities.Quantity.value_of(c)
            u1 = c1.get_default_unit()
            fc1 = c1.get_value(u1)

            return self.dof(fc1)

        inputs = c.depends_on()

        sum_v11 = 0.0;
        sum_v12 = 0.0;
        sum_v22 = 0
        a = 0.0;
        d = 0.0;
        f = 0.0

        for i in inputs:
            # emergency break, if one is infinity, its useless to continue
            dof = i.get_dof()
            if (dof == arithmetic.INFINITY):
                return arithmetic.INFINITY
            # create the cov-matrix v_i
            v_i = numpy.zeros((2, 2))
            for j in inputs:
                v_i += c.get_uncertainty(i) * self.get_correlation(i, j) \
                       * (c.get_uncertainty(j)).T

            v_11 = v_i[0, 0]
            v_12 = v_i[0, 1]
            v_22 = v_i[1, 1]

            sum_v11 += v_11
            sum_v12 += v_12
            sum_v22 += v_22

            a += 2.0 * v_11 ** 2.0 / dof
            d += (v_11 * v_22 + v_12 ** 2.0) / dof
            f += 2.0 * v_22 ** 2.0 / dof

        A = 2.0 * sum_v11 ** 2.0
        D = sum_v11 * sum_v22 + sum_v12 ** 2.0
        F = 2.0 * sum_v22 ** 2.0

        return (A + D + F) / (a + d + f)

## @}
