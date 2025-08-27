## \file ucomponents.py
# \brief This file contains the module to model uncertain values.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#          Thomas Reidemeister</a>

## \namespace scuq::ucomponents
# \brief This namespace contains the classes to evaluate the
#        uncertainty of scalar functions.

## \defgroup ucomponents The Uncertainty Module
#
# This module contains classes to model uncertain values.
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \addtogroup ucomponents 
# @{

# Example for Uncertain Quantities
## This example shows how uncertain values can be used as quantities.
# Instead of encapsulating instances of <tt>quantities.Quantity</tt>
# inside an instance of <tt>ucomponents.UncertainInput</tt>, you should
# always encapsulate uncertain values inside quantities. Otherwise
# this will lead to unpredicable behavior.
# \see quantities The quantities module.
# \see ucomponents The module to evaluate the uncertainty of
#      scalar models.
# \see cucomponents The module to evalute the uncertainty of
#      complex-valued models
# \author Thomas Reidemeister
# \example UncertainQuantity.py

# standard modules
import numpy
# import operator
import numbers

# local modules
import scuq.arithmetic as arithmetic
import scuq.quantities as quantities
import scuq.units as units
import scuq.cucomponents as cucomponents


def coerce(x, y):
    t = type(x + y)
    return (t(x), t(y))


def clearDuplicates(alist):
    """! @brief       Remove identical elements from a list
      @param alist A list that may contain identical elements.
      @return A list that only contains unique elements.
    """
    result = []
    for newItem in alist:
        contained = False
        for oldItem in result:
            if oldItem is newItem:
                contained = True
                break
        if (not contained):
            result += [newItem]
    return result


