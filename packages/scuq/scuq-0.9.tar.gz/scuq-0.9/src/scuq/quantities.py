# Example for FFT on Quantities
##In this section we show how to integrate SCUQ in NumPys fft module. 
# Although we implemented most of NumPys ufuncs, we cannot use quantities 
# directly in the fft module of NumPy. The reason for this drawback is 
# the fft module being directly implemented in C requiring floating 
# point ndarrays as input parameters. In compensation, we implemented 
# the floating-point conversion functions of NumPy. Thus our type quantity 
# can be converted to a floating-point number. In order to avoid an 
# unwanted conversion, we require weak consistency checking be enabled 
# to perform the conversion. 
# In Line 5 we create an array of input data. These values are quantities 
# and thus have a unit. To convert these values to float strict 
# consistency checking has to be disabled as shown in Line 15. 
# The converted array can be used as usual, however it lost the 
# information about the unit. We suggest saving the default unit from 
# the quantity before conversion takes place and reassign it to the result.
# \example dft_example.py

# This example shows the integration of SCUQ in NumPys linear algebra module
# <tt>linalg</tt>. The functions of the module convert their arguments to 
# floating point numbers; therefore, a direct integration of our quantities
# type is not feasible. However we implemented floating-point conversion 
# for quantities to solve this issue.
# If a quantity or an ndarray of quantities is an argument of functions 
# like <tt>linalg.inv</tt> is converted to floating point. In order to 
# avoid unwanted conversions to floating point strict consistency checking 
# must be disabled first. Otherwise, the type <tt>Quantity</tt> raises a 
# <tt>ConversionException</tt>.
# In Line 5 we create the quantity that will be stored in a matrix. Our 
# goal is to invert the matrix using NumPys <tt>linalg.inv</tt> method. 
# We disable strict consistency checking in Line 11 and perform the 
# operation in Line 14. Finally, the result has the type float.
# \example linalg_example.py





## \file quantities.py
#  \brief This file contains the classes to model, handle, and use physical
#  quantities. 
# 
#  It also contains some base quantities that can be used
#  to derive combined quantities.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#  Thomas Reidemeister</a>

## \namespace scuq::quantities
# \brief This namespace contains the class Quantity that models
#        physical quantities.

## \defgroup quantities The Quantities Module
#
# This module contains the classes to model, handle, and use physical
# quantities. Because of Pythons nature of weak typing, this implementation
# strongly differs from the jsr-275. In our interpretation a 
# Quantity is a tuple of a numeric value and a unit. Therefore we
# provide a class Quantity that emulates a numeric type and checks
# explicitly for consistency for each operation. Thus, this module
# is able to provide at least runtime checking for physical dimensions.
# For quantities you may choose between strict and non-strict unit
# checks. Strict type checking means that this instance
#        raises an error whenever unequal units are
#        compared. If strict checking is disabled
#        this instance tries to convert among the units. 
#        An error will only be raised, if the units are
#        not compatible (i.e. describe a different physical
#        dimension). For example if you want to add a quantity
#        measured in feet to a quantity measured in meters.
#        If Strict type checking is enabled an error is raised.
#        Otherwise the quantity measured in feet will be
#        transformed to meters before being added.
#        Strict type checking is enabled by default. In this 
#        class we use comparable for the case that the units
#        can be converted to each other and no strict checking
#        is used or for strict type checking and equal units.
# \see Quantity
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \see Quantity.set_strict
# \see Quantity.is_strict
# \addtogroup quantities 
# @{

# standard module
#import operator
import numbers
import collections.abc
import numpy
# local modules
import scuq.arithmetic as arithmetic
import scuq.qexceptions as qexceptions
import scuq.ucomponents as ucomponents
import scuq.cucomponents as cucomponents
#import scuq.si as si
import scuq.units as units

def set_strict(bValue = True):
    """! @brief       An abbreviation for Quantity.set_strict.
      @param bValue
    """
    Quantity.set_strict(bValue)

def is_strict():
    """! @brief       An abbreviation for Quantity.is_strict.
    """
    return Quantity.is_strict()

