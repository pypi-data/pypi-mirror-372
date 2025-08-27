## \file operators.py
#  \brief This file contains the classes necessary to define, use, and 
#  handle operations on units.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#          Thomas Reidemeister</a>

## \namespace scuq::operators
# \brief This namespace contains operators that are used for unit conversions.

## \defgroup operators The Operators Module
#
# This module contains the classes necessary to define, handle, and use
# operators on units.
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \addtogroup operators 
# @{

# standard modules
import numpy
#import operator
import numbers
import pickle

# local modules
import scuq.arithmetic as arithmetic
#import scuq.quantities as quantities 

class UnitOperator:
    """! @brief       Basic abstract Operator to use on units.
       @attention This class is intended to be abstract. You
                  have to use one of its silblings get any effect.
    """
    
    def __mul__( self, otherOperator ):
        """! @brief Perform the current operation on another operator.
             
              Another operation @f$g(x)@f$ will be performed on this
              operator @f$f(x)@f$. So that the new Operator is 
              @f$f \times g = g(f(x))@f$.
              @param self
              @param otherOperator The other operator to concat.
              @return The resulting operator.
        """
        assert( isinstance( otherOperator, UnitOperator ) )
        if ( otherOperator == IDENTITY ):
            return self
        if ( self == IDENTITY ):
            return otherOperator
        return CompoundOperator( otherOperator, self )
    
    
    def __invert__( self ):
        """! @brief Invert this operation.
             
              This method returns a new operator that
              represents the inversion of this operator.
              @attention This method is intended to be abstract. The 
                         silblings of this class override it in order
                         to get an effect.
              @param self
              @return The inverse operation of this operation.
        """
        raise NotImplementedError()
    
    
    def is_linear( self ):
        """! @brief Check if the operator is linear.
              
              This method checks if this operator is
              linear or not.
              @attention This method is intended to be abstract. The 
                         silblings of this class override it in order
                         to get an effect.
              @param self
              @return True, if the Operator is linear. 
        """
        raise NotImplementedError

    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method performs the desired operation on an
              absolute value.
              @attention This method is intended to be abstract. The 
                         silblings of this class override it in order
                         to get an effect.
              @param self
              @param value The value to convert.
              @return The converted value
        """
        raise NotImplementedError
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
              @attention This method is intended to be abstract. The 
                         silblings of this class override it in order
                         to get an effect.
              @param self
              @return A string describing this operation.
        """
        raise NotImplementedError
    
    def __getstate__( self ):
        """! @brief Abstract method: Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        raise NotImplementedError
    
    def __setstate__( self, state ):
        """! @brief Abstract method: Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        raise NotImplementedError
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        # global test for IDENTITY
        if( ( self is IDENTITY ) and ( other is IDENTITY ) ):
            return True
        return False
    

class _ExpOperator( UnitOperator ):
    """! @brief       This class provides an Interface for exponential operators.
       It is used as helper for the LogOperator.
      @note Instances of this class can be serialized using pickle.
    """
    
    def __init__( self, exponent ):
        """! @brief Default constructor.
             
              Initializes the operator and assigns the base to the
              current operator.
              @param self
              @param exponent the exponent.
        """
        assert( isinstance(exponent, (numbers.Number, arithmetic.RationalNumber)) )
        self._exponent = exponent
        self._logExponent = numpy.log( exponent )
    
    
    def __invert__( self ):
        """! @brief Invert this operation.
             
              This method returns the inverse operation of the current
              operation.
              @param self
              @return The inverse operation of the current operation.
        """
        return LogOperator( self.get_exponent() )
    
    
    def is_linear( self ):
        """! @brief Check if the operator is linear.
              
              This operator is not linear.
              @param self
              @return False; this operator is not linear.
        """
        return False
    
    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method performs raises the current value
              to the exponent.
              @param self
              @param value The value to convert.
              @return The converted value
        """
        assert( isinstance(value, (numbers.Number, arithmetic.RationalNumber)) )
        return numpy.exp( self._logExponent * float( value ) )
    
    def get_exponent( self ):
        """! @brief Get the base of logarithm.
              
              This method returns the exponent.
             
              @param self
              @return The base of the logarithm
        """
        return self._exponent
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
             
              @param self
              @return A string describing this operation.
        """
        return "^"+str( self._exponent )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._exponent )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._exponent = state
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        if( not isinstance( other, _ExpOperator ) ):
            return False
        return self._exponent == other._exponent