class UncertainComponent:
    """! @brief       This is the abstract base class to model components of 
       uncertainty as described in by "The GUM Tree".
       @see "The "GUM Tree": A software design pattern for handling
            measurement uncertainty"; B. D. Hall; Industrial Research
            Report 1291; Measurements Standards Laboratory New Zealand (2003).
    """

    def __init__(self):
        """! @brief Default constructor.
              @param self
        """
        raise NotImplementedError

    def arithmetic_check(self):
        """! @brief This method checks this instance for mathematical correctness.
              You should overload this method, if your class is not defined
              for specific argument values. If any (mathematical) invalid
              values have been assigned, your implementation should raise an
              ArithmeticError explaining the problem.
              This method is usually called within the constructor of a class, 
              after the members have been initialized.
              @param self
        """
        # if not overriden, assume all arguements are possible
        return True

    def get_value(self):
        """! @brief Abstract method: The implementation should return
              a numeric value (e.g. float,int,long,or arithmetic.RationalNumber)
              representing the value assigned to the component of uncertainty.
              @param self
              @return A numeric value, representing the value.
        """
        raise NotImplementedError

    def get_uncertainty(self, component):
        """! @brief Abstract method: The implementation should return
              a numeric value (e.g. float,int,long,or arithmetic.RationalNumber)
              representing the standard uncertainty of this component.
              @param self
              @param component Another instance of uncertainty.
                     If the argument is this instance the uncertainty is
                     returned, @f$\frac{0}{1}@f$ should be returned otherwise.
                     This is analogous to taking the derivate 
                     of an independent variable. For further explanation
                     see "The GUM tree".
              @return A numeric value, representing the standard uncertainty.
              @see arithmetic.RationalNumber
              @see "The "GUM Tree": A software design pattern for handling
                    measurement uncertainty"; B. D. Hall; Industrial Research
                    Report 1291; Measurements Standards Laboratory New Zealand (2003).
        """
        raise NotImplementedError

    def depends_on(self):
        """! @brief Abstract method: The implementation should return a list of
              the components of uncertainty, that this component depends on.
              @return A list of the components of uncertainty.
        """
        raise NotImplementedError

    def __getstate__(self):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        raise NotImplementedError

    def __setstate__(self, state):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        raise NotImplementedError

    def value_of(value):
        """! @brief A factory method, that can be used to create instances of
              uncertain components. This method returns instances of
              UncertainNumber depending on the argument.
              @param value An instance of UncertainNumber or a numeric
                     value.
              @return The argument, if it is already an instance of
                      UncertainNumber, or a new instance of UncertainInput
                      (having an uncertainty of 0.0)
                      if the argument is a numeric value (i.e. int,float...).
              @exception TypeError If the argument is a quantity. You cannot 
                      encapsulate quantites in UncertainValues. Plase use
                      Quantity(UncertainValue) instead.
        """

        # do not encapsulate uncertain components
        if (isinstance(value, UncertainComponent)):
            return value

        # do not encapsulate quantities
        if (isinstance(value, quantities.Quantity)):
            raise TypeError("You cannot encapsulate quantities in"
                            + " Uncertain components;"
                            + " Use Quantity(UncertainValue) instead")

        # if a numeric input is given,
        # assume it is an uncertain input
        assert (isinstance(value, (numbers.Number, arithmetic.RationalNumber)))

        return UncertainInput(value, 0.0)

    value_of = staticmethod(value_of)

    def gaussian(value, sigma, dof=arithmetic.INFINITY):
        """! @brief A factory method, that can be used to create instances of
              uncertain components. This method returns uncertain inputs
              that are quantified as a gaussian distribution, centered
              at value, and having the uncertainty sigma.
              @param value A numeric value, representing @f$x@f$.
              @param sigma A numeric value, representing @f$a@f$
              @param dof The assigned number of degrees of freedom.
              @return An uncertain component.
        """
        assert (not isinstance(value, UncertainComponent))
        assert (not isinstance(sigma, UncertainComponent))
        assert (not isinstance(value, quantities.Quantity))
        assert (not isinstance(sigma, quantities.Quantity))
        assert (isinstance(value, numbers.Number))
        assert (isinstance(sigma, numbers.Number))

        return UncertainInput(value, sigma, dof)

    gaussian = staticmethod(gaussian)

    def uniform(value, halfwidth, dof=arithmetic.INFINITY):
        """! @brief A factory method, that can be used to create instances of
              uncertain components. This method returns uncertain inputs
              that are quantified as a uniform distribution, centered
              at x, and having the half-width a.
              @param value A numeric value, representing @f$x@f$.
              @param halfwitdh A numeric value, representing @f$a@f$.
              @param dof The assigned number of degrees of freedom.
              @return An uncertain component, having the uncertainty
                      @f$ u(x) = \frac{a}{\sqrt{3}} @f$.
        """
        assert (not isinstance(value, UncertainComponent))
        assert (not isinstance(halfwidth, UncertainComponent))
        assert (not isinstance(value, quantities.Quantity))
        assert (not isinstance(halfwidth, quantities.Quantity))
        assert (isinstance(value, numbers.Number))
        assert (isinstance(halfwidth, numbers.Number))

        uncertainty = halfwidth / numpy.sqrt(3.0)

        return UncertainInput(value, uncertainty, dof)

    uniform = staticmethod(uniform)

    def triangular(value, halfwidth, dof=arithmetic.INFINITY):
        """! @brief A factory method, that can be used to create instances of
              uncertain components. This method returns uncertain inputs
              that are quantified as a triangular distribution, centered
              at x, and having the half-width a.
              @param value A numeric value, representing @f$x@f$.
              @param halfwitdh A numeric value, representing @f$a@f$
              @param dof The assigned number of degrees of freedom.
              @return An uncertain component, having the uncertainty
                      @f$ u(x) = \frac{a}{\sqrt{6}} @f$.
        """
        assert (not isinstance(value, UncertainComponent))
        assert (not isinstance(halfwidth, UncertainComponent))
        assert (not isinstance(value, quantities.Quantity))
        assert (not isinstance(halfwidth, quantities.Quantity))
        assert (isinstance(value, numbers.Number))
        assert (isinstance(halfwidth, numbers.Number))

        uncertainty = halfwidth / numpy.sqrt(6.0)

        return UncertainInput(value, uncertainty, dof)

    triangular = staticmethod(triangular)

    def beta(value, p, q, dof=arithmetic.INFINITY):
        """! @brief A factory method, that can be used to create instances of
              uncertain components. This method returns uncertain inputs
              that are quantified as a beta distribution, having the
              parameters @f$ p @f$ and @f$ q @f$.
              @param value The assigned value.
              @param p A numeric value, representing @f$p@f$.
              @param q A numeric value, representing @f$q@f$
              @param dof The assigned number of degrees of freedom.
              @return An uncertain component.
        """
        assert (not isinstance(p, UncertainComponent))
        assert (not isinstance(value, UncertainComponent))
        assert (not isinstance(q, UncertainComponent))
        assert (not isinstance(p, quantities.Quantity))
        assert (not isinstance(value, quantities.Quantity))
        assert (not isinstance(q, quantities.Quantity))
        assert (isinstance(p, numbers.Number))
        assert (isinstance(value, numbers.Number))
        assert (isinstance(q, numbers.Number))

        uncertainty = numpy.sqrt(p * q / ((p + q) ** 2.0 * (p + q + 1.0)))

        return UncertainInput(value, uncertainty, dof)

    beta = staticmethod(beta)

    def arcsine(value, dof=arithmetic.INFINITY):
        """! @brief A factory method, that can be used to create instances of
              uncertain components. This method returns uncertain inputs
              that are quantified as an arcsin distribution.
              @return An uncertain component.
        """
        assert (not isinstance(value, UncertainComponent))
        assert (not isinstance(value, quantities.Quantity))
        assert (isinstance(value, numbers.Number))

        return UncertainComponent.beta(value, 0.5, 0.5, dof)

    arcsine = staticmethod(arcsine)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has equal attributes as
                      the argument
        """
        raise NotImplementedError

    ### Emulation of numeric behaviour

    def __eq__(self, other):
        """! @brief This method is an alias for (self is other). It checks
              if the argument is identical with the current instance.
              @note This behavior is enforced to handle special cases.
                    Imagine you want to compare 
                    @f$ sin(a \pm u_a) \times (a \pm u_a) @f$
                    with @f$ sin(a \pm u_a) \times (b \pm u_b)@f$ with 
                    @f$ a = b;u_a = u_b @f$.
                    Since in the first case the values are identical, they
                    are dependent. In the second case the values are the same,
                    but we do not know about their independence. Therefore the
                    second case needs a different handling. In order not to
                    confuse these two cases, this method has to check
                    for identity.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the argument is identical to the current instance.
        """
        return self is other

    def __ne__(self, other):
        """! @brief This method is an alias for not(self is other). It checks
              if the argument is not identical with the current instance.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the argument is not identical to the current instance.
              @see UncertainComponent.__eq__
        """
        return not (self is other)

    def __cmp__(self, other):
        def cmp(a, b):
            return (a > b) - (a < b)

        sval = self.get_value()
        try:
            oval = other.get_value()
        except AttributeError:
            oval = other
        return cmp(sval, oval)

    def __lt__(self, other):
        sval = self.get_value()
        try:
            oval = other.get_value()
        except AttributeError:
            oval = other
        return sval < oval

    def __le__(self, other):
        sval = self.get_value()
        try:
            oval = other.get_value()
        except AttributeError:
            oval = other
        return sval <= oval

    def __gt__(self, other):
        sval = self.get_value()
        try:
            oval = other.get_value()
        except AttributeError:
            oval = other
        return sval > oval

    def __ge__(self, other):
        sval = self.get_value()
        try:
            oval = other.get_value()
        except AttributeError:
            oval = other
        return sval >= oval

    def __add__(self, other):
        """! @brief This method adds the argument to this instance.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Add(self, other)

    def arctan2(self, other):
        """! @brief This method provides an interface for
        numpy.arctan2.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        if (not isinstance(other, UncertainComponent)):
            tmp, other = coerce(self, other)
            return numpy.arctan2(tmp, other)
        return ArcTan2(self, other)

    def hypot(self, other):
        """! @brief This method provides an interface for
        numpy.hypot.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        if (not isinstance(other, UncertainComponent)):
            tmp, other = coerce(self, other)
            return numpy.hypot(tmp, other)
        return numpy.sqrt(self * self + other * other)

    def __sub__(self, other):
        """! @brief This method substracts the argument from this instance.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Sub(self, other)

    def __mul__(self, other):
        """! @brief This method multiplies the argument by this instance.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Mul(self, other)

    def __truediv__(self, other):
        """! @brief This method divides this instance by the argument.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Div(self, other)

    def __pow__(self, other):
        """! @brief This method raises this to the power of the argument.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Pow(self, other)

    def __radd__(self, other):
        """! @brief This method adds this instance to the argument.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Add(other, self)

    def __rsub__(self, other):
        """! @brief This method substracts this instance from the argument.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Sub(other, self)

    def __rmul__(self, other):
        """! @brief This method multiplies the argument by this instance.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Mul(other, self)

    def __rtruediv__(self, other):
        """! @brief              This method divides the argument by this instance.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Div(other, self)

    def __rpow__(self, other):
        """! @brief              This method raises the argument to the power of this instance.
              @note If the argument is not an instance of UncertainComponent
                    it will be converted using UncertainComponent.value_of.
              @param self
              @param other A numeric value.
              @see UncertainComponent.value_of
        """
        assert (isinstance(other, (UncertainComponent, numbers.Number, arithmetic.RationalNumber)))
        return Pow(other, self)

    def __neg__(self):
        """! @brief This method negates this instance.
              @param self
        """
        return Neg(self)

    def __invert__(self):
        """! @brief Inverts this instance.
              @param self
        """
        return 1.0 / self

    def __abs__(self):
        """! @brief This method returs the absolute value of this instance.
              @param self
        """
        return Abs(self)

    def set_context(self, context):
        """! @brief Assign a context to this component.
               This method is only used in combination with __str__.
               If a context is assigned to the instance, the correlation
               coefficients will be considered for __str__. Otherwise __str__
               assumes that there is no correlation among the inputs.
              @param context An instance of Context.
              @param self
              @see __str__
              @see Context
        """
        self._context = context

    def eval(self):
        """! @brief Factory method to get get an object with evaluated uncertainties.
              @param self
              @return object with <value> and <uncertainty>
              @see set_context
        """
        context = None
        try:
            context = self._context
        except AttributeError:
            context = Context()

        assert (isinstance(context, Context))

        uncert = context.uncertainty(self)
        value = self.get_value()
        return UncertainInput(value, uncert)

    def __str__(self):
        """! @brief This method returs the absolute value of this instance.
              @param self
              @return A string of the form "<value> +- <uncertainty>" or
                    "<value> +- <uncertainty> [NC]", if no context was provided.
              @see set_context
        """
        bnc = False
        context = None
        try:
            context = self._context
        except AttributeError:
            context = Context()
            bnc = len(self.depends_on()) > 1

        assert (isinstance(context, Context))

        uncert = context.uncertainty(self)
        value = self.get_value()

        if (bnc):
            return str(value) + " +/- " + str(uncert) + " [NC]"
        else:
            return str(value) + " +/- " + str(uncert)

    ### Numpy compliance

    def arccos(self):
        """! @brief This method provides the broadcast interface for
              numpy.arccos.
              @param self
              @return The inverse Cosine of this component.
        """
        return ArcCos(self)

    def arccosh(self):
        """! @brief This method provides the broadcast interface for
              numpy.arccosh.
              @param self
              @return The inverse hyperbolic Cosine of this component.
        """
        return ArcCosh(self)

    def arcsin(self):
        """! @brief This method provides the broadcast interface for
              numpy.arcsin.
              @param self
              @return The inverse Sine of this component.
        """
        return ArcSin(self)

    def arcsinh(self):
        """! @brief This method provides the broadcast interface for
              numpy.arcsinh.
              @param self
              @return The inverse hyperbolic Sine of this component.
        """
        return ArcSinh(self)

    def arctan(self):
        """! @brief This method provides the broadcast interface for
              numpy.arctan.
              @param self
              @return The inverse Tangent of this component.
        """
        return ArcTan(self)

    def arctanh(self):
        """! @brief This method provides the broadcast interface for
              numpy.arctanh.
              @param self
              @return The inverse hyperbolic Tangent of this component.
        """
        return ArcTanh(self)

    def cos(self):
        """! @brief This method provides the broadcast interface for
              numpy.cos.
              @param self
              @return The Cosine of this component.
        """
        return Cos(self)

    def cosh(self):
        """! @brief This method provides the broadcast interface for
              numpy.cosh.
              @param self
              @return The hyperbolic Cosine of this component.
        """
        return Cosh(self)

    def tan(self):
        """! @brief This method provides the broadcast interface for
              numpy.tan.
              @param self
              @return The Tangent of this component.
        """
        return Tan(self)

    def tanh(self):
        """! @brief This method provides the broadcast interface for
              numpy.tanh.
              @param self
              @return The hyperbolic Tangent of this component.
        """
        return Tanh(self)

    def log10(self):
        """! @brief This method provides the broadcast interface for
              numpy.log10.
              @param self
              @return The decadic Logarithm of this component.
        """
        return Log(self) / Log(10.0)

    def log2(self):
        """! @brief This method provides the broadcast interface for
              numpy.log2.
              @param self
              @return The decadic Logarithm of this component.
        """
        return Log(self) / Log(2.0)

    def sin(self):
        """! @brief This method provides the broadcast interface for
              numpy.sin.
              @param self
              @return The Sine of this component.
        """
        return Sin(self)

    def sinh(self):
        """! @brief This method provides the broadcast interface for
              numpy.sinh.
              @param self
              @return The hyperbolic Sine of this component.
        """
        return Sinh(self)

    def sqrt(self):
        """! @brief This method provides the broadcast interface for
              numpy.sqrt.
              @param self
              @return The Square Root of this component.
        """
        return Sqrt(self)

    def square(self):
        """! @brief This method provides the broadcast interface for
              numpy.sqrt.
              @param self
              @return The Square Root of this component.
        """
        return self * self

    def fabs(self):
        """! @brief This method provides the broadcast interface for
              numpy.fabs.
              @param self
              @return The absolute value of this component.
        """
        return Abs(self)

    def absolute(self):
        """! @brief This method provides the broadcast interface for
              numpy.absolute.
              @param self
              @return The absolute value of this component.
        """
        return Abs(self)

    def exp(self):
        """! @brief This method provides the broadcast interface for
              numpy.exp.
              @param self
              @return The Exponential of this component.
        """
        return Exp(self)

    def log(self):
        """! @brief This method provides the broadcast interface for
              numpy.log.
              @param self
              @return The Natural Logarithm of this component.
        """
        return Log(self)

    def __coerce__(self, other):
        """! @brief Implementation of coercion rules.
        \see Coercion - The page describing the coercion rules."""
        if (isinstance(other, UncertainComponent)):
            return (self, other)
        elif (isinstance(other, quantities.Quantity)):
            new_self = quantities.Quantity.value_of(self)
            return (new_self, other)
        elif (isinstance(other, cucomponents.CUncertainComponent)):
            raise NotImplementedError("You must not mix scalar and"
                                      + " complex-valued uncertain values")
        elif (isinstance(other, arithmetic.RationalNumber)
              or isinstance(other, int)
              or isinstance(other, int)
              or isinstance(other, float)):
            other = UncertainComponent.value_of(other)
            return (self, other)
        elif (isinstance(other, complex)):
            raise NotImplementedError("Please use the module cucomponents"
                                      + " to evaluate the uncertainty of complex"
                                      + "-valued quantities")
        elif (isinstance(other, units.Unit)):
            raise NotImplementedError("You cannot declare a unit as uncertain." +
                                      " Please use the quantities module" +
                                      " for that!")
        else:
            raise NotImplementedError()