class Quantity:
    """! @brief       Base class that provides an interface to model quantities.
      @note The numeric types (i.e. int, float,complex, and 
            arithmetic.RationalNumber) are
            automatically transformed to an dimensionless quantity if
            the operations are performed on them. This also applies if
            a quantity is the right operand of the numeric types stated
            above.
      @note Instances of this class can be serialized using pickle.
    """
    
    _STRICT = True
    
    def eval(self):
        u=self._unit
        v=self._value
        try:
            v=v.eval()
        except AttributeError:
            pass
        return Quantity(u,v)
    
    def _unitComparsion( unit1, unit2 ):
        """! @brief Helper method. 
              @param unit1 A unit.
              @param unit2 Another unit.
              @return True if they are compatible and strict is disabled or True
                      if they are equal and strict is enabled.
        """
        strict = Quantity.is_strict()
        
        assert( isinstance( unit1, units.Unit ) )
        assert( isinstance( unit2, units.Unit ) )
        
        return ( ( unit1 == unit2 ) or
                ( unit1.is_compatible( unit2 ) and ( not strict ) ) )
    _unitComparsion = staticmethod( _unitComparsion )
    
    def __init__( self, unit, value ):
        """! @brief Default constructor.
               
               @param self The current instance of this class.
               @param unit The corresponding unit.
               @param value The value assigned
               @note You may use numeric values, sequence types, and
                     instances of ucomponents.UncertainInput as values.
               @see units.Unit
               @see units.Dimensions
        """
        assert( isinstance( unit, units.Unit ) )
        #print ("***** ",type(value)," *****")
        assert( isinstance(value, (numbers.Number,
                                       numpy.ndarray,
                                       collections.abc.Sequence,
                                       ucomponents.UncertainComponent,
                                       cucomponents.CUncertainComponent,
                                       cucomponents.Context,
                                       arithmetic.RationalNumber) ))
        
        # switched arguments !
        assert( not isinstance( value, units.Unit ) )
        assert( not isinstance( value, Quantity ) )
        
        self._unit    = unit
        self._value   = Quantity._accuracy( value )
    
    def reduce_to(self, unit ):
        sdimen=self._unit.get_dimension()
        udimen=unit.get_dimension()
        if sdimen == udimen:
            return Quantity(unit, self._value)
        else:
            return self
    
    def get_value( self, unit ):
        """! @brief Get the absolute value of the quantity using the specified unit.
             
              @param self The current instance of this class.
              @param unit The unit in which the quantity should be expressed in.
              @return The absolute value of the quantity.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if( not Quantity._unitComparsion( self._unit, unit ) ):
            raise qexceptions.ConversionException( unit, 
                                                  " is not comparable to "
                                                  +str( self._unit ) )
        
        operator = self._unit.get_operator_to( unit )
        return operator.convert( self._value )
    
    def get_default_unit( self ):
        """! @brief Get the unit that is used commonly for this quantity.
             
              @param self The current instance of this class.
              @return The corresponding unit.
        """
        return self._unit
    
    def is_dimensionless( self ):
        """! @brief Check if this quantity copatible to dimensionless.
              @param self
              @return True, if the unit assigned is comparable to units.ONE.
        """
        return self._unit.is_compatible( units.ONE )

    def is_dimensionless_strict( self ):
        """! @brief Check if this quantity is dimensionless (strict).
              @param self
              @return True, if the unit assigned IS units.ONE.
        """
        return Quantity._unitComparsion( self._unit, units.ONE )


    
    #emulate numeric behaviour
    
    def __add__( self, other ):
        """! @brief Get the sum of another instance of Quantity and this instance.
              @param self
              @param other Another instance of Quantity or numeric value.
              @return A new instance of Quantity representing the sum of
                      both quantities.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if isinstance(other, numbers.Number):
            if self.is_dimensionless_strict():
                result = self._value + other
            else:
                raise qexceptions.ConversionException( self._unit, 
                    "is not compatible to dimensionless")
        else:
            assert(isinstance(other, Quantity))
            # check if the units are comparable
            if( not Quantity._unitComparsion( self._unit, other._unit ) ):
                raise qexceptions.ConversionException( other._unit, 
                    "is not compatible to "+str( self._unit ) )
            # get the other quantity in this unit
            result = self._value + other.get_value( self._unit )
        return Quantity( self._unit, result )
    
    def __sub__( self, other ):
        """! @brief Get the difference of another instance of Quantity and this instance.
              @param self
              @param other Another instance of Quantity.
              @return A new instance of Quantity representing the difference of
                      both quantities.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        return self.__add__( -other )
    
    def __mul__( self, other ):
        """! @brief Get the product of another instance of Quantity and this instance.
              @attention This method performs no conversion of alternate units: 
                    Even if the units are defined in the same dimension. For example,
                    if one takes @f$m \times ft@f$ the result will be @f$ ft m @f$
                    not @f$m^2@f$ nor @f$ft^2@f$.
              @param self
              @param other Another instance of Quantity or numeric value.
              @return A new instance of Quantity representing the product of
                      both quantities.
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        if isinstance(other, numbers.Number):            
            newUnit  = self._unit
            newValue = self._value * other
        else:
            newUnit  = self._unit * other._unit
            newValue = self._value * other._value
        return Quantity( newUnit, newValue )
    
    def __pow__( self, other ):
        """! @brief Get the power of of this instance.
              @param self
              @param other The power to which this instance is raised (must be
                           an integer or dimensionless quantity).
              @return A new instance of Quantity representing the power of
                      this instance.
              @exception qexceptions.ConversionException If a quantity argument 
                         is not dimensionless.
              @see units.Unit.__pow__
        """
        assert(isinstance(other, (Quantity,numbers.Number)))
        if isinstance(other, numbers.Number):            
            newUnit  = self._unit**other
            newValue = self._value ** other
        else:
            if( not Quantity._unitComparsion( other.get_default_unit(), 
                                                  units.ONE ) ):
                raise qexceptions.ConversionException( self._unit, 
                                                           "The argument is not comparable to a dimensionless "
                                                           +"quantity "
                                                           +str( other._unit ) )
            newValue = self._value ** other._value
            newUnit  = self._unit ** other._value
        return Quantity( newUnit, newValue )
    
    def __truediv__( self, other ):
        """! @brief Get the fraction of another instance of Quantity and this instance.
              @attention This method performs no conversion of alternate units: 
                    Even if the units are defined in the same dimension. For example,
                    if one takes @f$m \div ft@f$ the result will be 
                    @f$ \frac{ft}{m} @f$ not dimensionless.
              @param self The dividend.
              @param other Another instance of Quantity or numeric value used as 
                     divisor.
              @return A new instance of Quantity representing the sum of
                      both quantities.
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        if isinstance(other, numbers.Number):            
            newUnit  = self._unit
            newValue = self._value / other
        else:
            newUnit  = self._unit / other._unit
            newValue = self._value / other._value
        return Quantity( newUnit, newValue )
    
    
    def __radd__( self, other ):
        """! @brief Get the sum of this instance of Quantity and another value.
              @attention This library assumes that this is a commutative operation.
              @param self
              @param other Another value (not an instance of Quantity).
              @return A new instance of Quantity representing the sum.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        # since the addition is symetric
        return self.__add__( other )
    
    def __rsub__( self, other ):
        """! @brief Get the difference of another value and this instance of Quantity.
              @param self
              @param other Another value (not an instance of Quantity).
              @return A new instance of Quantity representing the difference of
                      both quantities.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        # other - self = -self+other
        v = -1*self
        return v.__add__(other)
    
    def __rmul__( self, other ):
        """! @brief Get the product of this instance of Quantity and another value.
              @attention This library assumes that this is a commutative operation.
              @param self
              @param other Another value (not an instance of Quantity).
              @return A new instance of Quantity representing the product of
                      both quantities.
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        if isinstance(other, numbers.Number):
            newValue = other * self._value
            newUnit  = self._unit
        else:    
            newValue = other._value * self._value
            newUnit  = other._unit * self._unit
        return Quantity( newUnit, newValue )
    
    def __rtruediv__( self, other ):
        """! @brief Get the fraction of another value and this instance.
              @param self The divisor.
              @param other Another instance of Quantity or numeric value used as 
                     dividend.
              @return A new instance of Quantity representing the sum of
                      both quantities.
        """
        assert(isinstance( other, (Quantity,numbers.Number) ) )
        if isinstance(other, numbers.Number):
            newValue = other / self._value
            newUnit  = units.ONE / self._unit
        else:    
            newValue = other._value / self._value
            newUnit  = other._unit / self._unit
        return Quantity( newUnit, newValue )
    
    def __rpow__( self, other ):
        """! @brief Get the power of another value and this instance.
              @attention In contrast to Quantity.__pow__ this
                         instance also accepts floating point powers.
              @param self
              @param other Another instance of Quantity.
              @return A new instance of Quantity representing the sum of
                      both quantities.
              @exception qexceptions.ConversionException If this unit is not
                         comparable to units.ONE.
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        if( not Quantity._unitComparsion( self._unit, units.ONE) ):
            raise qexceptions.ConversionException( self, 
                                                  "this unit is not"+
                                                  " dimensionless!" )
        return other ** self._value
    
    def __iadd__( self, other ):
        """! @brief Add the argument to this instance.
              @param self
              @param other Another instance of Quantity or numeric value.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if isinstance(other, numbers.Number):
            if self.is_dimensionless_strict():
                self._value += other
            else:
                raise qexceptions.ConversionException(self._unit)
        else:
            assert(isinstance(other, Quantity))
            result = self + other # may throw exception
            # assign the values
            self._unit  = result._unit
            self._value = result._value
        return self
    
    def __isub__( self, other ):
        """! @brief Substract the argument from this instance.
              @param self
              @param other Another instance of Quantity or numeric value.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if isinstance(other, numbers.Number):
            if self.is_dimensionless_strict():
                self._value -= other
            else:
                raise qexceptions.ConversionException(self._unit)
        else:
            assert(isinstance(other, Quantity))
            result = self - other # may throw exception
            # assign the values
            self._unit  = result._unit
            self._value = result._value
        return self

    def __imul__( self, other ):
        """! @brief Multiply this instance with the argument.
              @param self
              @param other Another instance of Quantity or numeric value.
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        result = self * other 
        # assign the values
        self._unit  = result._unit
        self._value = result._value
        return self
    
    def __idiv__( self, other ):
        """! @brief Divide this instance by the argument.
              @param self
              @param other Another instance of Quantity or numeric value..
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        result = self / other 
        # assign the values
        self._unit  = result._unit
        self._value = result._value
        return self
    
    def __ipow__( self, other ):
        """! @brief Raise the this instance to the argument.
              @param self
              @param other Another instance of Quantity or numeric value.
        """
        assert(isinstance(other, (Quantity, numbers.Number)))
        result = self ** other
        # assign the values
        self._unit    = result._unit
        self._value   = result._value
        return self
    
    def __neg__( self ):
        """! @brief Negate the value of this quantity.
              @param self
              @return A new instance of Quantity representing the negative of
                      this quantity.
        """
        return Quantity( self._unit, -self._value)
    
    def __pos__( self ):
        """! @brief Copy this instance.
              @param self
              @return A copy of the current instance.
        """
        return Quantity( self._unit, self._value)
    
    def __abs__( self ):
        """! @brief Get the absolute value of this Quantity.
              @param self
              @return The absolute value of this quantity.
        """
        return Quantity( self._unit, abs( self._value ) )
    
    def __invert__( self ):
        """! @brief Return the inverted instance of this Quantity.
              For example, let your quantity be @f$ \frac{1}{2} \frac{m}{s} @f$,
              then the result of this operation is @f$ 2 \frac{s}{m} @f$.
              @param self
              @return The inverted quantity.
        """
        return Quantity( ~self._unit, ~self._value)
    
    def __complex__( self ):
        """! @brief Cast this instance to the numeric type complex.
              @attention All information about the unit used will be
                         stripped from the result.
              @param self
              @return The value of this instance casted to complex.
        """
        if(Quantity.is_strict() and self.get_default_unit() != units.ONE):
            raise qexceptions.ConversionException(
                "Only dimensionless quantities can be converted to complex")
        return complex( self._value )
    
    def __long__( self ):
        """! @brief Cast this instance to the numeric type long.
              @attention All information about the unit used will be
                         stripped from the result.
              @param self
              @return The value of this instance casted to long.
        """
        if(Quantity.is_strict() and self.get_default_unit() != units.ONE):
            raise qexceptions.ConversionException(
                "Only dimensionless quantities can be converted to long")
        return int( self._value )
    
    def __float__( self ):
        """! @brief Cast this instance to the numeric type float.
              @attention All information about the unit used will be
                         stripped from the result.
              @attention This conversion is only possible, if weak consitency
              checking is enabled.
              @param self
              @return The value of this instance casted to float.
        """
        if(Quantity.is_strict() and self.get_default_unit() != units.ONE):
            raise qexceptions.ConversionException(
                "Only dimensionless quantities can be converted to float")
        return float( self._value )
    
    def __int__( self ):
        """! @brief Cast this instance to the numeric type int.
              @attention All information about the unit used will be
                         stripped from the result.
              @param self
              @return The value of this instance casted to int.
        """
        if(Quantity.is_strict() and self.get_default_unit() != units.ONE):
            raise qexceptions.ConversionException(
                "Only dimensionless quantities can be converted to int")
        return int( self._value )
    
    def __str__( self ):
        """! @brief Get a string describing this Quantity.
              The result will be of the form <tt>value unit</tt>
              (i.e. "12.0 m").
              @param self
              @return A string describing this quantity.
        """
        return str( self._value )+" "+str( self._unit )

    def __repr__( self ):
        """! @brief Get a string describing this Quantity.
              The result will be of the form <tt>Quantity(unit, value)</tt>
              (i.e. "Quantity(si.METER, 12.0)").
              @param self
              @return A string describing this quantity.
        """
        return "Quantity(%s, %s)"%(self._unit, self._value)
    
    def __lt__( self, other ):
        """! @brief Check, if this instance is less than the argument.
              A comparsion will be done, if the units are comparable.
              @param self
              @param other Another instance of Quantity.
              @return True, if this instance is less than the argument.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if(not isinstance(other, Quantity)):
            a,b = self._coerce(other)
            return a < b
        if( not Quantity._unitComparsion( self._unit, other._unit) ):
            raise qexceptions.ConversionException( self, 
                                                  " is not comparable to "
                                                  +str( other ) )
        otherValue = other.get_value( self._unit )
        return self._value < otherValue
    
    def __le__( self, other ):
        """! @brief Check, if this instance is less or equal to the argument.
              A comparsion will be done, if the units are comparable.
              @param self
              @param other Another instance of Quantity.
              @return True, if this instance is less or equal to the argument.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if(not isinstance(other, Quantity)):
            a,b = self._coerce(other)
            return a <= b
        if( not Quantity._unitComparsion( self._unit, other._unit ) ):
            raise qexceptions.ConversionException( self, 
                                                  " is not comparable to "
                                                  +str( other ) )
        otherValue = other.get_value( self._unit )
        return self._value <= otherValue
    
    def __eq__( self, other ):
        """! @brief Check, if this instance is equal to the argument.
              A comparsion will be done, if the units are comparable.
              @param self
              @param other Another instance of Quantity.
              @return True, if this instance is equal to the argument.
        """
        if(not isinstance(other, Quantity)):
            try:
                a,b = self._coerce(other)
                return a == b
            except NotImplementedError:
                return False
        if( not Quantity._unitComparsion( self._unit, other._unit ) ):
            return False
        otherValue = other.get_value( self._unit )
        return self._value == otherValue
    
    def __ne__( self, other ):
        """! @brief Check, if this instance is not equal to the argument.
              A comparsion will be done, if the units are comparable.
              @param self
              @param other Another instance of Quantity.
              @return True, if this instance is not equal to the argument.
        """
        if(not isinstance(other, Quantity)):
            a,b = self._coerce(other)
            return a != b
        if( not Quantity._unitComparsion( self._unit, other._unit ) ):
            return True
        otherValue = other.get_value( self._unit )
        return self._value != otherValue
    
    def __gt__( self, other ):
        """! @brief Check, if this instance is greater than the argument.
              A comparsion will be done, if the units are comparable.
              @param self
              @param other Another instance of Quantity.
              @return True, if this instance is greater than the argument.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if(not isinstance(other, Quantity)):
            a,b = self._coerce(other)
            return a > b
        if( not Quantity._unitComparsion( self._unit, other._unit ) ):
            raise qexceptions.ConversionException( self, 
                                                  " is not comparable to "
                                                  +str( other ) )
        otherValue = other.get_value( self._unit )
        return self._value > otherValue
    
    def __ge__( self, other ):
        """! @brief Check, if this instance is greater or equal to the argument.
              A comparsion will be done, if the units are comparable.
              @param self
              @param other Another instance of Quantity.
              @return True, if this instance is greater or equal to the argument.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        if(not isinstance(other, Quantity)):
            a,b = self._coerce(other)
            return a >= b
        if( not Quantity._unitComparsion( self._unit, other._unit ) ):
            raise qexceptions.ConversionException( self, 
                                                  " is not comparable to "
                                                  +str( other ) )
        otherValue = other.get_value( self._unit )
        return self._value >= otherValue
    
    def __cmp__( self, other ):
        """! @brief Compare two instances of quantity.
              @param self
              @param other Another instance of Quantity or numeric value.
              @return -1, if the this instance is less than the argument,
                       0, if this instance is equal to the argument,
                      +1, if this instance is greater than the argument.
              @exception qexceptions.ConversionException If the units are not
                         comparable.
        """
        def cmp(a, b):
            return (a > b) - (a < b)

        if(not isinstance(other, Quantity)):
            a,b = self._coerce(other)
            return cmp(a,b)
        if( not Quantity._unitComparsion( self._unit, other._unit ) ):
            raise qexceptions.ConversionException( self, 
                                                  " is not comparable to "
                                                  +str( other ) )
        if( self < other ):
            return -1
        if( self > other ):
            return 1
        if( self == other ):
            return 0
        # this should not happen
        assert( 0 )
        
    def __getstate__( self ):
        """! @brief
               Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._unit, self._value )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._unit, self._value = state
    
    def value_of( other ):
        """! @brief Factory for generating quantities.
              @param other A quantity, or another value.
              @return A Quantity. If the argument is a quantity
                      this method returns it. If the argument is
                      a numeric value, this method generates a 
                      dimensionless quantity having the argument
                      as value. 
               @note You may use numeric values, sequence types, and
                     instances of ucomponents.UncertainInput as values.
        """
        if( isinstance( other, Quantity ) ):
            return other
        assert( isinstance(other, numbers.Number) or 
                isinstance(other, collections.abc.Sequence) or
                isinstance( other, ucomponents.UncertainInput )  or
                isinstance(other, arithmetic.RationalNumber))
        assert( not isinstance( other, units.Unit ) )
        
        # Create a dimensionless quantity having the 
        # argument as value.
        return Quantity( units.ONE, other )
    value_of = staticmethod( value_of )
    
    def _accuracy( value ):
        """! @brief Helper method, to increase the accuracy of integer operations.
              As soon an int or long is provided, it is converted to a
              rational number.
              @param value The value to be converted.
        """
        if( isinstance( value, int ) or isinstance( value, int ) ):
            return arithmetic.RationalNumber( value, 1 )
        else:
            return value
    _accuracy = staticmethod( _accuracy )
    
    #Support for numpy
    
    def arccos( self ):
        """! @brief This method provides the broadcast interface for
              numpy.arccos.
              @param self
              @return The inverse Cosine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.arccos( self._value )

        return Quantity( units.ONE, value )
    
    def arccosh( self ):
        """! @brief This method provides the broadcast interface for
              numpy.arccosh.
              @param self
              @return The inverse hyperbolic Cosine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.arccosh( self._value )

        return Quantity( units.ONE, value )
    
    def arcsin( self ):
        """! @brief This method provides the broadcast interface for
              numpy.arcsin.
              @param self
              @return The inverse Sine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.arcsin( self._value )

        return Quantity( units.ONE, value )
    
    def arcsinh( self ):
        """! @brief This method provides the broadcast interface for
              numpy.arcsinh.
              @param self
              @return The inverse hyperbolic Sine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.arcsinh( self._value )

        return Quantity( units.ONE, value )
    
    def arctan( self ):
        """! @brief This method provides the broadcast interface for
              numpy.arctan.
              @param self
              @return The inverse Tangent of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.arctan( self._value )

        return Quantity( units.ONE, value )
    
    def arctanh( self ):
        """! @brief This method provides the broadcast interface for
              numpy.arctanh.
              @param self
              @return The inverse hyperbolic Tangent of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.arctanh( self._value )

        return Quantity( units.ONE, value )
    
    def cos( self ):
        """! @brief This method provides the broadcast interface for
              numpy.cos.
              @param self
              @return The Cosine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.cos( self._value )

        return Quantity( units.ONE, value )
    
    def cosh( self ):
        """! @brief This method provides the broadcast interface for
              numpy.cosh.
              @param self
              @return The hyperbolic Cosine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.cosh( self._value )

        return Quantity( units.ONE, value )
    
    def tan( self ):
        """! @brief This method provides the broadcast interface for
              numpy.tan.
              @param self
              @return The Tangent of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.tan( self._value )

        return Quantity( units.ONE, value )
    
    def tanh( self ):
        """! @brief This method provides the broadcast interface for
              numpy.tanh.
              @param self
              @return The hyperbolic Tangent of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.tanh( self._value )

        return Quantity( units.ONE, value )
    
    def log10( self ):
        """! @brief This method provides the broadcast interface for
              numpy.log10.
              @param self
              @return The decadic Logarithm of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.log10( self._value )

        return Quantity( units.ONE, value )
    
    def log2( self ):
        """! @brief This method provides the broadcast interface for
              numpy.log2.
              @param self
              @return The binary logarithm of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.log2( self._value )

        return Quantity( units.ONE, value )
    
    def sin( self ):
        """! @brief This method provides the broadcast interface for
              numpy.sin.
              @param self
              @return The Sine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.sin( self._value )

        return Quantity( units.ONE, value )
    
    def sinh( self ):
        """! @brief This method provides the broadcast interface for
              numpy.sinh.
              @param self
              @return The hyperbolic Sine of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.sinh( self._value )

        return Quantity( units.ONE, value )
    
    def sqrt( self ):
        """! @brief This method provides the broadcast interface for
              numpy.sqrt.
              @param self
              @return The Square Root of this quantity.
        """
        value = numpy.sqrt( self._value )
        unit  = numpy.sqrt( self._unit )
        
        return Quantity( unit, value )
    
    def square( self ):
        """! @brief This method provides the broadcast interface for
              numpy.sqrt.
              @param self
              @return The Square Root of this quantity.
        """
        return self*self
    
    def fabs( self ):
        """! @brief This method provides the broadcast interface for
              numpy.fabs.
              @param self
              @return The absolute value of this quantity.
        """
        value = numpy.fabs( self._value )

        return Quantity( self._unit, value )

    def absolute( self ):
        """! @brief This method provides the broadcast interface for
              numpy.absolute.
              @param self
              @return The absolute value of this quantity.
        """
        value = numpy.absolute( self._value )

        return Quantity( self._unit, value )
    
    def __floor__( self ):
        """! @brief This method provides the broadcast interface for
              numpy.floor.
              @param self
              @return The largest integer less than or equal to this quantity.
        """
        try:
            value=self._value.__floor__()
        except AttributeError:
            value = numpy.floor( self._value )

        return Quantity( self._unit, value )
    
    def __ceil__( self ):
        """! @brief This method provides the broadcast interface for
              numpy.ceil.
              @param self
              @return The largest integer greater than or equal to this 
                      quantity.
        """
        try:
            value=self._value.__ceil__()
        except AttributeError:
            value = numpy.ceil( self._value )

        return Quantity( self._unit, value )
    
    def exp( self ):
        """! @brief This method provides the broadcast interface for
              numpy.exp.
              @param self
              @return The Exponential of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)

        value = numpy.exp( self._value )

        return Quantity( units.ONE, value )
    
    def log( self ):
        """! @brief This method provides the broadcast interface for
              numpy.log.
              @param self
              @return The Natural Logarithm of this quantity.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if( not self.is_dimensionless() ):
            raise qexceptions.NotDimensionlessException(self._unit)
                    
        value = numpy.log( self._value )

        return Quantity( units.ONE, value )
    
    def arctan2( self, other ):
        """! @brief This method provides the broadcast interface for
              numpy.arctan2.
              @param self
              @param other Another instance of Quantity.
              @return The inverse two-argument tangent of the arguments.
              @exception qexceptions.NotDimensionlessException 
                         If the unit assigned is not dimensionless.
        """
        if isinstance(other, numbers.Number):
            if self.is_dimensionless():
                value = numpy.arctan2(float(self._value), other)
                return Quantity( units.ONE, value )
            else:
                raise qexceptions.NotDimensionlessException(self._unit)
        elif isinstance(other, Quantity):
            other_val=other.get_val(self.get_default_unit()) # may raise a qexceptions.ConversionException
            return Quantity( units.ONE, numpy.arctan2(float(self._value), float(other_val)) )
        else:
            raise NotImplementedError
            
    
    def hypot(self, other):
        """! @brief This method provides the broadcast interface for
              hypothenusis.
              @param self
              @param other Another instance of Quantity.
              @return The hypothenusis of the arguments.
        """
        if(not isinstance(other, Quantity)):
            tmp,other = self._coerce(other)
            return numpy.hypot(tmp, other)
        assert(isinstance(other, Quantity))
        return numpy.sqrt(self*self + other*other)
    
    def conjugate( self ):
        """! @brief This method provides the broadcast interface for
              numpy.conjugate.
              @param self
              @return This quantity.
        """
        try:
            value = self._value.conjugate()
        except AttributeError:
            value = numpy.conjugate( self._value )

        return Quantity( self._unit, value )
    
    def set_strict(bValue = True):
        """! @brief Turn on/off the strict evaluation of quantities. This will 
               affect any quantities calculation beyond this point.
               @param bValue True or False
        """
        if(bValue):
            Quantity._STRICT = True
        else:
            Quantity._STRICT = False
    set_strict = staticmethod(set_strict)
            
    def is_strict():
        """! @brief Get the type of quantities calculation. If either
              strict or non strict evaluation of quantities is
              implemented.
              @return True (i.e. strict enabled) or False (i.e. strict disabled).
        """
        return Quantity._STRICT
    is_strict = staticmethod(is_strict)
    
    def _coerce(self, other):
        """! @brief Implementation of coercion rules.
        \see Coercion - The page describing the coercion rules."""
        if(isinstance(other, Quantity)):
            return (self, other)
        elif(isinstance(other, int) or
             isinstance(other, float) or
             isinstance(other, complex) or
             isinstance(other, arithmetic.RationalNumber)):
            other = Quantity.value_of(other)
            return (self, other)
        elif(isinstance(other, numpy.ndarray)):
            if(other.dtype == Quantity):
                raise NotImplementedError("Cannot encapsulate ndarrays of"
                                         +"quantities in quantities")
        else:
            raise NotImplementedError()
    def get_expectation_value_as_float( self ):
        v=self._value
        try:
            v=v.get_value()
        except AttributeError:
            pass
        return v
            
    def get_expectation_value( self ):
        v=self.get_expectation_value_as_float()
        return Quantity(self._unit, v)
        
## @}