class LogOperator( UnitOperator ):
    """! @brief       This class provides an interface for logarithmic operators.
      @note Instances of this class can be serialized using pickle.
    """
    
    def __init__( self, base ):
        """! @brief Default constructor.
             
              Initializes this operator and assigns the base to it.
              @param self
              @param base The base of the logarithm.
        """
        assert( isinstance(base, (numbers.Number, arithmetic.RationalNumber)) )
        self._base = base
        self._logBase = numpy.log( base )
    
    
    def __invert__( self ):
        """! @brief Invert the current operation.
             
              This method returns the inverse Operation of the current
              operation.
              @param self The current instance of this class.
              @return The inverse Operation of the current Operation.
        """
        return _ExpOperator( self.get_base() )
    
    
    def is_linear( self ):
        """! @brief Check if this operator is linear.
              
              This operator is not linear.
              @param self
              @return False
        """
        return False
    
    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method performs the logarithm on an
              absolute value.
              @attention The logarithm for complex values is not
                         defined.
              @param self
              @param value The value to convert.
              @exception TypeError If the argument is a complex number.
              @return The converted value
        """
        assert( isinstance(value, (numbers.Number, arithmetic.RationalNumber)) )
        return numpy.log( float( value ) )/self._logBase
    
    def get_base( self ):
        """! @brief Get the base of this logarithm.
              
              This method returns the base of the logarithm.
             
              @param self
              @return The base of the logarithm
        """
        return self._base
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
             
              @param self
              @return A string describing this operation.
        """
        return "_"+str( self._base )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._base )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._base = state
        self._logBase = numpy.log( self._base )
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        if( not isinstance( other, LogOperator ) ):
            return False
        return self._base == other._base
    
class AddOperator( UnitOperator ):
    """! @brief       This class provides an Interface for offset operators.
     
      This class adds a constant value to an existing Operator.
      @note Instances of this class can be serialized using pickle.
    """
    
    def _isNegative( positvieOp, negativeOp ):
        """! @brief Helper method to optimize comparsions.
              @param negativeOp An AddOperator.
              @param positvieOp An AddOperator.
              @return <tt>negativeOp.get_offset() == -positvieOp.get_offset()</tt>
        """
        assert( isinstance( positvieOp, AddOperator ) )
        assert( isinstance( negativeOp, AddOperator ) )
        
        negOffset = negativeOp.get_offset()
        posOffset = positvieOp.get_offset()
        # convert to rational number
        try:
            negOffset = arithmetic.RationalNumber.value_of( negOffset )
            posOffset = arithmetic.RationalNumber.value_of( posOffset )
        except TypeError:
            return False
        
        return ( posOffset == -negOffset )
        _isNegative = staticmethod( _isNegative )
        
    def __init__( self, offset ):
        """! @brief Default constructor.
             
              Initializes the operator and assigns the offset to the
              current operator.
              @param self
              @param offset The offset of this operator.
        """
        assert( isinstance(offset, (numbers.Number, arithmetic.RationalNumber)) )
        self._offset = offset
    
    def __mul__( self, otherOperator ):
        """! @brief Perform the current operation on another operator.
             
              The current operation (adding an offset a) will be performed on 
              another operator @f$f(x)@f$. So that the new Operator is 
              @f$a+g(x)@f$.
              If the other Operator is an AddOperator, the offset is updated.
              @param self
              @param otherOperator The other operator to concat.
              @return The resulting operator.
        """
        assert( isinstance( otherOperator, UnitOperator ) )
        if( isinstance( otherOperator, AddOperator ) ):
            # optimize for identity
            if( AddOperator._isNegative( self, otherOperator ) ):
                return IDENTITY
            
            otherOffset = otherOperator.get_offset()
            newOffset   = self.get_offset()+otherOffset
            return AddOperator( newOffset )
        else:
            return UnitOperator.__mul__( self, otherOperator )
    
    
    def __invert__( self ):
        """! @brief Invert the current operation.
             
              This method returns the inverse operation of the current
              operation.
              @param self
              @return The inverse operation of this operation.
        """
        return AddOperator( -self._offset )
    
    
    def is_linear( self ):
        """! @brief Check if this operator is linear.
              
              This operator is not linear.
              @param self
              @return False
        """
        return False
    
    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method performs the addition of an offset on an
              absolute value.
              @param self
              @param value The value to convert.
              @return The converted value
        """
        assert( isinstance(value, (numbers.Number, arithmetic.RationalNumber)) )
        return value+self.get_offset()
    
    def get_offset( self ):
        """! @brief Get the offset.
              
              This method returns the offset of this operator.
             
              @param self
              @return The offset of this operator
        """
        return self._offset
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
             
              @param self
              @return A string describing this operation.
        """
        offset = abs( self._offset )
        if( self._offset < 0.0 ):
            return "-"+str( offset )
        else:
            return "+"+str( offset )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._offset )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._offset = state
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        if( not isinstance( other, AddOperator ) ):
            return False
        return self._offset == other._offset