class UncertainInput(UncertainComponent):
    """! @brief       This class provides the model for uncertain inputs, that
       are referred to as "Leafs" in "The GUM tree".
       @see "The "GUM Tree": A software design pattern for handling
            measurement uncertainty"; B. D. Hall; Industrial Research
            Report 1291; Measurements Standards Laboratory New Zealand (2003).
    """
    _value = 0.0
    _uncertainty = 0.0
    _dof = 0.0

    def __init__(self, value, uncertainty, dof=arithmetic.INFINITY):
        """! @brief Default constructor.
              @note The parameters of the input must not be instances of
                    UncertainComponent nor quantities.Quantity.
                    Create quantities, having an UncertainInput as
                    numeric argument instead.
              @param self
              @param value The numeric value of the input. 
              @param dof The assigned component of degrees of freedom.
              @param uncertainty The standard uncertainty of the input.
              @see UncertainQuantity.py
        """
        assert (not isinstance(value, UncertainComponent))
        assert (not isinstance(value, quantities.Quantity))
        assert (not isinstance(uncertainty, UncertainComponent))
        assert (not isinstance(uncertainty, quantities.Quantity))
        assert (not isinstance(dof, UncertainComponent))
        assert (not isinstance(dof, quantities.Quantity))

        assert (isinstance(value, (numbers.Number, arithmetic.RationalNumber)))
        assert (isinstance(uncertainty, (numbers.Number, arithmetic.RationalNumber)))
        assert (isinstance(dof, numbers.Number) or dof == arithmetic.INFINITY)

        self._value = value
        self._uncertainty = uncertainty
        self._dof = dof

    def get_value(self):
        """! @brief Returns the assigned value.
              @param self
              @return A numeric value, representing the value.
        """
        return self._value

    def get_dof(self):
        """! @brief Returns the assigned degrees of freedom.
              @param self
              @return A numeric value or arithmetic.INFINITY, representing the value.
        """
        return self._dof

    def conjugate(self):
        return self._value

    def get_uncertainty(self, component):
        """! @brief Returns the assigned uncertainty.
              @param self
              @param component Another component of uncertainty.
              @return A numeric value, representing the standard uncertainty.
              @see UncertainComponent.get_uncertainty
        """
        if (self is component):
            return self._uncertainty
        return 0.0

    def depends_on(self):
        """! @brief Returns a list containing this element.
              @return A list of the components of uncertainty.
        """
        return [self]

    def __ceil__(self):
        return numpy.ceil(self._value + self._uncertainty)

    def __floor__(self):
        return numpy.ceil(self._value - self._uncertainty)

    def __getstate__(self):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return (self._value, self._uncertainty, self._dof)

    def __setstate__(self, state):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._value, self._uncertainty, self._dof = state

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, UncertainInput)):
            return False
        return self._value == other._value and \
               self._uncertainty == other._uncertainty and \
               self._dof == other._dof

    def __hash__(self):
        """! @brief Hash this instance.
        """
        return 1