class MultiplyOperator( UnitOperator ):
    """! @brief       This class provides an Interface for factor operators.
     
      This class multiplies a constant with an existing Operator.
      @note Instances of this class can be serialized using pickle.
    """
    
    def _isNegative( positvieOp, negativeOp ):
        """! @brief Helper method to optimize comparsions.
              @param negativeOp An MultiplyOperator.
              @param positvieOp An MultiplyOperator.
              @return <tt>negativeOp.get_factor() == ~positvieOp.get_factor()</tt>
        """
        assert( isinstance( positvieOp, MultiplyOperator ) )
        assert( isinstance( negativeOp, MultiplyOperator ) )
        
        negFactor = negativeOp.get_factor()
        posFactor = positvieOp.get_factor()
        # convert to rational number
        try:
            negFactor = arithmetic.RationalNumber.value_of( negFactor )
            posFactor = arithmetic.RationalNumber.value_of( posFactor )
        except TypeError:
            return False
        
        return ( negFactor == ~posFactor )
        _isNegative = staticmethod( _isNegative )
    
    def __init__( self, factor ):
        """! @brief Default constructor.
             
              Initializes this operator and assigns the factor to the
              current operator.
              @param self
              @param factor The offset of this operator.
        """
        assert( isinstance(factor, (numbers.Number, arithmetic.RationalNumber)) )
        self._factor = factor
    
    
    def __mul__( self, otherOperator ):
        """! @brief Perform the current operation on another operator.
             
              The current operation (muliplying by a) will be performed on another
              operator @f$f(x)@f$. So that the new operator is @f$a \times g(x)@f$.
              In order to avoid numerical quirks, this method checks wether the
              parameter is an instance of a MuliplyOperator. If yes, then
              only the factor is updated.
              @param self
              @param otherOperator The other operator to concat.
              @return The resulting operator.
        """
        assert( isinstance( otherOperator, UnitOperator ) )
        if( isinstance( otherOperator, MultiplyOperator ) ):
            if( MultiplyOperator._isNegative( self, otherOperator ) ):
                return IDENTITY
            
            otherFactor = otherOperator.get_factor()
            newFactor   = self.get_factor() * otherFactor
            return MultiplyOperator( newFactor )
        else:
            return UnitOperator.__mul__( self, otherOperator )
    
    
    def __invert__( self ):
        """! @brief Invert the current operation.
             
              For example let this operator be @f$ a \times f(x) @f$ then
                       the inverse is @f$ \frac{1}{a} \times f(x) @f$.
              @param self
              @return The inverse Operation of the current Operation.
        """
        # Optimize for integer accuracy
        if( isinstance( self._factor, int ) or 
            isinstance( self._factor, int ) ):
            return MultiplyOperator( arithmetic.RationalNumber( 1, 
                                    self._factor ) )
        # Optimize rational factors
        if( isinstance( self._factor, arithmetic.RationalNumber ) ):
            return MultiplyOperator( ~self._factor )
        # no optimization possible for other types
        return MultiplyOperator( 1.0 / self._factor )
    
    
    def is_linear( self ):
        """! @brief Check if the operator is linear.
              
              This operator is linear.
              @param self
              @return True
        """
        return True
    
    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method performs the multiplication with an factor on an
              absolute value.
              @param self
              @param value The value to convert.
              @return The converted value.
        """
        assert( isinstance(value, (numbers.Number, arithmetic.RationalNumber)) )
        newval = value * self._factor
        #if isinstance(value, quantities.Quantity):
        if hasattr(newval, '_unit'):
            newval._unit=self.toUnit
        return newval
    
    
    def get_factor( self ):
        """! @brief Get the factor.
              
              This method returns the factor of this operator.
             
              @param self
              @return The factor of this operator.
        """
        return self._factor
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
             
              @param self
              @return A string describing this operation.
        """
        return "*"+str( self._factor )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._factor )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._factor = state
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        if( not isinstance( other, MultiplyOperator ) ):
            return False
        return self._factor == other._factor
    