class BinaryOperation(UncertainComponent):
    """! @brief       The abstract base class for modelling binary operations.
       This class provides the abstract interface for GUM-tree-nodes
       that have two silblings.
    """

    ## The right silbling of the operation.
    _right = None

    ## The left silbling of the operation.
    _left = None

    def __init__(self, left, right):
        """! @brief Default constructor.
              @attention If you extend this class call this 
                         constructor explicitly in order to
                         initialize the silblings!
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        assert (left != None)
        assert (right != None)

        self._right = UncertainComponent.value_of(right)
        self._left = UncertainComponent.value_of(left)

    def depends_on(self):
        """! @brief Get the components of uncertainty, that this class depends on.
              @return A list of the components of uncertainty.
        """
        list = self._left.depends_on()
        list += self._right.depends_on()
        return clearDuplicates(list)

    def get_right(self):
        """! @brief Return the right silbling.
              @return The right silbling.
        """
        return self._right

    def get_left(self):
        """! @brief Return the left silbling.
              @return The left silbling.
        """
        return self._left

    def __getstate__(self):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return (self._left, self._right)

    def __setstate__(self, state):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._left, self._right = state

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, BinaryOperation)):
            return False
        return self._right.equal_debug(other._right) and \
               self._left.equal_debug(other._left)


class UnaryOperation(UncertainComponent):
    """! @brief       The abstract base class for modelling unary operations.
       This class provides the abstract interface for GUM-tree-nodes
       that have one silbling.
    """
    ## The silbling of the operation.
    _right = None

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right The silbling of this instance.
        """
        assert (right != None)
        self._right = UncertainComponent.value_of(right)

    def depends_on(self):
        """! @brief Abstract method: The implementation should return a list of
              the components of uncertainty, that this component depends on.
              @return A list of the components of uncertainty.
        """
        return clearDuplicates(self._right.depends_on())

    def get_silbling(self):
        """! @brief Return the silbling.
              @return The silbling.
        """
        return self._right

    def __getstate__(self):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return self._right

    def __setstate__(self, state):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._right = state

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, UnaryOperation)):
            return False
        return self._right.equal_debug(other._right)


class Add(BinaryOperation):
    """! @brief       This class models GUM-tree nodes that add two silblings.
    """

    def __init__(self, left, right):
        """! @brief Default constructor.
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        BinaryOperation.__init__(self, left, right)

    def get_value(self):
        """! @brief Returns the sum of the silblings assigned.
              @param self
              @return A numeric value, representing the sum of the silblings.
        """
        return self.get_left().get_value() + self.get_right().get_value()

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = x_1 + x_2 @f$ then
              the resulting uncertainty is @f$ u(y) = u(x_1) + u(x_2) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        return self.get_left().get_uncertainty(component) + \
               self.get_right().get_uncertainty(component)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Add)):
            return False
        return BinaryOperation.equal_debug(self, other)


class ArcTan2(BinaryOperation):
    """! @brief This class models the inverse two-argument tangent.
    """

    def __init__(self, left, right):
        """! @brief Default constructor.
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        BinaryOperation.__init__(self, left, right)

    def get_value(self):
        """! @brief Returns the sum of the silblings assigned.
              @param self
              @return A numeric value, representing the 
              inverse two-argument tangent of the inputs.
        """
        return numpy.arctan2(self.get_left().get_value(),
                             self.get_right().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = x_1 + x_2 @f$ then
              the resulting uncertainty is @f$ u(y) = u(x_1) + u(x_2) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        lhs = self.get_left().get_uncertainty(component)
        rhs = self.get_right().get_uncertainty(component)
        lhs_val = self.get_left().get_value()
        rhs_val = self.get_right().get_value()
        return -rhs_val / (lhs_val ** 2 + rhs_val ** 2) * lhs + \
               lhs_val / (lhs_val ** 2 + rhs_val ** 2) * rhs

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcTan2)):
            return False
        return BinaryOperation.equal_debug(self, other)


class Mul(BinaryOperation):
    """! @brief       This class models GUM-tree nodes that multiply two silblings.
    """

    def __init__(self, left, right):
        """! @brief Default constructor.
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        BinaryOperation.__init__(self, left, right)

    def get_value(self):
        """! @brief Returns the product of the silblings assigned.
              @param self
              @return A numeric value, representing the product of the silblings.
        """
        return self.get_left().get_value() * self.get_right().get_value()

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = x_1 \times x_2 @f$ then
              the resulting uncertainty is 
              @f$ u(y) = x_2 \times u(x_1) + x_1 \times u(x_2) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        return self.get_right().get_value() * \
               self.get_left().get_uncertainty(component) + \
               self.get_left().get_value() * \
               self.get_right().get_uncertainty(component)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Mul)):
            return False
        return BinaryOperation.equal_debug(self, other)


class Div(BinaryOperation):
    """! @brief       This class models GUM-tree nodes that divide two silblings.
    """

    def __init__(self, left, right):
        """! @brief Default constructor.
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        BinaryOperation.__init__(self, left, right)
        self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for divide by zero.
              @param self
              @exception ArithmeticError If the right silbling returns 0.0
                     as value.
        """
        if (self.get_right().get_value() == 0.0):
            raise ArithmeticError("Divide by Zero")

    def get_value(self):
        """! @brief Returns the fraction of the silblings assigned.
              @param self
              @return A numeric value, representing the fraction of the silblings.
        """
        return self.get_left().get_value() / self.get_right().get_value()

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = \frac{x_1}{x_2} @f$ then
              the resulting uncertainty is 
              @f$ u(y) = \frac{u(x_1)}{x_2} - \frac{x_1 \times u(x_2)}{x_2^2} @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x_1 = self.get_left().get_uncertainty(component)
        u_x_2 = self.get_right().get_uncertainty(component)
        x_1 = self.get_left().get_value()
        x_2 = self.get_right().get_value()

        return u_x_1 / x_2 - u_x_2 * x_1 / (x_2 * x_2)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Div)):
            return False
        return BinaryOperation.equal_debug(self, other)


class Sub(BinaryOperation):
    """! @brief       This class models GUM-tree nodes that take the difference of 
      the two silblings.
    """

    def __init__(self, left, right):
        """! @brief Default constructor.
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        BinaryOperation.__init__(self, left, right)

    def get_value(self):
        """! @brief Returns the difference of the silblings assigned.
              @param self
              @return A numeric value, representing the difference of the silblings.
        """
        return self.get_left().get_value() - self.get_right().get_value()

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = x_1 - x_2 @f$ then
              the resulting uncertainty is @f$ u(y) = u(x_1) - u(x_2) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x_1 = self.get_left().get_uncertainty(component)
        u_x_2 = self.get_right().get_uncertainty(component)

        return u_x_1 - u_x_2

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Sub)):
            return False
        return BinaryOperation.equal_debug(self, other)