class CompoundOperator( UnitOperator ):
    """! @brief       Compound Operator.
       
       This class is used to generate compound operators 
       (i.e. by calling the concat method of the UnitOperator).
      @note Instances of this class can be serialized using pickle.
    """
    
    def __init__( self, firstOp, secondOp ):
        """! @brief Default Constructor 
             
              For example let the secondOp be @f$ g(x) @f$ and
                       the firstOp be @f$ f(x) @f$ then
                       the compound Operator models @f$ f(g(x)) @f$.
              @param self
              @param firstOp  The operator that is performed at first.
              @param secondOp The operator that is performed at last.
        """
        assert( isinstance( firstOp, UnitOperator ) )
        assert( isinstance( secondOp, UnitOperator ) )
        self._firstOperator = firstOp
        self._secondOperator = secondOp
    
    
    def __invert__( self ):
        """! @brief Invert the current operation.
             
              This method returns the inverse Operation of the current
              operation. Since this Operation is based on two Operations
              the operations are inverted in the reverse order.
              For example let this Operator model @f$y = f(g(x))@f$ the inverse 
                       Operator models @f$ x = g^{-1}(f^{-1}(y))@f$.
              @param self
              @return The inverse operation of the current operation.
        """
        return CompoundOperator( self._secondOperator.__invert__(), 
                    self._firstOperator.__invert__() )
    
    
    def is_linear( self ):
        """! @brief Check if the Operator is linear.
              
              This operator is linear if the underlying operators 
              are linear.
              @param self The current instance of this class.
              @return <tt>True</tt> if both underlying operators are linear.
        """
        return ( self._firstOperator.is_linear() 
            and self._secondOperator.is_linear() )

    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method performs the desired operation on an
              absolute value.
              @param self The current instance of this class.
              @param value The value to convert.
              @return the converted value
        """
        innerValue = self._firstOperator.convert( value )
        return self._secondOperator.convert( innerValue )
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
             
              @param self
              @return A string describing this operation.
        """
        return str( self._firstOperator )+\
               "("+str( self._secondOperator )+")"
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._firstOperator, self._secondOperator )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._firstOperator, self._secondOperator = state
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        if( not isinstance( other, CompoundOperator ) ):
            return False
        return ( self._firstOperator == other._firstOperator and
            self._secondOperator == other._secondOperator )
            
class Identity( UnitOperator ):
    """! @brief       This class provides an Interface for the identity Operator.
     
      This class returns all values as are.
      @attention This class is intendend to be static final. Deriving
                 subclasses makes no sense since there is only one identity
                 operator. Also Instances of this class should be avoided.
                 If you need an identity operator reference it from the global
                 IDENTITY object of this module.
      @note Instances of this class can be serialized using pickle.
    """
        
    def __mul__( self, otherOperator ):
        """! @brief Perform the current operation on another operator.
             
              This method returns the parameter.
              @param self
              @param otherOperator The other operator to concat.
              @return The other Operator.
        """
        assert( isinstance( otherOperator, UnitOperator ) )
        return otherOperator
    
    
    def __invert__( self ):
        """! @brief Invert the current operation.
             
              This method returns the inverse Operation of the current
              operation.
              @param self
              @return The inverse Operation of the current Operation.
              @warning This method is intended to be abstract. You
                        have to override it in order to get any effect.
        """
        return self
    
    
    def is_linear( self ):
        """! @brief Check if the Operator is linear.
              
              Identity is a linear operator. Thus, this method
              always returns True.
              @param self
              @return <tt>True</tt>.
        """
        return True

    
    def convert( self, value ):
        """! @brief Convert a value.
              
              This method returns the parameter.
              @param self
              @param value The value to convert (will be returned).
              @return The parameter value
        """
        return value
    
    def __str__( self ):
        """! @brief Represent this operation by a string.
             
              @param self
              @return A string describing this operation.
        """
        return "*1"
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( 1 )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        assert ( state == 1 )
    
    def __eq__( self, other ):
        """! @brief Test for equality.
              @param self
              @param other Another UnitOperator.
        """
        return isinstance( other, Identity )
    
## Global Identity Operator.
#  
#  Since there is only one Identity, it is defined global here.
IDENTITY = Identity()

## @}