class Pow(BinaryOperation):
    """! @brief       This class models GUM-tree nodes that raise the left silbling 
      to the power of the right one.
    """

    def __init__(self, left, right):
        """! @brief Default constructor.
              @param self
              @param left Left silbling of this instance.
              @param right Right silbling of this instance.
        """
        BinaryOperation.__init__(self, left, right)

    def get_value(self):
        """! @brief Returns the power @f$ pow(left,right) @f$ 
               of the silblings assigned.
              @param self
              @return A numeric value, representing the power of the silblings.
        """
        return self.get_left().get_value() ** self.get_right().get_value()

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = x_1^{x_2} @f$ then
              the resulting uncertainty is @f$ u(y) = x_2 \times x_1^{x_2-1} 
              \times u(x_1) + x_1^{x_2} \times ln(x_1) \times u(x_2) @f$.
              @attention The uncertainty is only defined, if @f$x_1>0@f$ and
                         @f$x_2>0@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
              @exception ArithmeticError If @f$x_1 \leq 0@f$ or @f$x_2 \leq 0@f$.
        """
        u_x_1 = self.get_left().get_uncertainty(component)
        u_x_2 = self.get_right().get_uncertainty(component)
        x_1 = self.get_left().get_value()
        x_2 = self.get_right().get_value()
        # if( x_1 <= 0.0 or x_2 <= 0.0 ):
        #    import sys
        #    print >> sys.stderr, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #    print >> sys.stderr, type(x_1), x_1, type(x_2), x_2
        #    raise ArithmeticError( "Illegal range exception:"+
        #                          " The uncertainty is not"+
        #                          "defined for the arguments" )
        try:
            # print repr(u_x_2)
            if abs(u_x_2) <= 1e-12:
                u = x_2 * numpy.power(x_1, (x_2 - 1.0)) * u_x_1
            else:
                u = x_2 * numpy.power(x_1, (x_2 - 1.0)) * u_x_1 + \
                    numpy.power(x_1, x_2) * u_x_2 * numpy.log(x_1)
            return u
        except:
            import sys
            print(type(x_1), x_1, type(x_2), x_2, file=sys.stderr)
            return 0.0

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Pow)):
            return False
        return BinaryOperation.equal_debug(self, other)


class Cos(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Cosine of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the Cosine of the silbling.
              @param self
              @return A numeric value, representing the Cosine of the silblings.
        """
        return numpy.cos(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = cos(x) @f$ then
              the resulting uncertainty is @f$ u(y) = -sin(x) \times u(x) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return -numpy.sin(x) * u_x

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Cos)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Sin(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Sine of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the Sine of the silbling.
              @param self
              @return A numeric value, representing the Sine of the silblings.
        """
        return numpy.sin(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = sin(x) @f$ then
              the resulting uncertainty is @f$ u(y) = cos(x) \times u(x) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return numpy.cos(x) * u_x

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Sin)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Tan(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Tangent of a
      silbling.
      @attention Because of floating point rounding issues, instances of
                 this class may return invalid values instead of raising an
                 OverflowError for values close to @f$n\times\frac{\pi}{2}@f$.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        self.arithmetic_check()

    def get_value(self):
        """! @brief Returns the Tangent of the silbling.
              @param self
              @return A numeric value, representing the Tangent of the silblings.
        """
        return numpy.tan(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = tan(x) @f$ then
              the resulting uncertainty is @f$ u(y) = \frac{u(x)}{cos^2(x)}@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x / (numpy.cos(x) * numpy.cos(x))

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Tan)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Sqrt(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the square root of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        # self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for undefined arguments.
              @note The square root is only defined for positive values.
              @param self
              @exception ArithmeticError If @f$x \leq 0@f$.
        """
        if (self.get_silbling().get_value() < 0.0):
            raise ArithmeticError("The argument must be positive")

    def get_value(self):
        """! @brief Returns the square root of the silbling.
              @param self
              @return A numeric value, representing the square root of the silblings.
        """
        return numpy.sqrt(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = \sqrt{x} @f$ then
              the resulting uncertainty is @f$ u(y) = \frac{1}{2\sqrt{x}}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
              @exception ZeroDivisionError If the square root is zero.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return 0.5 / numpy.sqrt(x) * u_x

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Sqrt)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Log(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Natural Logarithm of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for undefined arguments.
              @note The natural logarithm is not defined for values @f$x \leq 0@f$.
              @param self
              @exception ArithmeticError If @f$x \leq 0@f$.
        """
        if (self.get_silbling().get_value() < 0.0):
            raise ArithmeticError("The argument must be positive")

    def get_value(self):
        """! @brief Returns the Natural Logarithm of the silbling.
              @param self
              @return A numeric value, representing the Natural Logarithm of the 
                      silblings.
        """
        return numpy.log(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = ln(x) @f$ then
              the resulting uncertainty is @f$ u(y) = \frac{1}{x}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()
        if (not isinstance(x, float)):
            return arithmetic.RationalNumber(1) / x * u_x
        return u_x / x

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Log)):
            return False
        return UnaryOperation.equal_debug(self, other)


class ArcSin(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Arc Sine of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for undefined arguments.
              @note The Arc Sine is only defined within @f$[-1,1]@f$.
              @param self
              @exception ArithmeticError If @f$x \notin [-1,1]@f$.
        """
        value = self.get_silbling().get_value()
        if (value < -1.0 or value > 1.0):
            raise ArithmeticError("The argument must be within [-1,1]")

    def get_value(self):
        """! @brief Returns the Arc Sine of the silbling.
              @param self
              @return A numeric value, representing the Arc Sine of the silblings.
        """
        return numpy.arcsin(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = arcsin(x) @f$ then
              the resulting uncertainty is @f$ u(y) = \frac{1}{\sqrt{1-x^2}}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
              @exception ArithmeticError If @f$x^2 = 1@f$.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x / numpy.sqrt(1.0 - x * x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcSin)):
            return False
        return UnaryOperation.equal_debug(self, other)


class ArcSinh(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the inverse
      Hyperbolic Sine of a silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the inverse Hyperbolic Sine of a silbling.
              @param self
              @return A numeric value, representing the inverse 
                      Hyperbolic Sine of a silbling.
        """
        return numpy.arcsinh(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = arcsinh(x) @f$ then
              the resulting uncertainty is 
              @f$ u(y) = \frac{1}{\sqrt{1+x^2}}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x / numpy.sqrt(1.0 + x * x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcSinh)):
            return False
        return UnaryOperation.equal_debug(self, other)


class ArcCos(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Arcus Cosine of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for undefined arguments.
              @note The Arc Cosine is only defined within @f$[-1,1]@f$.
              @param self
              @exception ArithmeticError If @f$x \notin [-1,1]@f$.
        """
        value = self.get_silbling().get_value()
        if (value < -1.0 or value > 1.0):
            raise ArithmeticError("The argument must be within [-1,1]")

    def get_value(self):
        """! @brief Returns the Arc Cosine of the silbling.
              @param self
              @return A numeric value, representing the Arc Cosine of the silblings.
        """
        return numpy.arccos(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = arccos(x) @f$ then
              the resulting uncertainty is @f$ u(y) = -\frac{1}{\sqrt{1-x^2}}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
              @exception ArithmeticError If @f$x^2 = 1@f$.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return -u_x / numpy.sqrt(1.0 - x * x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcCos)):
            return False
        return UnaryOperation.equal_debug(self, other)


class ArcCosh(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the inverse
      Hyperbolic Cosine.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for undefined arguments.
              @note The inverse Hyperbolic Cosine is only defined 
                    within @f$(1,\infty]@f$.
              @param self
              @exception ArithmeticError If @f$x \notin (1,\infty]@f$.
        """
        value = self.get_silbling().get_value()
        if (value <= 1.0):
            raise ArithmeticError("The argument must be within (1,inf]")

    def get_value(self):
        """! @brief Returns the Arc Cosine of the silbling.
              @param self
              @return A numeric value, representing the Arc Cosine of the silblings.
        """
        return numpy.arccosh(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = arccosh(x) @f$ then
              the resulting uncertainty is 
              @f$ u(y) = \frac{1}{\sqrt{x-1}\sqrt{x+1}}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x / (numpy.sqrt(x - 1.0) * numpy.sqrt(x + 1.0))

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcCosh)):
            return False
        return UnaryOperation.equal_debug(self, other)


class ArcTan(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Arcus Tangent of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the Arc Tangent of the silbling.
              @param self
              @return A numeric value, representing the Arc Tangent of the silblings.
        """
        return numpy.arctan(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = arcsin(x) @f$ then
              the resulting uncertainty is @f$ u(y) = -\frac{1}{1+x^2}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x / (1.0 + x * x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcTan)):
            return False
        return UnaryOperation.equal_debug(self, other)


class ArcTanh(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the inverse
      Hyperbolic Tangent of a silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)
        self.arithmetic_check()

    def arithmetic_check(self):
        """! @brief Checks for undefined arguments.
              @note The inverse Hyperbolic Tangent is only defined 
                    within @f$(-1,1)@f$.
              @param self
              @exception ArithmeticError If @f$x \notin (-1,1)@f$.
        """
        value = self.get_silbling().get_value()
        if (value <= -1.0 or value >= 1.0):
            raise ArithmeticError("The argument must be within (-1,1)")

    def get_value(self):
        """! @brief Returns the Arc Tangent of the silbling.
              @param self
              @return A numeric value, representing the inverse
                      hyperbolic Tangent of the silblings.
        """
        return numpy.arctanh(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = arctanh(x) @f$ then
              the resulting uncertainty is @f$ u(y) = \frac{1}{1-x^2}u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x / (1.0 - x * x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, ArcTanh)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Cosh(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Hyperbolic Cosine of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the Hyperbolic Cosine of the silbling.
              @param self
              @return A numeric value, representing the Hyperbolic Cosine of the 
                      silblings.
        """
        return numpy.cosh(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = cosh(x) @f$ then
              the resulting uncertainty is @f$ u(y) = sinh(x) u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x * numpy.sinh(x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Cosh)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Sinh(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Hyperbolic Sine of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the Hyperbolic Sine of the silbling.
              @param self
              @return A numeric value, representing the Hyperbolic Sine of the 
                      silbling.
        """
        return numpy.sinh(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = sinh(x) @f$ then
              the resulting uncertainty is @f$ u(y) = cosh(x)u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x * numpy.cosh(x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Sinh)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Tanh(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the Hyperbolic Tangent of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the Hyperbolic Tangent of the silbling.
              @param self
              @return A numeric value, representing the Hyperbolic Sine of the 
                      silbling.
        """
        return numpy.tanh(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = tanh(x) @f$ then
              the resulting uncertainty is @f$ u(y) = (1 - tanh^{2}(x)) u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x * (1.0 - numpy.tanh(x) * numpy.tanh(x))

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Tanh)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Exp(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the exponential of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the exponential of the silbling.
              @param self
              @return A numeric value, representing the exponential of the silbling.
        """
        return numpy.exp(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = e^x @f$ then
              the resulting uncertainty is @f$ u(y) = x \times e^x \times u(x)@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)
        x = self.get_silbling().get_value()

        return u_x * numpy.exp(x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Exp)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Abs(UnaryOperation):
    """! @brief       This class models the GUM-tree-nodes that take the absolute value of a
      silbling.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the exponential of the silbling.
              @param self
              @return A numeric value, representing the absolute value of the 
                      silbling.
        """
        return numpy.absolute(self.get_silbling().get_value())

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = |x| @f$ then
              the resulting uncertainty is @f$ u(y) = |u(x)|@f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)

        return numpy.absolute(u_x)

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Abs)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Neg(UnaryOperation):
    """! @brief       This class models the unary negation as GUM-tree-element.
    """

    def __init__(self, right):
        """! @brief Default constructor.
              @param self
              @param right Right silbling of this instance.
        """
        UnaryOperation.__init__(self, right)

    def get_value(self):
        """! @brief Returns the exponential of the silbling.
              @param self
              @return A numeric value, representing the negative value of the 
                      silbling.
        """
        return - self.get_silbling().get_value()

    def get_uncertainty(self, component):
        """! @brief Returns the uncertainty of this node.
              Let the node represent the operation @f$y = -x @f$ then
              the resulting uncertainty is @f$ u(y) = - u(x) @f$.
              @param self
              @param component Another instance of uncertainty.
              @return A numeric value, representing the standard uncertainty.
        """
        u_x = self.get_silbling().get_uncertainty(component)

        return - u_x

    def equal_debug(self, other):
        """! @brief A method that is only used for serialization checking.
              @param self
              @param other Another instance of UncertainComponent
              @return True, if the instance has the same attribute values as
                      the argument
        """
        other = UncertainComponent.value_of(other)
        if (not isinstance(other, Neg)):
            return False
        return UnaryOperation.equal_debug(self, other)


class Context:
    """! @brief       This class provides the context for an uncertainty evaluation.
      It maintains the correlation between the inputs and can be used
      to evaluate the combined standard uncertainty, as shown below.
      Let your model be @f$y = f(x_1,x_2,\ldots,x_N)@f$, then
      @f$ u_c^2(y) = \sum_{i=1}^{N} 
                     \left(\frac{\delta f}{\delta x_i} \right)^2 u^2(x_i) 
                     + 2 \sum_{i=1}^{N}\sum_{j=i+1}^{N} 
                     \frac{\delta f}{\delta x_i}\frac{\delta f}{\delta x_j} 
                     u(x_i,x_j)@f$.
    """

    def __init__(self):
        """! @brief This method initializes the correlation matrix of this context.
              @note You may use the same uncertain components in different
                    contexts. Thus, you could maintain various correlation
                    models.
              @param self
        """
        self._correlationMatrix = {}

    def set_correlation(self, firstItem, secondItem, corr):
        """! @brief This method sets the correlation coefficient @f$ r(x_1,x_2) @f$
               of two inputs. Where 
               @f$ r(x_1,x_2) = \frac{u(x_1,x_2)}{u(x_1)u(x_2)} @f$.
               @note This libary assumes symmetry of correlation (i.e. 
                     @f$ r(x_1,x_2) = r(x_2,x_1)@f$).
               @attention If the arguments are identical, this method has no effect.
              @param self
              @param firstItem Is @f$ x_1 @f$ as denoted above.
              @param secondItem Is @f$ x_2 @f$ as denoted above.
              @param corr The correlation as described by @f$ r(x_1,x_2) @f$.
        """
        # masquerade quantities
        if (isinstance(firstItem, quantities.Quantity) or
                isinstance(secondItem, quantities.Quantity)):
            firstItem = quantities.Quantity.value_of(firstItem)
            secondItem = quantities.Quantity.value_of(secondItem)

            firstUnit = firstItem.get_default_unit()
            secondUnit = secondItem.get_default_unit()

            firstComp = firstItem.get_value(firstUnit)
            secondComp = secondItem.get_value(secondUnit)
            self.set_correlation(firstComp, secondComp, corr)
            return

        assert (isinstance(firstItem, UncertainInput))
        assert (isinstance(secondItem, UncertainInput))

        # autocorrelation automatically implied
        if (firstItem == secondItem):
            return

        # Update the covariance (lookup-table)
        self._correlationMatrix[(firstItem, secondItem)] = corr
        # ensure symmetry
        self._correlationMatrix[(secondItem, firstItem)] = corr

    def get_correlation(self, firstItem, secondItem):
        """! @brief This method returns the correlation coefficient @f$ r(x_1,x_2) @f$
               of two inputs. Where 
               @f$ r(x_1,x_2) = \frac{u(x_1,x_2)}{u(x_1)u(x_2)} @f$.
               If no correlation has been defined before, this method returns
               <tt>0.0</tt>, except for @f$x_1 = x_2@f$. In the last case this
               method returns <tt>1.0</tt>.
               @note This libary assumes symmetry of correlation (i.e. 
                     @f$ r(x_1,x_2) = r(x_2,x_1)@f$).
              @param self
              @param firstItem Is @f$ x_1 @f$ as denoted above.
              @param secondItem Is @f$ x_2 @f$ as denoted above.
        """
        if (isinstance(firstItem, quantities.Quantity) or
                isinstance(secondItem, quantities.Quantity)):
            firstItem = quantities.Quantity.value_of(firstItem)
            secondItem = quantities.Quantity.value_of(secondItem)

            firstUnit = firstItem.get_default_unit()
            secondUnit = secondItem.get_default_unit()

            firstComp = firstItem.get_value(firstUnit)
            secondComp = secondItem.get_value(secondUnit)
            return self.get_correlation(firstComp, secondComp)

        if (firstItem == secondItem):
            return 1.0

        return self._correlationMatrix.get((firstItem, secondItem), 0.0)

    def uncertainty(self, component):
        """! @brief This method returns the combined standard uncertainty of an
               uncertain value.
              @param self
              @param component The component of uncertainty to evaluate.
              @return The standard uncertainty.
        """
        if (isinstance(component, quantities.Quantity)):
            unit = component.get_default_unit()
            ucomp = component.get_value(unit)
            return quantities.Quantity(unit, self.uncertainty(ucomp))
        assert (isinstance(component, UncertainComponent))
        components = component.depends_on()
        result = 0.0
        for comp1 in components:
            for comp2 in components:
                result += component.get_uncertainty(comp1) * \
                          self.get_correlation(comp1, comp2) * \
                          component.get_uncertainty(comp2)
        return numpy.sqrt(result)

    def value_uncertainty_unit(self, component):
        """! @brief This method returns the value, combined standard uncertainty, and unit of an
               uncertain value.
              @param self
              @param component The component of uncertainty to evaluate.
              @return (value, The standard uncertainty,unit).
        """
        # if( isinstance( component, quantities.Quantity ) ):
        try:
            unit = component.get_default_unit()
        except AttributeError:
            # does not have unit
            unit = None
        if unit:
            ucomp = component.get_value(unit)
        else:
            ucomp = component.get_value()
        try:
            value = ucomp.get_value()
            if unit:
                uncertainty = self.uncertainty(component).get_value(unit)
            else:
                uncertainty = self.uncertainty(component).get_value()
        except AttributeError:
            value = ucomp
            uncertainty = 0.0
        return value, uncertainty, unit
        # assert( isinstance( component, UncertainComponent ) )

    def dof(self, component):
        """! @brief This method calculates the effective degrees of freedom using
               the Welch-Satterthwaite formulae:
               @f$ \nu_{eff} = \frac{u_c^4(y)}
                             {\sum_{i=1}^N \frac{\left(
                          \frac{\delta f}{\delta x_i}\right)^4 u^4(x_i)}{\nu_i}} @f$
               Where @f$ u_c(y) @f$ is the combined standard uncertainty, 
               @f$ \nu_{i} @f$ is the degrees of freedom of the input @f$ x_i @f$.
               @note The result of this method may be infinite. Since there is
                     no standard procedure in python to declare infinity, we use
                     our own constant for it. 
               @see arithmetic.INFINITY Our infinity constant.
               @param self
               @param component The component of uncertainty.
               @return The effective degrees of freedom @f$ \nu_{eff} @f$.
        """
        if (isinstance(component, quantities.Quantity)):
            unit = component.get_default_unit()
            ucomp = component.get_value(unit)
            return self.dof(ucomp)
        assert (isinstance(component, UncertainComponent))

        # Used to calculate the nominator of the formula described above.
        u_c = self.uncertainty(component)

        components = component.depends_on()

        # check for inifinity (i.e. if one component is infinite, 
        # the entire result will be infinite) and calculate the
        # denominator of the formula described above.
        sum = 0.0
        for comp in components:
            assert (isinstance(comp, UncertainInput))
            dof = comp.get_dof()

            if (dof == 0.0):
                return arithmetic.INFINITY
            elif (dof == arithmetic.INFINITY):
                continue
            else:
                sum += (component.get_uncertainty(comp)) ** 4 / dof

        dof_eff = u_c ** 4 / sum
        return dof_eff

    ## Assign the current context to the given component.
    # \attention This method is only useful in combination with
    #            UncertainComponent.__str__. The context assigned is 
    #            not passed to operations performed on <tt>component</tt>.
    # \see UncertainComponent.__str__
    # \param self
    # \param component The component to which the context should be
    #                  attached.
    # \return component having the context assigned.
    def value_of(self, component):
        # assert(isinstance(component, UncertainComponent))
        if isinstance(component, UncertainComponent):
            component.set_context(self)
        elif isinstance(component, quantities.Quantity):
            component._value.set_context(self)
        return component

## @}
