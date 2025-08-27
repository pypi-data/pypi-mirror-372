## \file testcases.py
#  \brief This file contains a variety of test cases that verify this library.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#          Thomas Reidemeister</a>

## \namespace scuq::testcases
# \brief This namespace contains several test cases to validate and verify
#        this class library.

## \defgroup testcases Testcases to verify the Quantitites library.
#
# This module contains a variety of test cases that verify this library.
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \addtogroup testcases 
# @{

# standard modules
import numpy
import operator
import numbers
import pickle
import types
import unittest
import sys

# local modules
# from . import arithmetic
# from . import operators
# from . import qexceptions
# from . import si
# from . import ucomponents
# from . import cucomponents
# from . import quantities
# from . import units
from scuq import arithmetic
from scuq import operators
from scuq import qexceptions
from scuq import si
from scuq import ucomponents
from scuq import cucomponents
from scuq import quantities
from scuq import units


def test_serialization( instance, copy, sanityInstance, type, bCopy=True ):
    """! @brief       A general test for serialization of instances.
      @attention This test is only based on the __eq__
                 method of the instance. It is assumed that
                 this method is working correctly.
      @param instance The instance to serialize.
      @param copy     A copy of the instance (having other object
                      reference).
      @param sanityInstance An instance that is not equal
                      to the instance.
      @param type     The type of the instance and the copy.
      @param bCopy    Use the above parameter copy (True,default), or
                      apply only a weak check using no copy.
    """
    # sanity tests
    assert( isinstance( instance, type ) )
    if( bCopy ):
        assert( isinstance( copy, type ) )
        assert( instance == copy )
        assert( not ( instance is copy ) )
        assert( sanityInstance != copy )
        
    assert( sanityInstance != instance )
        
    # If False is returned, the object can not be
    # serialized
    assert( instance.__getstate__() != False )
    
    # check the serialization using all available protocols
    for i in range( 0, pickle.HIGHEST_PROTOCOL+1 ):
        # serialize the object
        someString = pickle.dumps( instance )
        # is the result really a string?
        assert( someString != None )
        assert( len( someString ) > 0 )
        
        # Same thing for the sanity Object
        assert( sanityInstance.__getstate__() != False )
        # serialize the object
        sanityString = pickle.dumps( sanityInstance )
        # is the result really a string?
        assert( sanityString != None )
        assert( len( sanityString ) > 0 )
        
        # assert different code
        assert( sanityString != someString )
        
        # dserialize the objects
        deserializedInstance = pickle.loads( someString )
        deserializedSanity   = pickle.loads( sanityString )
        
        assert( isinstance( deserializedInstance, type ) )
        # something would be seriously wrong
        assert( deserializedInstance != deserializedSanity )
        # that is what we want to test
        if( bCopy ):
            assert( deserializedInstance == copy )
            # unlikely, but maybe a prog. error
            assert( not ( deserializedInstance is copy ) )
    
class TestSIUnits( unittest.TestCase ):
    """! @brief       SI Testing class.
      This class tests the definition and semantics of
      the SI units.
    """
    
    def BASE_UNIT_TEST( unit, dimension, idiotsUnit, symbol, idiotsDimension ):
        """! @brief Test base units.
              @param unit      The instance of the unit to test.
              @param dimension The physical dimension in which the base unit
                               should be defined.
              @param idiotsUnit A unit that should not be compatible or equal
                                to this unit.
              @param symbol    The string is equal to the units symbol.
              @param idiotsDimension  A dimension in which the unit should not 
                                be defined.
        """
        assert( unit.get_symbol() == symbol )
        assert( unit.get_dimension() == dimension )
        assert( unit.get_dimension() != idiotsDimension )
        assert( unit != idiotsUnit )
        assert( not unit.is_compatible( idiotsUnit ) )
        # Test serialization (using no copy, since the unit needs to be 
        # unique)
        test_serialization( unit, None, idiotsUnit, units.BaseUnit, False )
    BASE_UNIT_TEST = staticmethod( BASE_UNIT_TEST )
    
    def TRANSFORMED_TEST( unit, parent, valueParent, valueTransformed, 
		                         maxAcceptableError ):
        """! @brief Test transformed units.
              @param unit      The instance of the unit to test.
              @param parent    The expected parent unit of the unit.
              @param valueParent An example for a numeric value that 
                                 represents the parent.
              @param valueTransformed An example for a numeric value that
                                      represens this unit.
              @param maxAcceptableError The maximum acceptable numeric error.  
        """
        assert( unit.get_parent() == parent )
        assert( unit.is_compatible( parent ) )
        operator = unit.to_parent_unit()
        result   = operator.convert( valueParent )
        assert( abs( result - valueTransformed ) < maxAcceptableError )
        operator = ~operator
        result   = operator.convert( valueTransformed )
        assert( abs( result - valueParent ) < maxAcceptableError )
        # Test serialization (using no copy, since the unit needs 
        # to be unique)
        test_serialization( unit, None, parent, units.TransformedUnit, False )
    TRANSFORMED_TEST = staticmethod( TRANSFORMED_TEST )
    
    def ALTERNATE_TEST( unit, parent, idiotsUnit, symbol ):
        """! @brief Test alternate units.
              @param unit      The instance of the unit to test.
              @param parent    The expected parent unit of the unit.
              @param idiotsUnit A unit that should not be compatible or equal
                                to this unit.
              @param symbol    The string is equal to the units symbol.
        """
        assert( unit.get_symbol() == symbol )
        assert( idiotsUnit != unit )
        assert( unit != parent )
        assert( unit.get_parent() == parent )
        assert( unit.get_system_unit() != parent )
        assert( unit.get_system_unit() == unit )
        assert( unit.is_compatible( parent ) )        
        assert( unit.is_compatible( unit ) )
        assert( not unit.is_compatible( idiotsUnit ) )
        test_serialization( unit, None, idiotsUnit, units.AlternateUnit, 
				                    False )
    ALTERNATE_TEST = staticmethod( ALTERNATE_TEST )
    
    
    def test_base_units( self ):
        """! @brief Test the base SI units.
              @param self
              @see BASE_UNIT_TEST
        """
        TestSIUnits.BASE_UNIT_TEST( si.AMPERE, units.CURRENT, units.ONE, "A", 
                                  units.NONE )
        TestSIUnits.BASE_UNIT_TEST( si.CANDELA, units.LUMINOUS_INTENSITY, 
                                  si.AMPERE, "cd", units.CURRENT )
        TestSIUnits.BASE_UNIT_TEST( si.KELVIN, units.TEMPERATURE, si.AMPERE, 
                                  "K", units.CURRENT )
        TestSIUnits.BASE_UNIT_TEST( si.KILOGRAM, units.MASS, si.AMPERE, "kg", 
                                  units.CURRENT )
        TestSIUnits.BASE_UNIT_TEST( si.METER, units.LENGTH, si.AMPERE, "m", 
                                  units.CURRENT )
        TestSIUnits.BASE_UNIT_TEST( si.MOLE, units.SUBSTANCE, si.AMPERE, 
				                            "mol", units.CURRENT )
        TestSIUnits.BASE_UNIT_TEST( si.SECOND, units.TIME, si.AMPERE, "s", 
                                  units.CURRENT )
    
    def test_alternate_units( self ):
        """! @brief Test the alternate SI units.
              @param self
              @see ALTERNATE_TEST
        """
        TestSIUnits.ALTERNATE_TEST( si.RADIAN, units.ONE, si.AMPERE, "rad" )
        TestSIUnits.ALTERNATE_TEST( si.STERADIAN, units.ONE, si.AMPERE, "sr" )
        TestSIUnits.ALTERNATE_TEST( si.NEWTON, 
                                   si.KILOGRAM * si.METER/( si.SECOND ** 2 ), 
                                   si.AMPERE, "N" )
        TestSIUnits.ALTERNATE_TEST( si.PASCAL, si.NEWTON / ( si.METER ** 2 ), 
                                   si.AMPERE, "Pa" )
        TestSIUnits.ALTERNATE_TEST( si.JOULE, si.NEWTON * si.METER, 
                                   si.AMPERE, "J" )
        TestSIUnits.ALTERNATE_TEST( si.WATT, si.JOULE / si.SECOND, 
                                   si.AMPERE, "W" )
        TestSIUnits.ALTERNATE_TEST( si.COULOMB, si.AMPERE * si.SECOND, 
                                   si.AMPERE, "C" )
        TestSIUnits.ALTERNATE_TEST( si.VOLT, si.WATT / si.AMPERE, 
                                   si.AMPERE, "V" )
        TestSIUnits.ALTERNATE_TEST( si.FARAD, si.COULOMB / si.VOLT, 
                                   si.AMPERE, "F" )
        #_omega = "\u03A9"
        #_encoded = _omega.encode( "UTF-8" )
        TestSIUnits.ALTERNATE_TEST( si.OHM, si.VOLT / si.AMPERE, 
                                   si.AMPERE, 'u"\N{Greek Capital Letter Omega}"' )
        TestSIUnits.ALTERNATE_TEST( si.SIEMENS, si.AMPERE / si.VOLT, 
                                   si.AMPERE, "S" )
        TestSIUnits.ALTERNATE_TEST( si.WEBER, si.VOLT * si.SECOND, 
                                   si.AMPERE, "Wb" )
        TestSIUnits.ALTERNATE_TEST( si.TESLA, si.WEBER / ( si.METER ** 2 ), 
                                   si.AMPERE, "T" )
        TestSIUnits.ALTERNATE_TEST( si.HENRY, si.WEBER / si.AMPERE, 
                                   si.AMPERE, "H" )
        TestSIUnits.ALTERNATE_TEST( si.LUMEN, si.CANDELA * si.STERADIAN, 
                                   si.AMPERE, "lm" )
        TestSIUnits.ALTERNATE_TEST( si.LUX, si.LUMEN / ( si.METER**2 ), 
                                   si.AMPERE, "lx" )
        TestSIUnits.ALTERNATE_TEST( si.BECQUEREL, ~si.SECOND, 
                                   si.AMPERE, "Bq" )
        TestSIUnits.ALTERNATE_TEST( si.GRAY, si.JOULE / si.KILOGRAM, 
                                   si.AMPERE, "Gy" )
        TestSIUnits.ALTERNATE_TEST( si.SIVERT, si.JOULE / si.KILOGRAM, 
                                   si.AMPERE, "Sv" )
        TestSIUnits.ALTERNATE_TEST( si.KATAL, si.MOLE / si.SECOND, 
                                   si.AMPERE, "kat" )
        assert( si.KATAL != si.AMPERE )
        
    def test_transformed_units( self ):
        """! @brief Test the transformed SI units (i.e. there is only one: degrees Celsius)
              @param self
              @see TRANSFORMED_TEST
        """
        TestSIUnits.TRANSFORMED_TEST( si.CELSIUS, si.KELVIN, 
                                     273.15, 0.0, 1e-10 )
        
    def test_rational_powers( self ):
        """! @brief Test rational powers of units.
              @param self
        """
        result = si.AMPERE ** arithmetic.RationalNumber( 2, 1 )
        assert( result == si.AMPERE ** 2 )
        
        result = numpy.sqrt(si.AMPERE)*si.AMPERE
        assert(result == si.AMPERE ** arithmetic.RationalNumber(3,2))
        
        result = si.AMPERE*numpy.sqrt(si.AMPERE)
        assert(result == si.AMPERE ** arithmetic.RationalNumber(3,2))
        
class TestArithmetic( unittest.TestCase ):
    """! @brief       This class provides the tests to verify the rational number module.
    """
    def test_rational_creation( self ):
        """! @brief Test the creation of the Type arithmetic.RationalNumber.
              @param self
        """
        # creation using one argument + conversion to long
        number = arithmetic.RationalNumber( 2 )
        assert( number.get_dividend() == 2 and 
                isinstance( number.get_dividend(), int ) )
        assert( number.get_divisor() == 1 and 
                isinstance( number.get_dividend(), int ) )
        # creation using two arguments + test normalization
        number = arithmetic.RationalNumber( 2, -4 )
        assert( number.get_dividend() == -1 )
        assert( number.get_divisor() == 2 )
        
        # Test for divide by zero
        error = False
        try:
            number = arithmetic.RationalNumber( 2, 0 )
        except ArithmeticError:
            error = True
        assert( error )
        
        # Test if assertion works
        error = False
        try:
            number = arithmetic.RationalNumber( 2.0 )
        except AssertionError:
            error = True
        assert( error )
        
    def test_casting( self ):
        """! @brief Test the casting the Type arithmetic.RationalNumber.
              @param self
        """
        number = arithmetic.RationalNumber( 4, 3 )
        intval = int( number )
        assert( intval == 1 and isinstance( intval, int ) )
        longval = int( number )
        assert( longval == 1 and isinstance( longval, int ) )
        floatval = float( number )
        assert( floatval == 4.0 / 3.0 )
        complexval = complex( number )
        assert( complexval.real == 4.0 / 3.0 and complexval.imag == 0.0 )
        number = arithmetic.RationalNumber( 2, 1 )
        assert( number.is_integer() )
        
    def test_add( self ):
        """! @brief Test adding instances of the Type arithmetic.RationalNumber.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        secondVal = arithmetic.RationalNumber( 5, 10 ) # 1/2
        
        # addition of RationalNumbers
        result = firstVal + secondVal
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 11 )
        assert( result.get_divisor()  == 6 )
        # assert that arguments still untouched
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        assert( secondVal.get_dividend() == 1 )
        assert( secondVal.get_divisor() == 2 )
        
        # addition of integer
        result = firstVal + 1
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 7 )
        assert( result.get_divisor()  == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # addition of long
        result = firstVal + 1
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 7 )
        assert( result.get_divisor()  == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # addition of float
        result = firstVal + 1.0
        assert( isinstance( result, float ) )
        assert( abs( result - 7.0 / 3.0 ) < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # addition of complex
        result = firstVal + complex( 1.0, 2.0 )
        assert( isinstance( result, complex ) )
        assert( abs( result.real - 7.0 / 3.0 ) < 1e-5 and result.imag == 2.0 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
    def test_sub( self ):
        """! @brief Test substracting instances of the Type arithmetic.RationalNumber.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        secondVal = arithmetic.RationalNumber( 5, 10 ) # 1/2
        
        # substraction of RationalNumbers
        result = firstVal - secondVal
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 5 )
        assert( result.get_divisor()  == 6 )
        # assert that arguments still untouched
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        assert( secondVal.get_dividend() == 1 )
        assert( secondVal.get_divisor() == 2 )
        
        # substraction of integer
        result = firstVal - 1
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 1 )
        assert( result.get_divisor()  == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # substraction of long
        result = firstVal - 1
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 1 )
        assert( result.get_divisor()  == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # substraction of float
        result = firstVal - 1.0
        assert( isinstance( result, float ) )
        assert( abs( result - 1.0 / 3.0 ) < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # substraction of complex
        result = firstVal - complex( 1.0, 2.0 )
        assert( isinstance( result, complex ) )
        assert( abs( result.real - 1.0 / 3.0 ) < 1e-5 and result.imag == -2.0 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
    def test_mul( self ):
        """! @brief Test multiplying instances of the Type arithmetic.RationalNumber.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        secondVal = arithmetic.RationalNumber( 5, 10 ) # 1/2
        
        # multiplication of RationalNumbers
        result = firstVal * secondVal
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 2 )
        assert( result.get_divisor()  == 3 )
        # assert that arguments still untouched
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        assert( secondVal.get_dividend() == 1 )
        assert( secondVal.get_divisor() == 2 )
        
        # multiplication of integer
        result = firstVal * 3
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor()  == 1 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # multiplication of long
        result = firstVal * 3
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor()  == 1 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # multiplication of float
        result = firstVal * 3.0
        assert( isinstance( result, float ) )
        assert( abs( result - 4.0 ) < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # multiplication of complex
        result = firstVal * complex( 3.0, 2.0 )
        assert( isinstance( result, complex ) )
        assert( abs( result.real - 4.0 ) < 1e-5 and 
                abs( result.imag - 8.0/3.0 ) < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
    
    def test_pow( self ):
        """! @brief Test powers of  instances of the Type arithmetic.RationalNumber.
              @param self
        """
        number = arithmetic.RationalNumber( 1, 2 )
        result = number ** 2
        assert( result.get_dividend() == 1 )
        assert( result.get_divisor() == 4 )
        assert( number.get_dividend() == 1 )
        assert( number.get_divisor() == 2 )
        
        number2 = arithmetic.RationalNumber( 0, 10 )
        assert( number2.get_dividend() == 0 )
        assert( number2.get_divisor() == 1 )
        
        result = number2 ** 3
        assert( result.get_dividend() == 0 )
        assert( result.get_divisor() == 1 )
        
        result = number ** 0
        assert( result.get_dividend() == 1 )
        assert( result.get_divisor() == 1 )
        
        # test negative power
        result = number ** ( -2 )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor() == 1 )
        
        # test rational integer powers
        result = number ** arithmetic.RationalNumber( 2, 1 )
        assert( result.get_dividend() == 1 )
        assert( result.get_divisor() == 4 )
        
        # test for floating point powers
        result = number ** 2.0
        assert( isinstance( result, float ) )
        
        # test rpow
        value = 10
        number = arithmetic.RationalNumber( 2, 1 )
        result = value ** number
        assert( result == 100 )
        
        value = 10.0
        number = arithmetic.RationalNumber( 2, 1 )
        result = value ** number
        assert( abs( result - 100.0 ) < 1e-5 )
        
    def test_div( self ):
        """! @brief Test dividing instances of the Type arithmetic.RationalNumber.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        secondVal = arithmetic.RationalNumber( 5, 10 ) # 1/2
        
        # division of RationalNumbers
        result = firstVal / secondVal
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 8 )
        assert( result.get_divisor()  == 3 )
        # assert that arguments still untouched
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        assert( secondVal.get_dividend() == 1 )
        assert( secondVal.get_divisor() == 2 )
        
        # division of integer
        result = firstVal / 3
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor()  == 9 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # division of long
        result = firstVal / 3
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor()  == 9 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # division of float
        result = firstVal / 3.0
        assert( isinstance( result, float ) )
        assert( abs( result - 4.0/9.0 ) < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )        
        
        # division of complex
        result = firstVal / complex( 3.0, 2.0 )
        assert( isinstance( result, complex ) )
        assert( ( abs( result.real - 4.0/13.0 ) < 1e-5 ) and 
                ( abs( result.imag + 8.0/39.0 ) < 1e-5 ) )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )

        #divide by negative numbers
        # division of RationalNumbers
        secondVal = arithmetic.RationalNumber( -5, 10 ) # 1/2
        result = firstVal / secondVal
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == -8 )
        assert( result.get_divisor()  == 3 )
        # assert that arguments still untouched
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        assert( secondVal.get_dividend() == -1 )
        assert( secondVal.get_divisor() == 2 )
        
        # division of integer
        result = firstVal / -3
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == -4 )
        assert( result.get_divisor()  == 9 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # division of long
        result = firstVal / -3
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result.get_dividend() == -4 )
        assert( result.get_divisor()  == 9 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # division of float
        result = firstVal / -3.0
        assert( isinstance( result, float ) )
        assert( result + 4.0/9.0 < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # division of complex
        result = firstVal / complex( -3.0, 2.0 )
        assert( isinstance( result, complex ) )
        assert( abs( result.real + 4.0/13.0 ) < 1e-5 and 
                abs( result.imag + 8.0/39.0 ) < 1e-5 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # test for divide by zero
        error = 0
        try:
            result = firstVal / 0
        except ArithmeticError:
            error = 1
        assert( error )
        
        # test for divide by zero (float)
        error = 0
        try:
            result = firstVal / 0.0
        except ArithmeticError:
            error = 1
        assert( error )
        
    def test_neg( self ):
        """! @brief Test negating instances of the Type arithmetic.RationalNumber.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        result   = -firstVal
        assert( result.get_dividend() == -4 )
        assert( result.get_divisor() == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # test with zero
        firstVal = arithmetic.RationalNumber( 0, 3 )   # 1/1/3
        result   = -firstVal
        assert( result.get_dividend() == 0 )
        assert( firstVal.get_divisor() == 1 )
        assert( firstVal.get_dividend() == 0 )
        assert( firstVal.get_divisor() == 1 )
        
    def test_pos( self ):
        """! @brief Test cloning instances of the Type arithmetic.RationalNumber.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        result   = +firstVal
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor() == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # test with zero
        firstVal = arithmetic.RationalNumber( 0, 3 )   # 1/1/3
        result   = +firstVal
        assert( result.get_dividend() == 0 )
        assert( firstVal.get_divisor() == 1 )
        assert( firstVal.get_dividend() == 0 )
        assert( firstVal.get_divisor() == 1 )
        
    def test_abs( self ):
        """! @brief Test getting the absolute value of rational numbers.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        secondVal = arithmetic.RationalNumber( -4, 3 )   # 1/1/3
        
        result = abs( firstVal )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor() == 3 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        result = abs( secondVal )
        assert( result.get_dividend() == 4 )
        assert( result.get_divisor() == 3 )
        assert( secondVal.get_dividend() == -4 )
        assert( secondVal.get_divisor() == 3 )
       
    def test_invert( self ):
        """! @brief Test inverting instances of the Type arithmetic.RationalNumber.
              @param self 
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        result   = ~firstVal
        assert( result.get_dividend() == 3 )
        assert( result.get_divisor() == 4 )
        assert( firstVal.get_dividend() == 4 )
        assert( firstVal.get_divisor() == 3 )
        
        # test for divide by zero
        secondVal = arithmetic.RationalNumber( 0, 3 )   # 1/1/3
        assert( secondVal.get_dividend() == 0 )
        assert( secondVal.get_divisor() == 1 )
        error = 0
        try:
            result = ~secondVal
        except ArithmeticError:
            error = 1
        assert( error )
        
    def test_comparisions( self ):
        """! @brief Test the comparision functions of rational numbers.
              @param self
        """
        firstVal = arithmetic.RationalNumber( 4, 3 )   # 1/1/3
        secondVal = arithmetic.RationalNumber( 5, 10 ) # 1/2
        assert( firstVal != secondVal ) # __eq__
        assert( firstVal == arithmetic.RationalNumber( 4, 3 ) ) # __eq__
        assert( secondVal == arithmetic.RationalNumber( 1, 2 ) ) # __eq__
        assert( not ( firstVal == secondVal ) ) # __ne__
        assert( not ( firstVal < secondVal ) ) # __lt__
        assert( secondVal < firstVal ) # __lt__
        assert( not ( firstVal <= secondVal ) ) # __le__
        assert( secondVal <= firstVal ) # __le__
        assert( firstVal <= arithmetic.RationalNumber( 4, 3 ) ) # __le__
        assert( secondVal <= arithmetic.RationalNumber( 1, 2 ) ) # __le__
        assert( not ( secondVal > firstVal ) ) # __gt__
        assert( firstVal > secondVal ) # __gt__
        assert( not ( secondVal >= firstVal ) ) # __gt__
        assert( firstVal >= secondVal ) # __gt__
        assert( firstVal >= arithmetic.RationalNumber( 4, 3 ) ) # __ge__
        assert( secondVal >= arithmetic.RationalNumber( 1, 2 ) ) # __ge__
        # test cmp
        #assert( cmp( firstVal, secondVal ) > 0 )
        #assert( cmp( secondVal, firstVal ) < 0 )
        #assert( cmp( firstVal, firstVal ) == 0 )
        # test nonzero
        assert( firstVal )
        assert( not arithmetic.RationalNumber( 0, 3 ) )
        
        # test against float
        secondVal = 0.5 # 1/2
        assert( firstVal != secondVal ) # __eq__
        assert( firstVal == arithmetic.RationalNumber( 4, 3 ) ) # __eq__
        assert( secondVal == arithmetic.RationalNumber( 1, 2 ) ) # __eq__
        assert( not ( firstVal == secondVal ) ) # __ne__
        assert( not ( firstVal < secondVal ) ) # __lt__
        assert( secondVal < firstVal ) # __lt__
        assert( not ( firstVal <= secondVal ) ) # __le__
        assert( secondVal <= firstVal ) # __le__
        assert( firstVal <= arithmetic.RationalNumber( 4, 3 ) ) # __le__
        assert( secondVal <= arithmetic.RationalNumber( 1, 2 ) ) # __le__
        assert( not ( secondVal > firstVal ) ) # __gt__
        assert( firstVal > secondVal ) # __gt__
        assert( not ( secondVal >= firstVal ) ) # __gt__
        assert( firstVal >= secondVal ) # __gt__
        assert( firstVal >= arithmetic.RationalNumber( 4, 3 ) ) # __ge__
        assert( secondVal >= arithmetic.RationalNumber( 1, 2 ) ) # __ge__
        # test cmp
        #assert( cmp( firstVal, secondVal ) > 0 )
        #assert( cmp( secondVal, firstVal ) < 0 )
        #assert( cmp( firstVal, firstVal ) == 0 )
        
        # test against long
        secondVal = 1 # 1/2
        assert( firstVal != secondVal ) # __eq__
        assert( firstVal == arithmetic.RationalNumber( 4, 3 ) ) # __eq__
        assert( secondVal == arithmetic.RationalNumber( 1, 1 ) ) # __eq__
        assert( not ( firstVal == secondVal ) ) # __ne__
        assert( not ( firstVal < secondVal ) ) # __lt__
        assert( secondVal < firstVal ) # __lt__
        assert( not ( firstVal <= secondVal ) ) # __le__
        assert( secondVal <= firstVal ) # __le__
        assert( firstVal <= arithmetic.RationalNumber( 4, 3 ) ) # __le__
        assert( secondVal <= 1 ) # __le__
        assert( not ( secondVal > firstVal ) ) # __gt__
        assert( firstVal > secondVal ) # __gt__
        assert( not ( secondVal >= firstVal ) ) # __gt__
        assert( firstVal >= secondVal ) # __gt__
        assert( firstVal >= arithmetic.RationalNumber( 4, 3 ) ) # __ge__
        assert( secondVal >= arithmetic.RationalNumber( 1, 2 ) ) # __ge__
        # test cmp
        # assert( cmp( firstVal, secondVal ) > 0 )
        # assert( cmp( secondVal, firstVal ) < 0 )
        # assert( cmp( firstVal, firstVal ) == 0 )
        
    def test_right_ops( self ):
        """! @brief Test right-operations of the Type arithmetic.RationalNumber.
               Test the operations where an unknown numeric type is
              a left argument of the instance of rational number.
              @attention This test is not as strict as the individual tests for
                         the operations that require a left argument. This is
                         because the functions tested here rely on them.
              @param self
        """
        assert( abs( 2.0 + arithmetic.RationalNumber( 1, 2 ) - 5.0/2.0 ) 
                < 1e-5 )
        assert( 2 + arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 5, 2 ) )
        assert( 2 + arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 5, 2 ) )
        assert( abs( complex( 2, 1 ) + arithmetic.RationalNumber( 1, 2 ) - 
                complex( 5.0/2.0, 1 ) ) < 1e-5 )
        
        assert( abs( 2.0 - arithmetic.RationalNumber( 1, 2 ) - 3.0/2.0 ) 
                < 1e-5 )
        assert( 2 - arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 3, 2 ) )
        assert( 2 - arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 3, 2 ) )
        assert( abs( complex( 2, 1 ) - arithmetic.RationalNumber( 1, 2 ) - 
                complex( 3.0/2.0, 1 ) ) < 1e-5 )
        
        assert( abs( 2.0 * arithmetic.RationalNumber( 1, 2 ) - 1.0 ) < 1e-5 )
        assert( 2 * arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 1, 1 ) )
        assert( 2 * arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 1, 1 ) )
        assert( abs( complex( 2, 1 ) * arithmetic.RationalNumber( 1, 2 ) - 
                complex( 1.0, 0.5 ) ) < 1e-5 )
        
        assert( abs( 2.0 / arithmetic.RationalNumber( 1, 2 ) - 4.0 ) < 1e-5 )
        assert( 2 / arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 4, 1 ) )
        assert( 2 / arithmetic.RationalNumber( 1, 2 ) == 
                arithmetic.RationalNumber( 4, 1 ) )
        assert( abs( complex( 2, 1 ) / arithmetic.RationalNumber( 1, 2 ) - 
                complex( 4, 2 ) ) < 1e-5 )
        
    def test_value_of( self ):
        """! @brief Test the value_of proxy of the Type arithmetic.RationalNumber.
              @param self
        """
        # test int
        num = arithmetic.RationalNumber.value_of( 1 )
        assert( isinstance( num, arithmetic.RationalNumber ) )
        assert( num == 1 )
        # test float
        error = 0
        try:
            num = arithmetic.RationalNumber.value_of( 1.1 )
        except TypeError:
            error = 1
        assert( error==1 )
        
        # test complex
        error = 0
        try:
            num = arithmetic.RationalNumber.value_of( complex( 1, 2 ) )
        except TypeError:
            error = 1
        assert( error==1 )
        # test RationalNumber
        num = arithmetic.RationalNumber.value_of( 
                                            arithmetic.RationalNumber( 1, 2 ) )
        assert( isinstance( num, arithmetic.RationalNumber ) )
        assert( num == arithmetic.RationalNumber( 1, 2 ) )
        
    def test_complex_to_matrix(self):
        """! @brief Test the conversion from complex numbers to a matrix.
        """
        c = complex(1,2)
        result = arithmetic.complex_to_matrix(c)
        assert(isinstance(result, numpy.matrix))
        assert(result[0,0] == c.real)
        assert(result[0,1] == -c.imag)
        assert(result[1,0] == c.imag)
        assert(result[1,1] == c.real)
        assert(result.shape == (2,2))
        
    def test_Numpy( self ):
        """! @brief Test the integration of the Type arithmetic.RationalNumbers in NumPy.
        """
        
        num1 = arithmetic.rational( 1, 2 )
        num2 = arithmetic.rational( 1, 4 )
        num3 = arithmetic.rational( 5, 2 )
        
        assert( numpy.greater( num1, num2 ) )
        assert( not numpy.greater( num2, num1 ) )
        
        assert( not numpy.equal( num1, num2 ) )
        assert( numpy.equal( num1, num1 ) )
        
        assert( numpy.not_equal( num1, num2 ) )
        assert( not numpy.not_equal( num1, num1 ) )
        
        assert( numpy.greater_equal( num1, num2 ) )
        assert( not numpy.greater_equal( num2, num1 ) )
        assert( numpy.greater_equal( num1, num1 ) )
        
        assert( not numpy.less( num1, num2 ) )
        assert( numpy.less( num2, num1 ) )
        
        result = arithmetic.rational( 3, 4 )
        assert( numpy.add( num1, num2 ) == result )
        assert( numpy.add( 1.0, num1 ) == 1.5 )
        
        result = arithmetic.rational( 1, 4 )
        assert( numpy.subtract( num1, num2 ) == result )
        assert( numpy.subtract( 1.0, num1 ) == 0.5 )
        
        result = arithmetic.rational( 1, 8 )
        assert( numpy.multiply( num1, num2 ) == result )
        assert( numpy.multiply( 1.0, num1 ) == num1 )
        
        result = 2
        assert( numpy.divide( num1, num2 ) == result )
        assert( numpy.divide( 1.0, num1 ) == 2.0 )
        
        error = 0
        try:
            numpy.remainder( num1, num2 )
        except TypeError:
            error = 1
        assert( error )
        
        assert( abs( numpy.arccos( num1 ) - numpy.arccos( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.arccosh( num3 ) - numpy.arccosh( 2.5 ) ) < 1e-4 )
        
        assert( abs( numpy.arcsin( num1 ) - numpy.arcsin( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.arcsinh( num3 ) - numpy.arcsinh( 2.5 ) ) < 1e-4 )
        
        assert( abs( numpy.arctan( num1 ) - numpy.arctan( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.arctanh( num1 ) - numpy.arctanh( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.cos( num1 ) - numpy.cos( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.cosh( num1 ) - numpy.cosh( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.tan( num1 ) - numpy.tan( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.tanh( num1 ) - numpy.tanh( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.log10( num1 ) - numpy.log10( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.sin( num1 ) - numpy.sin( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.sinh( num1 ) - numpy.sinh( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.sqrt( num1 ) - numpy.sqrt( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.absolute( num1 ) - numpy.absolute( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.absolute( -num1 ) - numpy.absolute( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.fabs( num1 ) - numpy.fabs( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.floor( num1 ) - numpy.floor( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.ceil( num1 ) - numpy.ceil( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.fmod( num1, 10 ) - numpy.fmod( 0.5, 10 ) ) < 1e-4 )
        
        error = 0
        try:
            numpy.fmod( [10], num1 )
        except AttributeError:
            error = 1
        assert( error )
        
        assert( abs( numpy.exp( num1 ) - numpy.exp( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.log( num1 ) - numpy.log( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.log2( num1 ) - numpy.log2( 0.5 ) ) < 1e-4 )
        
        assert( abs( numpy.maximum( num1, num2 ) 
                - numpy.maximum( 0.5, 0.25 ) ) < 1e-4 )
                
        assert( abs( numpy.minimum( num1, num2 ) 
                - numpy.minimum( 0.5, 0.25 ) ) < 1e-4 )
                
        assert( abs( numpy.conjugate( num1 ) - 0.5 ) < 1e-4 )
        
class TestOperators( unittest.TestCase ):
    """! @brief       Test the unit conversion operators.
    """
    def TEST_CONV( operator, invalue, outvalue, outtype ):
        """! @brief Test an Operator with an integer/long input and an
              expected output value. Also make sure, that the output-type
              is correct.
        """
        result = operator.convert( invalue )
        assert( isinstance( result, outtype ) )
        assert( result == outvalue )
    TEST_CONV = staticmethod( TEST_CONV )
    
    def TEST_CONV_APPX( operator, invalue, outvalue, outtype, confidence ):
        """! @brief Test an Operator with an integer/long input and an
              expected output value. Also make sure, that the output-type
              is correct.
        """
        result = operator.convert( invalue )
        assert( isinstance( result, outtype ) )
        assert( abs( result - outvalue ) < confidence )
    TEST_CONV_APPX = staticmethod( TEST_CONV_APPX )
    
    def test_log_exp_operator( self ):
        """! @brief Test the exponential and logarithmic unit operators.
              @param self
        """
        base      = 10
        # basic operation
        log10     = operators.LogOperator( base )
        assert( abs( log10.get_base() - base ) < 1e-5 )
        assert( abs( log10.convert( 10 ) - 1.0 ) < 1e-5 )
        # verify using logarithmic rules
        # 1. product rule
        result = log10.convert( 10 ) + log10.convert( 20 )
        assert( abs( result - log10.convert( 10*20 ) ) < 1e-5 )
        # 2. quotient rule
        result = log10.convert( arithmetic.RationalNumber( 1, 2 ) )
        assert( abs( result - log10.convert( 1 ) + log10.convert( 2 ) ) 
                < 1e-5 )
        # 3. exponent rule
        assert( abs( log10.convert( 2**3 ) - 3*log10.convert( 2 ) ) < 1e-5 )
        assert( not log10.is_linear() )
        
        exp10     = ~log10
        assert( isinstance( exp10, operators._ExpOperator ) )
        assert( abs( exp10.get_exponent() - base ) < 1e-5 )
        assert( abs( exp10.convert( 1 ) - 10.0 ) < 1e-5 )
        assert( abs( exp10.convert( 2 ) * 
                exp10.convert( 3 )-exp10.convert( 2+3 ) ) < 1e-5 )
        assert( not exp10.is_linear() )
        # Test serialization
        log10copy = operators.LogOperator( base )
        sanityOp  = operators.AddOperator( 10 )
        test_serialization( log10, log10copy, sanityOp, 
                                         operators.LogOperator )
        # same of exp
        exp10copy = ~log10copy
        test_serialization( exp10, exp10copy, sanityOp, 
                                         operators._ExpOperator )
    
    def test_add_operator( self ):
        """! @brief Test the unit add operator.
              @param self
        """
        add = operators.AddOperator( arithmetic.RationalNumber( 1, 2 ) )
        result = add.get_offset()
        # This operator should preserve the type
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result == arithmetic.RationalNumber( 1, 2 ) )
        result = add.convert( 10 )
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result == arithmetic.RationalNumber( 21, 2 ) )
        min = ~add
        result = min.convert( 10 )
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result == arithmetic.RationalNumber( 19, 2 ) )
        # Ok, works for rational number and now test an int.
        add = operators.AddOperator( 10 )
        assert( add.convert( 10 ) == 20 )
        min = ~add
        assert( min.convert( 10 ) == 0 )
        # test serialization
        copy = operators.AddOperator( 10 )
        sanity = operators.AddOperator( arithmetic.RationalNumber( 1, 4 ) )
        test_serialization( add, copy, sanity, 
                                         operators.AddOperator )
    
    def test_multiply_operator( self ):
        """! @brief Test the unit multiply operator.
              @param self
        """
        mul = operators.MultiplyOperator( arithmetic.RationalNumber( 1, 2 ) )
        result = mul.get_factor()
        # This operator should preserve the type
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result == arithmetic.RationalNumber( 1, 2 ) )
        result = mul.convert( 10 )
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result == arithmetic.RationalNumber( 5, 1 ) )
        div = ~mul
        result = div.convert( 10 )
        assert( isinstance( result, arithmetic.RationalNumber ) )
        assert( result == arithmetic.RationalNumber( 20, 1 ) )
        # Ok, works for rational number and now test an int.
        mul = operators.MultiplyOperator( 10 )
        assert( mul.convert( 10 ) == 100 )
        div = ~mul
        assert( div.convert( 10 ) == 1 )
        
        copy = operators.MultiplyOperator( 10 )
        sanity = operators.MultiplyOperator( 
                           arithmetic.RationalNumber( 1, 4 ) )
        test_serialization( mul, copy, sanity, 
                                         operators.MultiplyOperator )
    
    def test_identity( self ):
        """! @brief Test the global identity variable (for unit converters).
              @param self
        """
        id = operators.IDENTITY
        # test conversion
        TestOperators.TEST_CONV( id, 1, 1, int )
        TestOperators.TEST_CONV( id, 1, 1, int )
        TestOperators.TEST_CONV( id, arithmetic.RationalNumber( 1, 2 ), 
                                arithmetic.RationalNumber( 1, 2 ), 
                                arithmetic.RationalNumber )
        TestOperators.TEST_CONV_APPX( id, 1.0, 1.0, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( id, complex( 1.0, 1.0 ), 
                                    complex( 1.0, 1.0 ), complex, 1e-5 )
        
        # test concatenations with inverse
        addInt = operators.AddOperator( 10 )
        addRat = operators.AddOperator( arithmetic.RationalNumber( 10, 1 ) )
        addFlt = operators.AddOperator( 10.0 )

        assert( addInt*~addInt == operators.IDENTITY )
        assert( addInt*~addRat == operators.IDENTITY )
        assert( addInt*~addFlt == operators.IDENTITY  )
        mulInt = operators.MultiplyOperator( 10 )
        mulRat = operators.MultiplyOperator( 
                           arithmetic.RationalNumber( 10, 1 ) )
        mulFlt = operators.MultiplyOperator( 10.0 )
        assert( mulInt*~mulInt == operators.IDENTITY )
        assert( mulInt*~mulRat == operators.IDENTITY )
        assert( mulFlt*~mulInt == operators.IDENTITY )
        
        # test concatenation with IDENTITY
        # right multiplication
        assert( addInt * operators.IDENTITY == addInt )
        # left multiplication
        assert( operators.IDENTITY * addInt == addInt )
        # test serialization
        copy = operators.Identity()
        sanity = operators.MultiplyOperator( 
                           arithmetic.RationalNumber( 1, 4 ) )
        test_serialization( operators.IDENTITY, copy, sanity, 
                                         operators.Identity )
        
    def test_compound_operations( self ):
        """! @brief Test all permuations of binary operations on unit operators.
              @param self
        """
        #define some operators
        addOp = operators.AddOperator( 5.25 )
        mulOp = operators.MultiplyOperator( arithmetic.RationalNumber( 1, 2 ) )
        logOp = operators.LogOperator( 10 )
        # test all combinations of two operators
        # Add first, then multiply
        mulAdd = mulOp * addOp 
        # Multiply first, then add
        addMul = addOp * mulOp
        # Add First then take the logarithm
        logAdd = logOp * addOp
        # Take the logarithm, then add
        addLog = addOp * logOp
        # Take the logartihm, then multiply
        mulLog = mulOp * logOp
        # Multiply first, then take the logarithm
        logMul = logOp * mulOp
        # test for optimization of operators
        addAdd = addOp * addOp
        mulMul = mulOp * mulOp
        logLog = logOp * logOp
        #check linearity
        assert( not mulAdd.is_linear() )
        assert( not addMul.is_linear() )
        assert( not logAdd.is_linear() )
        assert( not addLog.is_linear() )
        assert( not mulLog.is_linear() )
        assert( not logMul.is_linear() )
        assert( not addAdd.is_linear() )
        assert( mulMul.is_linear() )
        assert( not logLog.is_linear() )
        
        #Test the optimizations first
        assert( isinstance( addAdd, operators.AddOperator ) )
        assert( isinstance( mulMul, operators.MultiplyOperator ) )
        # The logOperator cannot be optimized that way
        assert( isinstance( logLog, operators.CompoundOperator ) )
        
        # addAdd
        assert( abs( addAdd.get_offset() - 10.5 ) < 1e-5 )
        TestOperators.TEST_CONV_APPX( addAdd, 10, 20.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addAdd, 10.0, 20.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addAdd, complex( 10.0, 1.0 ), 
                                   complex( 20.5, 1.0 ), complex, 
                                   1e-5 )
        TestOperators.TEST_CONV_APPX( addAdd, 
                                    arithmetic.RationalNumber( 1, 2 ), 
                                    11.0, float, 1e-5 )
        
        # mulMul
        assert( mulMul.get_factor() == arithmetic.RationalNumber( 1, 4 ) )
        TestOperators.TEST_CONV( mulMul, 10, 
                                arithmetic.RationalNumber( 5, 2 ), 
                                arithmetic.RationalNumber )
        TestOperators.TEST_CONV_APPX( mulMul, 10.0, 2.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( mulMul, complex( 10.0, 1.0 ), 
                                    complex( 2.5, 0.25 ), complex, 
                                    1e-5 )
        TestOperators.TEST_CONV( mulMul, 
                                arithmetic.RationalNumber( 1, 2 ), 
                                arithmetic.RationalNumber( 1, 8 ), 
                                arithmetic.RationalNumber )
        # logLog
        TestOperators.TEST_CONV_APPX( logLog, 100, 0.3010299957, 
                                    float, 1e-5 )
        TestOperators.TEST_CONV_APPX( logLog, 100.0, 0.3010299957, 
                                    float, 1e-5 )
        TestOperators.TEST_CONV_APPX( logLog, 
                                    arithmetic.RationalNumber( 100, 1 ), 
                                    0.3010299957, 
                                    float, 
                                    1e-5 )

        # test that log not defined for complex
        error = 0
        try:
            result = logLog.convert( complex( 100.0, 1.0 ) )
        except TypeError:
            error = 1
        assert( error )
        
        # mulAdd
        TestOperators.TEST_CONV_APPX( mulAdd, 10, 7.625, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( mulAdd, 10.0, 7.625, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( mulAdd, 
                                    arithmetic.RationalNumber( 10, 1 ), 
                                    7.625, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( mulAdd, complex( 10, 2 ), 
                                    complex( 7.625, 1 ), complex, 1e-5 )
        
        # addMul
        TestOperators.TEST_CONV_APPX( addMul, 10, 10.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addMul, 10.0, 10.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addMul, 
                                    arithmetic.RationalNumber( 10, 1 ), 
                                    10.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addMul, complex( 10, 2 ), 
                                    complex( 10.25, 1 ), complex, 1e-5 )
                                    
        # addLog
        TestOperators.TEST_CONV_APPX( addLog, 100, 7.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addLog, 100.0, 7.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( addLog, 
                                    arithmetic.RationalNumber( 100, 1 ), 
                                    7.25, float, 1e-5 )
        # Test for type error (complex not defined)
        error = 0
        try:
            result = addLog.convert( complex( 100.0, 1.0 ) )
        except TypeError:
            error = 1
        assert( error )
        
        # logAdd
        TestOperators.TEST_CONV_APPX( logAdd, 10, 1.183269844, 
                                    float, 1e-5 )
        TestOperators.TEST_CONV_APPX( logAdd, 10.0, 1.183269844, 
                                    float, 1e-5 )
        TestOperators.TEST_CONV_APPX( logAdd, 
                                    arithmetic.RationalNumber( 10, 1 ), 
                                    1.183269844, float, 1e-5 )
        # Test for type error (complex not defined)
        error = 0
        try:
            result = logAdd.convert( complex( 100.0, 1.0 ) )
        except TypeError:
            error = 1
        assert( error )
        
        # mulLog
        TestOperators.TEST_CONV_APPX( mulLog, 100, 1.0, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( mulLog, 100.0, 1.0, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( mulLog, 
                                    arithmetic.RationalNumber( 100, 1 ), 
                                    1.0, float, 1e-5 )
        # Test for type error (complex not defined)
        error = 0
        try:
            result = mulLog.convert( complex( 100.0, 1.0 ) )
        except TypeError:
            error = 1
        assert( error )
        
        # logMul
        TestOperators.TEST_CONV_APPX( logMul, 200, 2.0, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( logMul, 200.0, 2.0, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( logMul, 
                                    arithmetic.RationalNumber( 200, 1 ), 
                                    2.0, float, 1e-5 )
        # Test for type error (complex not defined)
        error = 0
        try:
            result = logMul.convert( complex( 100.0, 1.0 ) )
        except TypeError:
            error = 1
        assert( error )
        
        #Test the inversions
        invMulAdd = ~mulAdd # ok
        invAddMul = ~addMul # ok
        invLogAdd = ~logAdd # ok
        invAddLog = ~addLog # ok
        invMulLog = ~mulLog # ok
        invLogMul = ~logMul # ok
        invAddAdd = ~addAdd # ok
        invLogLog = ~logLog # ok
        invMulMul = ~mulMul # ok
        
        #check linearity
        assert( not invMulAdd.is_linear() )
        assert( not invAddMul.is_linear() )
        assert( not invLogAdd.is_linear() )
        assert( not invAddLog.is_linear() )
        assert( not invMulLog.is_linear() )
        assert( not invLogMul.is_linear() )
        assert( not invAddAdd.is_linear() )
        assert( not invLogLog.is_linear() )
        assert( invMulMul.is_linear() )

        # invAddAdd
        TestOperators.TEST_CONV_APPX( invAddAdd, 10, -0.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invAddAdd, 10.0, -0.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invAddAdd, 
                                    arithmetic.RationalNumber( 10, 1 ), 
                                    -0.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invAddAdd, complex( 10, 1 ), 
                                    complex( -0.5, 1 ), complex, 1e-5 )
        
        TestOperators.TEST_CONV( invMulMul, 10, 40, arithmetic.RationalNumber )
        TestOperators.TEST_CONV_APPX( invMulMul, 10.0, 40, float, 1e-5 )
        TestOperators.TEST_CONV( invMulMul, 
                                arithmetic.RationalNumber( 10, 1 ), 
                                arithmetic.RationalNumber( 40, 1 ), 
                                arithmetic.RationalNumber )
        TestOperators.TEST_CONV_APPX( invMulMul, 
                                    complex( 10.0, 1.0 ), 
                                    complex( 40.0, 4.0 ), 
                                    complex, 1e-5 )
        
        # invLogLog !!! accuracy is quite limited, therefore 1e-4
        TestOperators.TEST_CONV_APPX( invLogLog, 1, 1e10, float, 1e-4 )
        TestOperators.TEST_CONV_APPX( invLogLog, 1.0, 1e10, float, 1e-4 )
        TestOperators.TEST_CONV_APPX( invLogLog, 
                                    arithmetic.RationalNumber( 1, 1 ), 
                                    1e10, float, 1e-4 )
        # Test for type error (complex not defined)
        error = 0
        try:
            result = invLogLog.convert( complex( 1.0, 1.0 ) )
        except TypeError:
            error = 1
        assert( error )
        
        # invMulAdd
        TestOperators.TEST_CONV_APPX( invMulAdd, 2, -1.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invMulAdd, 2.0, -1.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invMulAdd, 
                                    arithmetic.RationalNumber( 2, 1 ), 
                                    -1.25, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invMulAdd, complex( 2.0, 1.0 ), 
                                    complex( -1.25, 2.0 ), complex, 1e-5 )
                                    
        # invAddMul
        TestOperators.TEST_CONV_APPX( invAddMul, 6, 1.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invAddMul, 6.0, 1.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invAddMul, 
                                    arithmetic.RationalNumber( 6, 1 ), 
                                    1.5, float, 1e-5 )
        TestOperators.TEST_CONV_APPX( invAddMul, complex( 6.0, 1.0 ), 
                                    complex( 1.5, 2 ), complex, 1e-5 )
        # invAddLog
        TestOperators.TEST_CONV_APPX( invAddLog, 6, 5.623413252, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invAddLog, 6.25, 10.0, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invAddLog, 
                                    arithmetic.RationalNumber( 6, 1 ), 
                                    5.623413252, float, 1e-5 )
        # invLogAdd
        TestOperators.TEST_CONV_APPX( invLogAdd, 1, 4.75, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invLogAdd, 1.0, 4.75, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invLogAdd, 
                                    arithmetic.RationalNumber( 1, 1 ), 
                                    4.75, float, 1e-5 )

        # invMulLog
        TestOperators.TEST_CONV_APPX( invMulLog, 2, 1e4, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invMulLog, 2.0, 1e4, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invMulLog, 
                                    arithmetic.RationalNumber( 2, 1 ), 
                                    1e4, float, 1e-5 )
        # invLogMul
        TestOperators.TEST_CONV_APPX( invLogMul, 2, 200, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invLogMul, 2.0, 200, float, 
                                    1e-5 )
        TestOperators.TEST_CONV_APPX( invLogMul, 
                                    arithmetic.RationalNumber( 2, 1 ), 
                                    200, float, 1e-5 )
        # assertions for complex don't need to be tested anymore
        
        # Test Serialization
        copy = mulOp * addOp
        sanity = operators.MultiplyOperator( 
                           arithmetic.RationalNumber( 1, 4 ) )
        test_serialization( mulAdd, copy, logAdd, 
                                         operators.CompoundOperator )
        
class TestQuantity( unittest.TestCase ):
    """! @brief       This class provides the test cases for the quantities.
    """
    
    def setUp( self ):
        """! @brief This method initializes this test instance.
              @param self
        """
        self.newtons1 = quantities.Quantity( si.NEWTON, 2 )
        self.newtons2 = quantities.Quantity( si.NEWTON, 3.0 )
        self.otherStr = quantities.Quantity( si.KILOGRAM * si.METER / ( si.SECOND **2 ), arithmetic.RationalNumber( 4, 1 ) )
        self.other    = quantities.Quantity( si.KILOGRAM * si.METER / ( si.SECOND **2 ), arithmetic.RationalNumber( 4, 1 ) )
        self.incompat = quantities.Quantity( si.AMPERE, 10 )
        self.dimensionless = quantities.Quantity( units.ONE, 3)
    
    def test_init( self ):
        """! @brief Test the initialization of quantities.
              @param self
        """
        quantity = quantities.Quantity( si.NEWTON, 10 )
        
        assert( quantity.get_default_unit() == si.NEWTON )
        assert( quantity.get_value( si.NEWTON ) == 10 )
        assert( not quantity.is_dimensionless() )
        
        # check for strict checking
        error = 0
        try:
            quantity.get_value( si.KILOGRAM * si.METER / ( si.SECOND **2 ) )
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # same again, with no strict checks
        quantities.set_strict(False)
        quantity = quantities.Quantity( si.NEWTON, 10 )
        assert( quantity.get_default_unit() == si.NEWTON )
        assert( quantity.get_value( si.NEWTON ) == 10 )
        assert( quantity.get_value( si.KILOGRAM * si.METER / 
                ( si.SECOND **2 ) ) == 10 )
        quantities.set_strict(True)
        
        # creation using factory method
        quantity = quantities.Quantity.value_of( 10 )
        assert( quantity.get_default_unit() == units.ONE )
        assert( quantity.get_value( units.ONE ) == 10 )
        assert( quantity.is_dimensionless() )
        
        # check serializablility
        newtons1copy = +self.newtons1
        test_serialization( self.newtons1, newtons1copy, self.incompat, 
                           quantities.Quantity )
        
        # check is_dimensionless
        quantity = quantities.Quantity( si.RADIAN, 10 )
        assert( quantity.is_dimensionless() )
        quantity = quantities.Quantity( si.STERADIAN, 10 )
        assert( quantity.is_dimensionless() )
        

    def test_add( self ):       
        """! @brief Test adding quantities.
              @param self
        """
        # trivial
        result = self.newtons1 + self.newtons2
        assert( result.get_default_unit() == si.NEWTON )
        assert( abs( result.get_value( si.NEWTON ) - 5.0 ) < 10e-6 )
        
        # check for error
        error = 0
        try:
            result = self.newtons1 + self.otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with strict checks (now argument is strict)
        error = 0
        try:
            result = self.newtons2 + self.otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with weak checks
        quantities.set_strict(False)
        result = self.newtons2 + self.other
        assert( result.get_default_unit() == si.NEWTON )
        assert( abs( result.get_value( si.NEWTON ) - 7.0 ) < 1e-5 )
        assert( abs( result.get_value( si.KILOGRAM * si.METER / 
                ( si.SECOND **2 ) ) 
                - 7.0 ) < 1e-5 )
        quantities.set_strict(True)
        
        # check with numeric arguments
        result = self.dimensionless + 10
        assert( result.get_default_unit() == units.ONE )
        assert( result.get_value( units.ONE ) == 13 )
        
        error = 0
        try:
            result = self.newtons2 + 10
        except (qexceptions.ConversionException, AssertionError):
            error = 1
        assert( error==1 )
        
    
    def test_sub( self ):
        """! @brief Test subtracting quantities.
              @param self
        """
        # trivial
        result = self.newtons1 - self.newtons2
        assert( result.get_default_unit() == si.NEWTON )
        assert( abs( result.get_value( si.NEWTON ) + 1.0 ) < 10e-6 )
        
        # check for error
        error = 0
        try:
            result = self.newtons1 - self.otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with strict checks (now argument is strict)
        error = 0
        try:
            result = self.newtons2 - self.otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with weak checks
        quantities.set_strict(False)
        result = self.newtons2 - self.other
        assert( result.get_default_unit() == si.NEWTON )
        assert( abs( result.get_value( si.NEWTON ) + 1.0 ) < 1e-5 )
        assert( abs( result.get_value( si.KILOGRAM *\
                si.METER / ( si.SECOND **2 ) ) + 1.0 ) < 1e-5 )
        quantities.set_strict(True)
        
        # check with numeric arguments
        result = self.dimensionless - 10
        assert( result.get_default_unit() == units.ONE )
        assert( result.get_value( units.ONE ) == -7 )
        
        error = 0
        try:
            result = self.newtons2 - 10
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
    def test_mul( self ):
        """! @brief Test multiplying quantities.
              @param self
        """
        # trivial
        result = self.newtons1 * self.newtons2
        assert( result.get_default_unit() == si.NEWTON ** 2 )
        assert( abs( result.get_value( si.NEWTON ** 2 ) - 6.0 ) < 1e-5 )
        
        result = self.newtons2 * self.other
        unit   = si.NEWTON * si.KILOGRAM * si.METER /\
                 si.SECOND ** 2
        assert( result.get_default_unit() == unit ) 
        assert( abs( result.get_value( unit ) - 12.0 ) < 1e-5 )
        
        result = self.newtons2 * self.otherStr
        unit   = si.NEWTON * si.KILOGRAM * si.METER /\
                 si.SECOND ** 2
        assert( result.get_default_unit() == unit ) 
        assert( abs( result.get_value( unit ) - 12.0 ) < 1e-5 )
        
        result = self.newtons1 * 10
        assert( result.get_default_unit() == si.NEWTON ) 
        assert( result.get_value( si.NEWTON ) == 20 )
        
    def test_pow( self ):
        """! @brief Test powers of quantities.
              @param self
        """
        # numeric powers
        result = self.newtons1 ** 3
        assert( result.get_default_unit() == si.NEWTON ** 3 )
        assert( abs( result.get_value( si.NEWTON ** 3 ) - 8.0 ) < 1e-5 )
        
        # powers of integer dimensionless quantities
        result = self.newtons1 ** self.dimensionless
        assert( result.get_default_unit() == si.NEWTON ** 3 )
        assert( abs( result.get_value( si.NEWTON ** 3 ) - 8.0 ) < 1e-5 )
        
        # Radian is dimensionless for non strict checking
        quantities.set_strict( False )
        quantity = quantities.Quantity( si.RADIAN, 3 )
        result = self.newtons2 ** quantity
        assert( result.get_default_unit() == si.NEWTON ** 3 )
        assert( abs( result.get_value( si.NEWTON ** 3 ) - 27.0 ) < 1e-5 )
        quantities.set_strict( True )
        
        # check violation of non integer-powers
        error = 0
        try:
            result = self.newtons1 ** 2.0
        except AssertionError:
            error = 1
        assert( error )
        
        # again, check violation of non integer-powers
        quantity = quantities.Quantity.value_of( 10.0 )
        error = 0
        try:
            result = self.newtons1 ** quantity
        except AssertionError:
            error = 1
        assert( error )
        
        # check violation, of non dimensionless quantities
        error = 0
        try:
            result = self.newtons1 ** self.newtons2
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
         # check violation, of dimensionless (violating strict checks)
        error = 0
        quantity = quantities.Quantity( si.RADIAN, 3 )
        try:
            result = self.newtons1 ** quantity
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
    def test_arctan2( self ):
        """! @brief Test the operator numpy.arctan2 on quantities.
              @param self
        """
        result = numpy.arctan2(self.dimensionless, 10.0)
        #print(result)
        assert(result==numpy.arctan2(3, 10.0))
        
    def test_hypot( self ):
        """! @brief Test the operator numpy.hypot on quantities.
              @param self
        """
        # trivial
        result = numpy.hypot(self.newtons1, self.newtons2)
        assert( result.get_default_unit() == si.NEWTON )
        assert( abs( result.get_value( si.NEWTON ) - numpy.sqrt(13.0) ) 
                < 10e-6 )

        
    def test_div( self ):
        """! @brief Test dividing quantities.
              @param self
        """
        # trivial
        result = self.newtons1 / self.newtons2
        assert( result.get_default_unit() == units.ONE )
        assert( abs( result.get_value( units.ONE ) - 2.0/3.0 ) < 1e-5 )
        
        result = self.newtons2 / self.other
        unit   = si.NEWTON / ( si.KILOGRAM * si.METER /\
                 si.SECOND ** 2 )
        assert( result.get_default_unit() == unit ) 
        assert( abs( result.get_value( unit ) - 3.0/4.0 ) < 1e-5 )

        result = self.newtons1 / 10
        assert( result.get_default_unit() == si.NEWTON ) 
        assert( result.get_value( si.NEWTON ) == 
                arithmetic.RationalNumber( 2, 10 ) )
        
        # test for divide by zero
        error = 0
        try:
            result = self.newtons1 / 0
        except ArithmeticError:
            error = 1
        assert( error )
        
    def test_radd( self ):
        """! @brief Test right-add of quantities.
              @param self
        """
        value = 10
        result = value + self.dimensionless
        assert( result.get_default_unit() == units.ONE )
        assert( result.get_value( units.ONE ) == 13 )
        
        # test violation for non dimensionless quantites
        error = 0
        try:
            result = value + self.newtons1
        except qexceptions.ConversionException:
            error = 1
        assert( error == 1)
        
        # test violation for alternate dimensionless quantites
        quantity = quantities.Quantity( si.RADIAN, 3 )
        error = 0
        try:
            result = value + quantity
        except qexceptions.ConversionException:
            error = 1
        assert( error == 1 )
    
    def test_rsub( self ):
        """! @brief Test right-subtract of quantities.
              @param self
        """
        value = 10
        result = value - self.dimensionless
        assert( result.get_default_unit() == units.ONE )
        assert( result.get_value( units.ONE ) == 7 )
        
        # test violation for non dimensionless quantites
        error = 0
        try:
            result = value - self.newtons1
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # test violation for alternate dimensionless quantites
        quantity = quantities.Quantity( si.RADIAN, 3 )
        error = 0
        try:
            result = value - quantity
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
    def test_rmul( self ):
        """! @brief Test right-multiply of quantities.
              @param self
        """
        value = 10
        # trivial
        result = value * self.newtons2
        assert( result.get_default_unit() == si.NEWTON )
        assert( abs( result.get_value( si.NEWTON ) - 30.0 ) < 1e-5 )
        
        result = value * self.other
        unit   = si.KILOGRAM * si.METER /\
                 si.SECOND ** 2
        assert( result.get_default_unit() == unit ) 
        assert( result.get_value( unit ) == 40 )
        
    def test_rpow( self ):
        """! @brief Test right-powers of quantities.
              @param self
        """
        value = 10
        # powers of integer dimensionless quantities
        result = value ** self.dimensionless
        assert( isinstance(result, numbers.Number) )
        assert( result == 1000 )
        
        # Check violation of dimensionless alternate units
        error = 0
        quantity = quantities.Quantity( si.RADIAN, 3 )
        try:
            result = value ** quantity
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check non integer-powers
        quantity = quantities.Quantity.value_of( 3.0 )
        result = value ** quantity
        assert( isinstance(result, numbers.Number) )
        assert( abs( result - 1000 ) < 1e-5 )
        
        # check violation, of non dimensionless quantities
        error = 0
        try:
            result = value ** self.newtons2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
    def test_rdiv( self ):
        """! @brief Test right-divide of quantities.
              @param self
        """
        value = 10.0
        # trivial
        result = value / self.newtons2
        assert( result.get_default_unit() == units.ONE / si.NEWTON )
        assert( abs( result.get_value( units.ONE / si.NEWTON ) - 10.0/3.0 ) 
                < 1e-5 )
        
        result = value / self.other
        unit   = units.ONE / ( si.KILOGRAM * si.METER /\
                 si.SECOND ** 2 )
        assert( result.get_default_unit() == unit ) 
        assert( abs( result.get_value( unit ) - 10.0/4.0 ) < 1e-5 )

        result = value / self.dimensionless
        assert( result.get_default_unit() == units.ONE ) 
        assert( abs( result.get_value( units.ONE ) - 10.0 / 3.0 ) < 1e-5 )
        
        # test for divide by zero
        error = 0
        quantity = quantities.Quantity( si.NEWTON, 0 )
        try:
            result = value / quantity
        except ArithmeticError:
            error = 1
        assert( error )
        
    def test_iadd( self ):
        """! @brief Test augmented-add (+=) of quantities.
              @param self
        """
        newtons1 = self.newtons1
        newtons2 = self.newtons2
        # trivial
        newtons1 = self.newtons1
        newtons2 = self.newtons2
        newtons1 += newtons2
        assert( newtons1.get_default_unit() == si.NEWTON )
        assert( abs( newtons1.get_value( si.NEWTON ) - 5.0 ) < 10e-6 )
        
        # check for error
        error = 0
        newtons1 = self.newtons1
        otherStr = self.otherStr
        try:
            newtons1 += otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with strict checks (now argument is strict)
        error = 0
        newtons2 = self.newtons2
        otherStr = self.otherStr
        try:
            newtons2 += otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with weak checks
        quantities.set_strict(False)
        newtons2 = self.newtons2
        other    = self.other
        newtons2 += other
        assert( newtons2.get_default_unit() == si.NEWTON )
        assert( abs( newtons2.get_value( si.NEWTON ) - 7.0 ) < 1e-5 )
        assert( abs( newtons2.get_value( si.KILOGRAM * si.METER / 
                ( si.SECOND **2 ) ) - 7.0 ) < 1e-5 )
        quantities.set_strict(True)
        
        # check with numeric arguments
        dimensionless = self.dimensionless
        dimensionless += 10
        assert( dimensionless.get_default_unit() == units.ONE )
        assert( dimensionless.get_value( units.ONE ) == 13 )
        
        error = 0
        newtons2 = self.newtons2
        try:
            self.newtons2 += 10
        except qexceptions.ConversionException:
            error = 1
        assert( error )
    
    def test_isub( self ):
        """! @brief Test augmented-subtract (-=) of quantities.
              @param self
        """
        newtons1 = self.newtons1
        newtons2 = self.newtons2
        # trivial
        newtons1 = self.newtons1
        newtons2 = self.newtons2
        newtons1 -= newtons2
        assert( newtons1.get_default_unit() == si.NEWTON )
        assert( abs( newtons1.get_value( si.NEWTON ) + 1.0 ) < 10e-6 )
        
        # check for error
        error = 0
        newtons1 = self.newtons1
        otherStr = self.otherStr
        try:
            newtons1 -= otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with strict checks (now argument is strict)
        error = 0
        newtons2 = self.newtons2
        otherStr = self.otherStr
        try:
            newtons2 -= otherStr
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
        # check it again with weak checks
        quantities.set_strict(False)
        newtons2 = +self.newtons2
        other    = +self.other
        newtons2 -= other
        assert( newtons2.get_default_unit() == si.NEWTON )
        assert( abs( newtons2.get_value( si.NEWTON ) + 1.0 ) < 1e-5 )
        assert( abs( newtons2.get_value( si.KILOGRAM * si.METER / 
                ( si.SECOND **2 ) ) + 1.0 ) < 1e-5 )
        quantities.set_strict(True)
        
        # check with numeric arguments
        dimensionless = +self.dimensionless
        dimensionless -= 10
        assert( dimensionless.get_default_unit() == units.ONE )
        assert( dimensionless.get_value( units.ONE ) == -7 )
        
        error = 0
        newtons2 = +self.newtons2
        try:
            self.newtons2 -= 10
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
    def test_imul( self ):
        """! @brief Test augmented-multiply (*=) of quantities.
              @param self
        """
        # trivial
        newtons1 = +self.newtons1
        newtons1 *= self.newtons2
        assert( newtons1.get_default_unit() == si.NEWTON ** 2 )
        assert( abs( newtons1.get_value( si.NEWTON ** 2 ) - 6.0 ) < 1e-5 )
        
        newtons2 = +self.newtons2
        newtons2 *= self.other
        unit   = si.NEWTON * si.KILOGRAM * si.METER / si.SECOND ** 2
        assert( newtons2.get_default_unit() == unit ) 
        assert( abs( newtons2.get_value( unit ) - 12.0 ) < 1e-5 )
        
        newtons2 = +self.newtons2
        newtons2 *= self.otherStr
        unit   = si.NEWTON * si.KILOGRAM * si.METER / si.SECOND ** 2
        assert( newtons2.get_default_unit() == unit ) 
        assert( abs( newtons2.get_value( unit ) - 12.0 ) < 1e-5 )
        
        newtons1 = +self.newtons1
        #print (newtons1)
        newtons1 *= 10
        #print (newtons1)
        assert( newtons1.get_default_unit() == si.NEWTON ) 
        assert( newtons1.get_value( si.NEWTON ) == 20 )
        
    def test_ipow( self ):
        """! @brief Test augmented-powers (**=) of quantities.
              @param self
        """
        # numeric powers
        newtons1 = +self.newtons1
        newtons1 **= 3
        #print (newtons1)
        assert( newtons1.get_default_unit() == si.NEWTON**3 )
        assert( abs( newtons1.get_value( si.NEWTON ** 3 ) - 8.0 ) < 1e-5 )
        
        # powers of integer dimensionless quantities
        newtons1 = +self.newtons1
        newtons1 **= self.dimensionless
        assert( newtons1.get_default_unit() == si.NEWTON ** 3 )
        assert( abs( newtons1.get_value( si.NEWTON ** 3 ) - 8.0 ) < 1e-5 )
        
        # Radian is dimensionless for non strict checking
        quantities.set_strict(False)
        quantity = quantities.Quantity( si.RADIAN, 3 )
        newtons2 = +self.newtons2
        newtons2 **= quantity
        assert( newtons2.get_default_unit() == si.NEWTON ** 3 )
        assert( abs( newtons2.get_value( si.NEWTON ** 3 ) - 27.0 ) < 1e-5 )
        quantities.set_strict(True)
        
        # check violation of non integer-powers
        error = 0
        newtons1 = +self.newtons1
        try:
            newtons1 **= 2.0
        except AssertionError:
            error = 1
        assert( error )
        
        # again, check violation of non integer-powers
        quantity = quantities.Quantity.value_of( 10.0 )
        error = 0
        newtons1 = +self.newtons1
        try:
            newtons1 **= quantity
        except AssertionError:
            error = 1
        assert( error )
        
        # check violation, of non dimensionless quantities
        error = 0
        newtons1 = +self.newtons1
        try:
            newtons1 **= self.newtons2
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
         # check violation, of dimensionless (violating strict checks)
        error = 0
        newtons1 = +self.newtons1
        quantity = quantities.Quantity( si.RADIAN, 3 )
        try:
            newtons1 **= quantity
        except qexceptions.ConversionException:
            error = 1
        assert( error )
        
    def test_idiv( self ):
        """! @brief Test augmented-division (/=) of quantities.
              @param self
        """
        # trivial
        newtons1 = +self.newtons1
        newtons1 /= self.newtons2
        assert( newtons1.get_default_unit() == units.ONE )
        assert( abs( newtons1.get_value( units.ONE ) - 2.0/3.0 ) < 1e-5 )
        
        newtons2 = +self.newtons2
        newtons2 /= self.other
        unit   = si.NEWTON / ( si.KILOGRAM * si.METER /\
                 si.SECOND ** 2 )
        assert( newtons2.get_default_unit() == unit ) 
        assert( abs( newtons2.get_value( unit ) - 3.0/4.0 ) < 1e-5 )

        newtons1 = +self.newtons1
        newtons1 /= 10
        assert( newtons1.get_default_unit() == si.NEWTON ) 
        assert( newtons1.get_value( si.NEWTON ) == 
                arithmetic.RationalNumber( 2, 10 ) )
        
        # test for divide by zero
        error = 0
        newtons1 = +self.newtons1
        try:
            newtons1 /= 0
        except ArithmeticError:
            error = 1
        assert( error )
    
    def test_neg( self ):
        """! @brief Test negating quantities.
              @param self
        """
        quantity = quantities.Quantity( si.AMPERE, 10 )
        negative = -quantity
        
        negative *= 10
        quantity *= 100
        
        # assert correct units
        assert( negative.get_default_unit() == si.AMPERE )
        assert( quantity.get_default_unit() == si.AMPERE )
        # check independence, correct values
        assert( negative.get_value( si.AMPERE ) == -100 )
        assert( quantity.get_value( si.AMPERE ) == 1000 )
        
        # assert back transformation
        assert( -negative*10 == quantity )
        assert( -quantity == negative*10 )
        assert( negative*10 != quantity )
        assert( quantity != negative*10 )
        
        # and again one time
        quantity = quantities.Quantity( si.AMPERE, 10 )
        negative = -quantity
        
    def test_pos( self ):
        """! @brief Test cloning quantities.
              @param self
        """
        quantity = quantities.Quantity( si.AMPERE, 10 )
        clone    = +quantity
        
        clone *= 10
        quantity **= 2
        # test independence
        assert( clone.get_default_unit() != quantity.get_default_unit() )
        assert( clone.get_value( si.AMPERE ) == 
                quantity.get_value( si.AMPERE ** 2 ) )
        
    def test_abs( self ):
        """! @brief Test getting absolute values of quantities.
              @param self
        """
        quantity = quantities.Quantity( si.AMPERE, -10 )
        negation = quantities.Quantity( si.AMPERE, 10 )
        # check for correctness
        assert( abs( quantity ) == negation )
        assert( abs( negation ) == negation )
    
    def test_arccos( self ):
        """! @brief Test the operator numpy.arccos on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.arccos( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.arccos( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.arccos( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.ArcCos ) )
        
        error = 0
        try:
            result = numpy.arccos( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )

    def test_arccosh( self ):
        """! @brief Test the operator numpy.arccosh on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 1.1
        uvalue = ucomponents.UncertainInput( 1.1, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 1.1 )
        
        # test numeric broadcast
        result = numpy.arccosh( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.arccosh( 1.1 ) )
        
        # test quantities broadcast
        result = numpy.arccosh( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.ArcCosh ) )
        
        error = 0
        try:
            result = numpy.arccosh( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_arcsin( self ):
        """! @brief Test the operator numpy.arcsin on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.arcsin( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.arcsin( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.arcsin( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.ArcSin ) )
        
        error = 0
        try:
            result = numpy.arcsin( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_arcsinh( self ):
        """! @brief Test the operator numpy.arcsinh on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.arcsinh( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.arcsinh( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.arcsinh( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.ArcSinh ) )
        
        error = 0
        try:
            result = numpy.arcsinh( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_arctan( self ):
        """! @brief Test the operator numpy.arctan on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.arctan( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.arctan( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.arctan( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.ArcTan ) )
        
        error = 0
        try:
            result = numpy.arctan( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_arctanh( self ):
        """! @brief Test the operator numpy.arctanh on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.arctanh( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.arctanh( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.arctanh( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.ArcTanh ) )
        
        error = 0
        try:
            result = numpy.arctanh( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_cos( self ):
        """! @brief Test the operator numpy.cos on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.cos( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.cos( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.cos( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Cos ) )
        
        error = 0
        try:
            result = numpy.cos( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_cosh( self ):
        """! @brief Test the operator numpy.cosh on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.cosh( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.cosh( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.cosh( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Cosh ) )
        
        error = 0
        try:
            result = numpy.cosh( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_tan( self ):
        """! @brief Test the operator numpy.tan on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.tan( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.tan( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.tan( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Tan ) )
        
        error = 0
        try:
            result = numpy.tan( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_tanh( self ):
        """! @brief Test the operator numpy.tanh on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.tanh( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.tanh( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.tanh( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Tanh ) )
        
        error = 0
        try:
            result = numpy.tanh( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_log10( self ):
        """! @brief Test the operator numpy.log10 on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.log10( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.log10( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.log10( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Div ) )
        
        error = 0
        try:
            result = numpy.log10( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
        
    def test_log2( self ):
        """! @brief Test the operator numpy.log2 on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.log2( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.log2( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.log2( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Div ) )
        
        error = 0
        try:
            result = numpy.log2( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_sin( self ):
        """! @brief Test the operator numpy.sin on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.sin( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.sin( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.sin( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Sin ) )
        
        error = 0
        try:
            result = numpy.sin( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_sinh( self ):
        """! @brief Test the operator numpy.sinh on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.sinh( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.sinh( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.sinh( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Sinh ) )
        
        error = 0
        try:
            result = numpy.sinh( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error )
    
    def test_sqrt( self ):
        """! @brief Test the operator numpy.sqrt on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        result = numpy.sqrt( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN.sqrt() )
        value = result.get_value( unit )
        assert( value == numpy.sqrt( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.sqrt( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN.sqrt() )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Sqrt ) )
        
        result = numpy.sqrt( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.METER )
        value = result.get_value( unit )
        assert( value == numpy.sqrt( 0.9 ) )
        
    def test_square( self ):
        """! @brief Test the operator numpy.square on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        result = numpy.square( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN ** 2)
        value = result.get_value( unit )
        assert( value == numpy.square( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.square( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN ** 2 )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Mul ) )
        
        result = numpy.square( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.METER ** 4 )
        value = result.get_value( unit )
        assert( value == numpy.square( 0.9 ) )
    
    def test_absolute( self ):
        """! @brief Test the operator numpy.absolute on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        result = numpy.absolute( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( value == numpy.absolute( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.absolute( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Abs ) )
        
        result = numpy.absolute( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.METER**2 )
        value = result.get_value( unit )
        assert( value == numpy.absolute( 0.9 ) )
    
    def test_fabs( self ):
        """! @brief Test the operator numpy.fabs on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        result = numpy.fabs( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( value == numpy.fabs( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.fabs( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Abs ) )
        
        result = numpy.fabs( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.METER**2 )
        value = result.get_value( unit )
        assert( value == numpy.fabs( 0.9 ) )
    
    def test_floor( self ):
        """! @brief Test the operator numpy.floor on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        result = numpy.floor( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( value == numpy.floor( 0.9 ) )
        
        # test quantities broadcast
        error = 0
        try:
            result = numpy.floor( quvalue )
        except AttributeError:
            error = 1
        assert( error==0 )
        
        result = numpy.floor( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.METER**2 )
        value = result.get_value( unit )
        assert( value == numpy.floor( 0.9 ) )
    
    def test_ceil( self ):
        """! @brief Test the operator numpy.ceil on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        result = numpy.ceil( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( value == numpy.ceil( 0.9 ) )
        
        # test quantities broadcast
        error = 0
        try:
            result = numpy.ceil( quvalue )
        except AttributeError:
            error = 1
        assert( error==0 )
        
        result = numpy.ceil( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.METER**2 )
        value = result.get_value( unit )
        assert( value == numpy.ceil( 0.9 ) )
    
    def test_fmod( self ):
        """! @brief Test the operator numpy.fmod on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.METER**2, 0.9 )
        
        # test numeric broadcast
        error = 0
        try:
            result = numpy.fmod( qnvalue, quvalue )
        except AttributeError:
            error = 1
        assert( error==1 )
    
    def test_exp( self ):
        """! @brief Test the operator numpy.exp on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.exp( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.exp( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.exp( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Exp ) )
        
        error = 0
        try:
            result = numpy.exp( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error==1 )
    
    def test_log( self ):
        """! @brief Test the operator numpy.log on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, 0.9 )
        
        # test numeric broadcast
        result = numpy.log( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( value == numpy.log( 0.9 ) )
        
        # test quantities broadcast
        result = numpy.log( quvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == units.ONE )
        value = result.get_value( unit )
        assert( isinstance( value, ucomponents.Log ) )
        
        error = 0
        try:
            result = numpy.log( qivalue )
        except qexceptions.NotDimensionlessException:
            error = 1
        assert( error==1 )
    
    def test_conjugate( self ):
        """! @brief Test the operator numpy.conjugate on quantities.
              @param self
        """
        # define different value types in order to test the broadcasts
        nvalue = 0.9
        uvalue = ucomponents.UncertainInput( 0.9, 0.0 )
        # the corresponding quantities
        qnvalue = quantities.Quantity( si.RADIAN, nvalue )
        quvalue = quantities.Quantity( si.RADIAN, uvalue )
        qivalue = quantities.Quantity( si.NEWTON, complex( 1.0, 2.0 ) )
        
        # test numeric broadcast
        result = numpy.conjugate( qnvalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.RADIAN )
        value = result.get_value( unit )
        assert( value == numpy.conjugate( 0.9 ) )
        
        # test quantities broadcast
        error = 0
        try:
            result = numpy.conjugate( quvalue )
        except AttributeError:
            error = 1
        assert( error==0 )
            
        result = numpy.conjugate( qivalue )
        assert( isinstance( result, quantities.Quantity ) )
        unit = result.get_default_unit()
        assert( unit == si.NEWTON )
        value = result.get_value( unit )
        assert( value == complex( 1.0, -2.0 ) )
        
    def test_invert( self ):
        """! @brief Test inverting of quantities.
              @param self
        """
        quantity  = quantities.Quantity( si.AMPERE, 10 )
        inversion = quantities.Quantity( units.ONE / si.AMPERE, 
                                       arithmetic.RationalNumber( 1, 10 ) )
        assert( ~quantity == inversion )
        assert( ~inversion == quantity )
        # test dimensionless
        quantity  = quantities.Quantity.value_of( 10 )
        inversion = quantities.Quantity.value_of(arithmetic.RationalNumber( 1, 10 ) )
        assert( ~quantity == inversion )
        assert( ~inversion == quantity )
        
    def test_casts( self ):
        """! @brief Test casting quatities to other numeric types.
              @param self
        """
        quantities.set_strict(False)
        q1 = quantities.Quantity( si.AMPERE, 10 )
        q2 = quantities.Quantity( si.AMPERE, 1.5 )
        q3 = quantities.Quantity( si.AMPERE, 
                                  arithmetic.RationalNumber( 1, 2 ) )
        q4 = quantities.Quantity( si.AMPERE, complex( 2, 1 ) )
        
        value = float( q1 )
        assert( abs( value - 10.0 ) < 1e-5 )
        value = float( q2 )
        assert( value == 1.5 )
        value = float( q3 )
        assert( abs( value - 0.5 ) < 1e-5 )
        
        error = 0
        try:
            float( q4 )
        except TypeError:
            error = 1
        assert( error==1 )
        
        value = int( q1 )
        assert( value == 10 )
        value = int( q2 )
        assert( value == 1 )
        value = int( q3 )
        assert( value == 0 )
        
        error = 0
        try:
            int( q4 )
        except TypeError:
            error = 1
        assert( error==1 )
        
        value = int( q1 )
        assert( value == 10 )
        value = int( q2 )
        assert( value == 1 )
        value = int( q3 )
        assert( value == 0 )
        
        error = 0
        try:
            int( q4 )
        except TypeError:
            error = 1
        assert( error==1 )
        
        value = complex( q1 )
        assert( value == complex( 10, 0 ) )
        value = complex( q2 )
        assert( abs( value - complex( 1.5, 0 ) ) < 1e-5 )
        value = complex( q3 )
        assert( abs( value - complex( 0.5, 0 ) ) < 1e-5 )
        value = complex( q4 )
        assert( value == complex( 2, 1 ) )
        quantities.set_strict(True)
        
    def test_comparisions( self ):
        """! @brief Test comparing quantities.
              @param self
        """
        # assert errors if wrong units
        q1 = quantities.Quantity( si.AMPERE, 10 )
        q2 = quantities.Quantity( si.KELVIN, 11.0 )
        assert( q1 != q2 )
        
        # impossible different units
        error = 0
        try:
            q1 < q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        error = 0
        try:
            q1 > q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        error = 0
        try:
            q1 <= q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        error = 0
        try:
            q1 >= q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        # error = 0
        # try:
        #     cmp( q1, q2 )
        # except qexceptions.ConversionException:
        #     error = 1
        # assert( error==1 )
        
        # assert errors if compatible units but strict checking
        q1 = quantities.Quantity( si.NEWTON, 10 )
        q2 = quantities.Quantity( si.KILOGRAM * si.METER / 
                                  si.SECOND ** 2, 11.0 )
        assert( q1 != q2 )
        
        # impossible different units
        error = 0
        try:
            q1 < q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        error = 0
        try:
            q1 > q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        error = 0
        try:
            q1 <= q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        error = 0
        try:
            q1 >= q2
        except qexceptions.ConversionException:
            error = 1
        assert( error==1 )
        
        # impossible different units
        # error = 0
        # try:
        #     cmp( q1, q2 )
        # except qexceptions.ConversionException:
        #     error = 1
        # assert( error==1 )
        
        q1 = quantities.Quantity( si.NEWTON, 10 )
        q2 = quantities.Quantity( si.KILOGRAM * si.METER / 
                                  si.SECOND ** 2, 11.0 )
        assert( q1 != q2 )
        quantities.set_strict(False)
        assert( q1 < q2 )
        assert( not ( q1 > q2 ) )
        assert( q1 <= q2 )
        assert( not ( q1 >= q2 ) )
        #assert( cmp( q1, q2 ) < 0 )
        quantities.set_strict(True)
        
        # trivial
        q1 = quantities.Quantity( si.NEWTON, 10 )
        q2 = quantities.Quantity( si.NEWTON, 11.0 )
        assert( q1 != q2 )
        assert( q1 < q2 )
        assert( not ( q1 > q2 ) )
        assert( q1 <= q2 )
        assert( not ( q1 >= q2 ) )
        #assert( cmp( q1, q2 ) < 0 )
        
class TestUncertaintyComponents( unittest.TestCase ):
    """! @brief       This class provides tests for the ucomponents module.
    """
    
    def TEST_COMPONENT_SERIALIZATION( component, type, numsilblings, 
                                    protocol = pickle.HIGHEST_PROTOCOL ):
        """! @brief Check serializing components of uncertainty.
              @param component The instance of ucomponents.UncertainComponent 
                     to check.
              @param type The type of the component.
              @param numsilblings The number components that is returned
                     by ucomponents.UncertainComponent.depends_on
              @param protocol The serialization protocol version to use.
              @see pickle.HIGHEST_PROTOCOL
              @return The deserialized instance.
        """
        # sanity check
        assert( isinstance( component, type ) )
        assert( len( component.depends_on() ) == numsilblings )
        
        # If False is returned, the object can not be
        # serialized
        assert( component.__getstate__() != False )
        # serialize the object
        someString = pickle.dumps( component, protocol )
        # is the result really a string?
        assert( someString != None )
        assert( len( someString ) > 0 )
        
        # dserialize the objects
        deserializedInstance = pickle.loads( someString )
        # check for type
        assert( isinstance( deserializedInstance, type ) )
        # check for reference
        assert( not ( deserializedInstance is component ) )
        # check for same number of silblings
        # if not, then an inccorect handling of silblings occured
        assert( len( deserializedInstance.depends_on() ) ==
                len( component.depends_on() ) )
        assert( len( deserializedInstance.depends_on() ) == numsilblings )
        # Check for type and silblings
        assert( component.equal_debug( deserializedInstance ) )
        return deserializedInstance
    TEST_COMPONENT_SERIALIZATION = staticmethod( TEST_COMPONENT_SERIALIZATION )
    
    def TEST_UNCERTAIN_COMPONENT( component, dtype, expectedValue, 
                                expectedUncertainty, accuracy ):
        """! @brief A general component test for ucomponents.UncertainComponent.
        """
        # sanity tests
        assert( isinstance( component, ucomponents.UncertainComponent ) )
        assert( isinstance(expectedValue, numbers.Number) )
        # check for range violations
        if(sys.platform != 'win32'):
            assert( expectedValue != float( "NaN" ) )
            assert( expectedUncertainty != float( "NaN" ) )
            assert( accuracy != float( "NaN" ) )
            assert( expectedValue != float( "Infinity" ) )
            assert( expectedUncertainty != float( "Infinity" ) )
            assert( accuracy != float( "Infinity" ) )
        
        assert( isinstance(expectedUncertainty, numbers.Number) )
        assert( isinstance(accuracy, numbers.Number) )
        
        value       = component.get_value()
        uncertty = 0.0
        
        # perform partial derivation 
        for item in component.depends_on():
            tmp = component.get_uncertainty( item )
            uncertty += tmp
        
        # type checking
        assert( isinstance( component, dtype ) )
        
        # value checking
        #print (value, expectedValue)
        #print (uncertty, expectedUncertainty)
        assert( abs( value - expectedValue ) < accuracy )
        assert( abs( uncertty - expectedUncertainty ) < accuracy )
        # check for range violations
        if(sys.platform != 'win32'):
            assert( value != float( "NaN" ) )
            assert( uncertty != float( "NaN" ) )
            assert( value != float( "Infinity" ) )
            assert( uncertty != float( "Infinity" ) )
            
    TEST_UNCERTAIN_COMPONENT = staticmethod( TEST_UNCERTAIN_COMPONENT )
    
    class Element:
        """! @brief A class that is used for testing for identity
        """
        
        def __init__( self, value ):
            """! @brief         Default constructor.
                      @param self
                      @param value A value to assign to the instance
            """
            self.value = value
            
        def __eq__( self, other ):
            """! @brief         The function that is normally used for comparision.
                      @attention When using ucomponents.clearDuplicates
                                 this method should not get called.
                      @param self
                      @param other Another instance of Element.
            """
            return self.value == other.value
            
        def get_value( self ):
            """! @brief         Return the value assigned.
                      @param self
                      @return The value assigned
            """
            return self.value
        
        def __hash__( self ):
            """! @brief         A necessary method for working with containers.
                      @param self
            """
            return 1
    
    def test_clear_duplicates( self ):
        """! @brief Test the function ucomponents.clearDuplicates.
              @param self
        """
        # create some elements
        one         = TestUncertaintyComponents.Element( 1 )
        two         = TestUncertaintyComponents.Element( 2 )
        three       = TestUncertaintyComponents.Element( 3 )
        anotherOne  = TestUncertaintyComponents.Element( 1 )
        
        # some sanity tests (for is)
        assert( not ( one is anotherOne ) )
        assert( not ( two is anotherOne ) )
        assert( not ( three is anotherOne ) )
        assert( one is one )
        assert( two is two )
        assert( three is three )
        assert( anotherOne is anotherOne )
        # ... check if eq works
        assert( one == anotherOne )
        assert( one != two )
        
        mysequence = [one, two, three]
        assert( len( mysequence ) == 3 )
        # here __eq__ gets called
        assert( operator.contains( mysequence, one ) == True )
        # here __eq__ gets called
        assert( operator.contains( mysequence, anotherOne ) == True )
        # now append an identical one (we have two "ones" then)
        mysequence += [one]
        assert( len( mysequence ) == 4 )
        # now append an equal one (we have two "ones"
        # and one "anotherOne" then)
        mysequence += [anotherOne]
        # this should remove the duplicate one
        newList = ucomponents.clearDuplicates( mysequence )
        assert( len( newList ) == 4 )
        # make shure the correctOne was removed
        countOne = 1
        countTwo = 1
        countThree = 1
        countAnotherOne = 1
        for item in newList:
            if item is one:
                countOne -= 1
            if item is two:
                countTwo -= 1
            if item is three:
                countThree -= 1
            if item is anotherOne:
                countAnotherOne -= 1
        assert( countOne == 0 )
        assert( countTwo == 0 )
        assert( countThree == 0 )
        assert( countAnotherOne == 0 )
        
    def setUp( self ):
        """! @brief Initialize this test instance.
              @param self
        """
        self.inputLong = ucomponents.UncertainInput( 10, 2 )
        self.inputFloat = ucomponents.UncertainInput( 20.0, 3.0 )
        self.inputRational = ucomponents.UncertainInput( 
                                        arithmetic.RationalNumber( 30, 1 ), 
                                        arithmetic.RationalNumber( 4, 1 ) )
        
    def test_add( self ):
        """! @brief Test the Operator ucomponents.Add.
              @param self
        """
        # Addition (10+-2) + (20+-3)
        operator = ucomponents.Add( self.inputLong, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Add, 
                                                30.0, 5.0, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Add, 
                                                    2 )
        # Addition (10+-2) + (30+-4)
        operator = ucomponents.Add( self.inputLong, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Add, 
                                                40.0, 6.0, 1e-4 )
        # Addition (20+-3) + (10+-2)
        operator = ucomponents.Add( self.inputFloat, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Add, 
                                                30.0, 5.0, 1e-4 )
        # Addition (20+-3) + (30+-4)
        operator = ucomponents.Add( self.inputFloat, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Add, 
                                                50.0, 7.0, 1e-4 )
        # Addition (30+-4) + (10+-2)
        operator = ucomponents.Add( self.inputRational, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Add, 
                                                40.0, 6.0, 1e-4 )
        # Addition (30+-4) + (20+-3)
        operator = ucomponents.Add( self.inputRational, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Add, 
                                                50.0, 7.0, 1e-4 )
                                                
    def test_arctan2( self ):
        """! @brief Test the Operator ucomponents.ArcTan2.
              @param self
        """
        # (10+-2) + (20+-3)
        operator = numpy.arctan2( self.inputLong, self.inputFloat )
        val = numpy.arctan2(10.0,20.0)
        u   = 10.0/(10.0**2 + 20**2)*3 - 20.0/(10.0**2 + 20**2)*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcTan2, 
                                                val, u, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.ArcTan2, 
                                                    2 )
    
    def test_mul( self ):
        """! @brief Test the Operator ucomponents.Mul.
              @param self                                            
        """
        # Multiplication (10+-2) * (20+-3)
        operator = ucomponents.Mul( self.inputLong, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Mul, 
                                                200.0, 70.0, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Mul, 
                                                    2 )
        # Multiplication (10+-2) * (30+-4)
        operator = ucomponents.Mul( self.inputLong, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Mul, 
                                                300.0, 100.0, 1e-4 )
        # Multiplication (20+-3) * (10+-2)
        operator = ucomponents.Mul( self.inputFloat, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Mul, 
                                                200.0, 70.0, 1e-4 )
        # Multiplication (20+-3) * (30+-4)
        operator = ucomponents.Mul( self.inputFloat, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Mul, 
                                                600.0, 170.0, 1e-4 )
        # Multiplication (30+-4) * (10+-2)
        operator = ucomponents.Mul( self.inputRational, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Mul, 
                                                300.0, 100.0, 1e-4 )
        # Multiplication (30+-4) * (20+-3)
        operator = ucomponents.Mul( self.inputRational, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Mul, 
                                                600.0, 170.0, 1e-4 )
                                                
    def test_div( self ):
        """! @brief Test the Operator ucomponents.Div.
              @param self                                            
        """
        # Division (10+-2) / (20+-3)
        operator = ucomponents.Div( self.inputLong, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Div, 
                                                1.0/2.0, 1.0/40.0, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Div, 
                                                    2 )
        # Division (10+-2) / (30+-4)
        operator = ucomponents.Div( self.inputLong, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Div, 
                                                1.0/3.0, 0.02222, 1e-4 )
        # Division (20+-3) / (10+-2)
        operator = ucomponents.Div( self.inputFloat, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Div, 
                                                2.0, -1.0/10.0, 1e-4 )
        
        # Division (20+-3) / (30+-4)
        operator = ucomponents.Div( self.inputFloat, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Div, 
                                                2.0/3.0, 0.01111, 1e-4 )
        # Division (30+-4) / (10+-2)
        operator = ucomponents.Div( self.inputRational, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Div, 
                                                3.0, -1.0/5.0, 1e-4 )
        # Division (30+-4) / (20+-3)
        operator = ucomponents.Div( self.inputRational, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Div, 
                                                3.0/2.0, -1.0/40.0, 1e-4 )
        
        # Check for divide by zero
        error = False
        try:
            operator = ucomponents.Div( self.inputRational, 0.0 )
        except ArithmeticError:
            error = True
        assert( error==True )
        
    def test_sub( self ):
        """! @brief Test the Operator ucomponents.Sub.
              @param self                                            
        """
        # Difference (10+-2) - (20+-3)
        operator = ucomponents.Sub( self.inputLong, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sub, 
                                                -10.0, -1.0, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Sub, 
                                                    2 )
        # Difference (10+-2) - (30+-4)
        operator = ucomponents.Sub( self.inputLong, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sub, 
                                                -20.0, -2.0, 1e-4 )
        # Difference (20+-3) - (10+-2)
        operator = ucomponents.Sub( self.inputFloat, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sub, 
                                                10.0, 1.0, 1e-4 )
        # Difference (20+-3) - (30+-4)
        operator = ucomponents.Sub( self.inputFloat, self.inputRational )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sub, 
                                                -10.0, -1.0, 1e-4 )
        # Difference (30+-4) - (10+-2)
        operator = ucomponents.Sub( self.inputRational, self.inputLong )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sub, 
                                                20.0, 2.0, 1e-4 )
        # Difference (30+-4) - (20+-3)
        operator = ucomponents.Sub( self.inputRational, self.inputFloat )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sub, 
                                                10.0, 1.0, 1e-4 )
                                                
    def test_pow( self ):
        """! @brief Test the Operator ucomponents.Pow.
              @param self                                            
        """
        # Power (10+-2) ** (20+-3)
        operator = ucomponents.Pow( self.inputLong, self.inputFloat )
        uncertty =  1e19*20*2 + 1e20 * numpy.log( 10 ) * 3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Pow, 
                                                1e20, uncertty, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Pow, 
                                                    2 )
#        # Power (10+-2) ** (30+-4)
#        operator = ucomponents.Pow( self.inputLong, self.inputRational )
#        uncertty =  1e29*30*2 + 1e30 * numpy.log( 10 ) * 4
#        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
#                                                ucomponents.Pow, 
#                                                1e30, uncertty, 1e-4 )
        # Power (20+-3) ** (10+-2)
        operator = ucomponents.Pow( self.inputFloat, self.inputLong )
        uncertty =  ( 20**9 )*10*3 + ( 20**10 ) * numpy.log( 20 ) * 2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Pow, 
                                                20**10, uncertty, 1e-4 )
        # Power (20+-3) ** (30+-4)
        operator = ucomponents.Pow( self.inputFloat, self.inputRational )
        uncertty =  ( 20.0**29.0 )*30.0*3.0 + ( 20.0**30.0 ) \
                    * numpy.log( 20.0 ) * 4.0
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Pow, 
                                                20**30, uncertty, 1e-4 )
        # Power (30+-4) ** (10+-2)
        operator = ucomponents.Pow( self.inputRational, self.inputLong )
        uncertty =  ( 30**9 )*10*4 + ( 30**10 ) * numpy.log( 30 ) * 2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Pow, 
                                                30**10, uncertty, 1e-4 )
        # Power (30+-4) ** (20+-3)
        operator = ucomponents.Pow( self.inputRational, self.inputFloat )
        uncertty =  ( 30.0**19.0 )*20.0*4.0 + ( 30.0**20.0 ) * numpy.log( 30.0 ) * 3.0
        #print(self.inputRational)
        #print(self.inputFloat)
        #print (uncertty)
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, ucomponents.Pow, 30**20, uncertty, 1e-4 )
                                                
        # check range errors (for which pow is undefined for)
        error = False
        try:
            value = ucomponents.Pow( self.inputRational, 0.0 )
            assert( value.get_value() == 1.0 )
            uncertty = value.get_uncertainty( None )
        except ArithmeticError:
            error = True
        assert( error==False )
        
        error = False
        try:
            value = ucomponents.Pow( 0.0, self.inputRational )
            assert( value.get_value() == 0.0 )
            uncertty = value.get_uncertainty( None )
        except ArithmeticError:
            error = True
        assert( error==False )
        
    
    def test_sin( self ):
        """! @brief Test the Operator ucomponents.Sin.
              @param self                                            
        """
        # sin(10+-2)
        operator = ucomponents.Sin( self.inputLong )
        uncertty = numpy.cos( 10 )*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sin, 
                                                numpy.sin( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Sin, 
                                                    1 )
        # sin(20+-3)
        operator = ucomponents.Sin( self.inputFloat )
        uncertty = numpy.cos( 20 )*3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sin, 
                                                numpy.sin( 20 ), uncertty, 
                                                1e-4 )
        # sin(30+-4)
        operator = ucomponents.Sin( self.inputRational )
        uncertty = numpy.cos( 30 )*4
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sin, 
                                                numpy.sin( 30 ), uncertty, 
                                                1e-4 )
    
    def test_cos( self ):
        """! @brief Test the Operator ucomponents.Cos.
              @param self                                            
        """
        # cos(10+-2)
        operator = ucomponents.Cos( self.inputLong )
        uncertty = -numpy.sin( 10 )*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Cos, 
                                                numpy.cos( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Cos, 
                                                    1 )
        # cos(20+-3)
        operator = ucomponents.Cos( self.inputFloat )
        uncertty = -numpy.sin( 20 )*3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Cos, 
                                                numpy.cos( 20 ), uncertty, 
                                                1e-4 )
        # cos(30+-4)
        operator = ucomponents.Cos( self.inputRational )
        uncertty = -numpy.sin( 30 )*4
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Cos, 
                                                numpy.cos( 30 ), uncertty, 
                                                1e-4 )
    
    def test_tan( self ):
        """! @brief Test the Operator ucomponents.Tan.
              @param self                                            
        """
        # cos(10+-2)
        operator = ucomponents.Tan( self.inputLong )
        uncertty = 2.0/( numpy.cos( 10 )*numpy.cos( 10 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Tan, 
                                                numpy.tan( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Tan, 
                                                    1 )
        # cos(20+-3)
        operator = ucomponents.Tan( self.inputFloat )
        uncertty = 3.0/( numpy.cos( 20 )*numpy.cos( 20 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Tan, 
                                                numpy.tan( 20 ), uncertty, 
                                                1e-4 )
        # cos(30+-4)
        operator = ucomponents.Tan( self.inputRational )
        uncertty = 4.0/( numpy.cos( 30 )*numpy.cos( 30 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Tan, 
                                                numpy.tan( 30 ), uncertty, 
                                                1e-4 )
    
    def test_sqrt( self ):
        """! @brief Test the Operator ucomponents.Sqrt.
              @param self
        """
        # sqrt(10+-2)
        operator = ucomponents.Sqrt( self.inputLong )
        uncertty = 1.0/numpy.sqrt( 10 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sqrt, 
                                                numpy.sqrt( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Sqrt, 
                                                    1 )
        # sqrt(20+-3)
        operator = ucomponents.Sqrt( self.inputFloat )
        uncertty = 3.0/( 2.0*numpy.sqrt( 20 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sqrt, 
                                                numpy.sqrt( 20 ), uncertty, 
                                                1e-4 )
        # sqrt(30+-4)
        operator = ucomponents.Sqrt( self.inputRational )
        uncertty = 4.0/( 2.0*numpy.sqrt( 30 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sqrt, 
                                                numpy.sqrt( 30 ), uncertty, 
                                                1e-4 )
        # test for extreme values
        error = False
        try:
            operator = ucomponents.Sqrt( -1.0 )
        except ArithmeticError:
            error = True
        assert( error==False )
        
        error = False
        try:
            operator = ucomponents.Sqrt( -1.0 )
            operator.get_uncertainty( None )
        except ArithmeticError:
            error = True
        assert( error==False )
    
    def test_log( self ):
        """! @brief Test the Operator ucomponents.Log.
              @param self                                            
        """
        # log(10+-2)
        operator = ucomponents.Log( self.inputLong )
        uncertty = 2.0/10.0
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Log, 
                                                numpy.log( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Log, 
                                                    1 )

        # log(20+-3)
        operator = ucomponents.Log( self.inputFloat )
        uncertty = 3.0/20.0
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Log, 
                                                numpy.log( 20 ), uncertty, 
                                                1e-4 )
        # log(30+-4)
        operator = ucomponents.Log( self.inputRational )
        uncertty = 4.0/30.0
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Log, 
                                                numpy.log( 30 ), uncertty, 
                                                1e-4 )
        
        # test for extreme values
        error = False
        try:
            operator = ucomponents.Log( -1.0 )
        except ArithmeticError:
            error = True
        assert( error==True )
        
        error = False
        try:
            operator = ucomponents.Log( 0.0 )
            operator.get_uncertainty( None )
        except ArithmeticError:
            error = True
        assert( error==True )
    
    def test_arcsin( self ):
        """! @brief Test the Operator ucomponents.ArcSin.
              @param self                                            
        """
        # define some custom values (since the default ones violate
        # the range conditions)
        customFloat    = ucomponents.UncertainInput( 0.7, 0.2 )
        customRational = ucomponents.UncertainInput( 
                         arithmetic.RationalNumber( 1, 2 ), 
                         arithmetic.RationalNumber( 1, 10 ) )
        
        # log(10+-2)
        operator = ucomponents.ArcSin( customFloat )
        uncertty = 0.2/numpy.sqrt( 1.0-0.7*0.7 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcSin, 
                                                numpy.arcsin( 0.7 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.ArcSin, 
                                                    1 )
        # log(20+-3)
        operator = ucomponents.ArcSin( customRational )
        uncertty = 0.1/numpy.sqrt( 1.0-0.5*0.5 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcSin, 
                                                numpy.arcsin( 0.5 ), uncertty, 
                                                1e-4 )
                                                
        # test for extreme values
        error = False
        try:
            operator = ucomponents.ArcSin( -1.1 )
        except ArithmeticError:
            error = True
        assert( error==True )
        
        error = False
        try:
            operator = ucomponents.ArcSin( 1.1 )
        except ArithmeticError:
            error = True
        assert( error==True )
    
    def test_arctan( self ):       
        """! @brief Test the Operator ucomponents.ArcTan.
              @param self                                            
        """
        # arctan(10+-2)
        operator = ucomponents.ArcTan( self.inputLong )
        uncertty = 2.0/( 1.0+10.0*10.0 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcTan, 
                                                numpy.arctan( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.ArcTan, 
                                                    1 )
        # arctan(20+-3)
        operator = ucomponents.ArcTan( self.inputFloat )
        uncertty = 3.0/( 1.0+20.0*20.0 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcTan, 
                                                numpy.arctan( 20 ), uncertty, 
                                                1e-4 )
        # arctan(30+-4)
        operator = ucomponents.ArcTan( self.inputRational )
        uncertty = 4.0/( 1.0+30.0*30.0 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcTan, 
                                                numpy.arctan( 30 ), uncertty, 
                                                1e-4 )
    
    def test_arccos( self ):
        """! @brief Test the Operator ucomponents.ArcCos.
              @param self                                            
        """
        # define some custom values (since the default ones violate
        # the range conditions)
        customFloat    = ucomponents.UncertainInput( 0.7, 0.2 )
        customRational = ucomponents.UncertainInput( 
                         arithmetic.RationalNumber( 1, 2 ), 
                         arithmetic.RationalNumber( 1, 10 ) )
        
        # log(10+-2)
        operator = ucomponents.ArcCos( customFloat )
        uncertty = -0.2/numpy.sqrt( 1.0-0.7*0.7 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcCos, 
                                                numpy.arccos( 0.7 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.ArcCos, 
                                                    1 )
        # log(20+-3)
        operator = ucomponents.ArcCos( customRational )
        uncertty = -0.1/numpy.sqrt( 1.0-0.5*0.5 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcCos, 
                                                numpy.arccos( 0.5 ), uncertty, 
                                                1e-4 )
                                                
        # test for extreme values
        error = False
        try:
            operator = ucomponents.ArcCos( -1.1 )
        except ArithmeticError:
            error = True
        assert( error==True )
        
        error = False
        try:
            operator = ucomponents.ArcCos( 1.1 )
        except ArithmeticError:
            error = True
        assert( error==True )
    
    def test_cosh( self ):
        """! @brief Test the Operator ucomponents.Cosh.
              @param self                                            
        """
        # cosh(10+-2)
        operator = ucomponents.Cosh( self.inputLong )
        uncertty = numpy.sinh( 10 )*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Cosh, 
                                                numpy.cosh( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Cosh, 
                                                    1 )
        # cosh(20+-3)
        operator = ucomponents.Cosh( self.inputFloat )
        uncertty = numpy.sinh( 20 )*3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Cosh, 
                                                numpy.cosh( 20 ), uncertty, 
                                                1e-4 )
        # cosh(30+-4)
        operator = ucomponents.Cosh( self.inputRational )
        uncertty = numpy.sinh( 30 )*4
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Cosh, 
                                                numpy.cosh( 30 ), uncertty, 
                                                1e-4 )
    
    def test_sinh( self ):
        """! @brief Test the Operator ucomponents.Sinh.
              @param self                                            
        """
        # sinh(10+-2)
        operator = ucomponents.Sinh( self.inputLong )
        uncertty = numpy.cosh( 10 )*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sinh, 
                                                numpy.sinh( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Sinh, 
                                                    1 )
        # sinh(20+-3)
        operator = ucomponents.Sinh( self.inputFloat )
        uncertty = numpy.cosh( 20 )*3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sinh, 
                                                numpy.sinh( 20 ), uncertty, 
                                                1e-4 )
        # sinh(30+-4)
        operator = ucomponents.Sinh( self.inputRational )
        uncertty = numpy.cosh( 30 )*4
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Sinh, 
                                                numpy.sinh( 30 ), uncertty, 
                                                1e-4 )
                                                
    def test_tanh( self ):
        """! @brief Test the Operator ucomponents.Tanh.
              @param self                                            
        """
        # tanh(10+-2)
        operator = ucomponents.Tanh( self.inputLong )
        uncertty = ( 1.0 - numpy.tanh( 10 )**2 )*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Tanh, 
                                                numpy.tanh( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Tanh, 
                                                    1 )
        # tanh(20+-3)
        operator = ucomponents.Tanh( self.inputFloat )
        uncertty = ( 1.0 - numpy.tanh( 20 )**2 )*3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Tanh, 
                                                numpy.tanh( 20 ), uncertty, 
                                                1e-4 )
        # tanh(30+-4)
        operator = ucomponents.Tanh( self.inputRational )
        uncertty = ( 1.0 - numpy.tanh( 30 )**2 )*4
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Tanh, 
                                                numpy.tanh( 30 ), uncertty, 
                                                1e-4 )
                                                
    def test_arctanh( self ):
        """! @brief Test the Operator ucomponents.ArcTanh.
              @param self                                            
        """
        # arctanh(-0.9+-0.1)
        value = ucomponents.UncertainInput( -0.9, 0.1 )
        operator = ucomponents.ArcTanh( value )
        uncertty = 0.1/( 1.0 - 0.9**2 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcTanh, 
                                                numpy.arctanh( -0.9 ), 
                                                uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( 
                                                    operator, 
                                                    ucomponents.ArcTanh, 
                                                    1 )
        # arctanh(0.0+-0.1)
        value = ucomponents.UncertainInput( 0.0, 0.1 )
        operator = ucomponents.ArcTanh( value )
        uncertty = 0.1
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcTanh, 
                                                numpy.arctanh( 0.0 ), 
                                                uncertty, 
                                                1e-4 )
                                                
        # force arithmetic error
        # arctanh(1.0)
        error = 0
        try:
            value = ucomponents.UncertainInput( 1.0, 0.0 )
            operator = ucomponents.ArcTanh( value )
        except ArithmeticError:
            error = 1
        assert( error==1 )
    
    def test_arccosh( self ):
        """! @brief Test the Operator ucomponents.ArcCosh.
              @param self                                            
        """
        # arccosh(10+-2)
        operator = ucomponents.ArcCosh( self.inputLong )
        uncertty = 2 / ( numpy.sqrt( 10 - 1.0 )*numpy.sqrt( 10 + 1.0 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcCosh, 
                                                numpy.arccosh( 10 ), 
                                                uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( 
                                                    operator, 
                                                    ucomponents.ArcCosh, 
                                                    1 )
        # arccosh(20+-3)
        operator = ucomponents.ArcCosh( self.inputFloat )
        uncertty = 3.0 / ( numpy.sqrt( 20.0 - 1.0 )*numpy.sqrt( 20.0 + 1.0 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcCosh, 
                                                numpy.arccosh( 20 ), 
                                                uncertty, 
                                                1e-4 )
        # arccosh(30+-4)
        operator = ucomponents.ArcCosh( self.inputRational )
        uncertty = 4.0 / ( numpy.sqrt( 30.0 - 1.0 )*numpy.sqrt( 30.0 + 1.0 ) )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcCosh, 
                                                numpy.arccosh( 30 ), 
                                                uncertty, 
                                                1e-4 )
        # force arithmetic error
        value = ucomponents.UncertainInput( 1.0, 0.0 )
        error = 0
        try:                          
            operator = ucomponents.ArcCosh( value )
        except ArithmeticError:
            error = 1
        assert( error==1 )
                                                
    def test_arcsinh( self ):
        """! @brief Test the Operator ucomponents.ArcSinh.
              @param self                                            
        """
        # arcsinh(10+-2)
        operator = ucomponents.ArcSinh( self.inputLong )
        uncertty = 2.0/numpy.sqrt( 1.0 + 10**2 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcSinh, 
                                                numpy.arcsinh( 10 ), 
                                                uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.ArcSinh, 
                                                    1 )
        # arcsinh(20+-3)
        operator = ucomponents.ArcSinh( self.inputFloat )
        uncertty = 3.0/numpy.sqrt( 1.0 + 20**2 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcSinh, 
                                                numpy.arcsinh( 20 ), 
                                                uncertty, 
                                                1e-4 )
        # arcsinh(30+-4)
        operator = ucomponents.ArcSinh( self.inputRational )
        uncertty = 4.0/numpy.sqrt( 1.0 + 30**2 )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.ArcSinh, 
                                                numpy.arcsinh( 30 ), 
                                                uncertty, 
                                                1e-4 )
    
    def test_exp( self ):
        """! @brief Test the Operator ucomponents.Exp.
              ucomponents.Exp.
              @param self                                            
        """
        # exp(10+-2)
        operator = ucomponents.Exp( self.inputLong )
        uncertty = numpy.exp( 10 )*2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Exp, 
                                                numpy.exp( 10 ), uncertty, 
                                                1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Exp, 
                                                    1 )
        
        # exp(20+-3)
        operator = ucomponents.Exp( self.inputFloat )
        uncertty = numpy.exp( 20 )*3
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Exp, 
                                                numpy.exp( 20 ), uncertty, 
                                                1e-4 )
        # exp(30+-4)
        operator = ucomponents.Exp( self.inputRational )
        uncertty = numpy.exp( 30 )*4
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Exp, 
                                                numpy.exp( 30 ), uncertty, 
                                                1e-4 )
    def test_abs( self ):
        """! @brief Test the Operator ucomponents.Abs.
              @param self                                                
        """
        # abs(10+-2)
        operator = ucomponents.Abs( self.inputLong )
        uncertty = numpy.fabs( self.inputLong.get_uncertainty( 
                              self.inputLong ) )
        value = numpy.fabs( self.inputLong.get_value() )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Abs, 
                                                value, uncertty, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Abs, 
                                                    1 )
        
        # abs(20+-3)
        operator = ucomponents.Abs( self.inputFloat )
        uncertty = numpy.fabs( self.inputFloat.get_uncertainty( 
                                             self.inputFloat ) )
        value = numpy.fabs( self.inputFloat.get_value() )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Abs, 
                                                value, uncertty, 1e-4 )
        # abs(30+-4)
        operator = ucomponents.Abs( self.inputRational )
        uncertty = numpy.fabs( self.inputRational.get_uncertainty( 
                              self.inputRational ) )
        value = numpy.fabs( self.inputRational.get_value() )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Abs, 
                                                value, uncertty, 1e-4 )
                                                
        # Above was trivial, now test some negative stuff
        number = ucomponents.UncertainInput( -10, -2 )
        operator = ucomponents.Abs( number )
        uncertty = numpy.fabs( number.get_uncertainty( number ) )
        value = numpy.fabs( number.get_value() )
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Abs, 
                                                value, uncertty, 1e-4 )

        assert( operator.get_value() == 10.0 )
        assert( operator.get_uncertainty( number ) == 2.0 )
        
    def test_neg( self ):
        """! @brief Test the Operator ucomponents.Neg.
              @param self
        """
        # abs(10+-2)
        operator = ucomponents.Neg( self.inputLong )
        uncertty = -2
        value = -10
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Neg, 
                                                value, uncertty, 1e-4 )
        TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( operator, 
                                                    ucomponents.Neg, 
                                                    1 )
        
        # abs(20+-3)
        operator = ucomponents.Neg( self.inputFloat )
        uncertty = -3
        value = -20
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Neg, 
                                                value, uncertty, 1e-4 )
        # abs(30+-4)
        operator = ucomponents.Neg( self.inputRational )
        uncertty = -4
        value = -30
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Neg, 
                                                value, uncertty, 1e-4 )
                                                
        # Above was trivial, now test some negative stuff
        number = ucomponents.UncertainInput( -10, -2 )
        operator = ucomponents.Neg( number )
        uncertty = 2
        value = 10
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( operator, 
                                                ucomponents.Neg, 
                                                value, uncertty, 1e-4 )

        assert( operator.get_value() == 10.0 )
        assert( operator.get_uncertainty( number ) == 2.0 )
    
    def test_creation( self ):
        """! @brief Test creating scalar uncertain numbers.
              @param self  
        """
        value = ucomponents.UncertainInput( 1.0, 2.0 )
        assert( value.get_value() == 1.0 )
        assert( value.get_uncertainty( value ) == 2.0 )
        value = ucomponents.UncertainInput( 1, 2 )
        assert( value.get_value() == 1 )
        assert( value.get_uncertainty( value ) == 2 )
        value = ucomponents.UncertainInput( arithmetic.RationalNumber( 1, 
                                                                       10 ), 
                                            arithmetic.RationalNumber( 1, 2 ) )
        assert( value.get_value() == arithmetic.RationalNumber( 1, 10 ) )
        assert( value.get_uncertainty( value ) == 
                arithmetic.RationalNumber( 1, 2 ) )

        value = ucomponents.UncertainComponent.value_of( 10 )
        assert( isinstance( value, ucomponents.UncertainInput ) )
        assert( value.get_value() == 10 )
        assert( value.get_uncertainty( value ) == 0 )
        assert( value.get_dof() == arithmetic.INFINITY )
        
        value = ucomponents.UncertainComponent.gaussian( 10, 2 )
        assert( isinstance( value, ucomponents.UncertainInput ) )
        assert( value.get_value() == 10 )
        assert( value.get_uncertainty( value ) == 2 )
        assert( value.get_dof() == arithmetic.INFINITY )

        value = ucomponents.UncertainComponent.beta( 10, 2.0, 2 )
        uncertainty = numpy.sqrt( 2.0*2.0/( ( 2.0+2.0 )**2.0 \
                                  *( 2.0 + 2.0 + 1.0 ) ) )
        assert( isinstance( value, ucomponents.UncertainInput ) )
        assert( value.get_value() == 10 )
        assert( abs( value.get_uncertainty( value ) - uncertainty ) < 1e-4 )
        assert( value.get_dof() == arithmetic.INFINITY )

        value = ucomponents.UncertainComponent.arcsine( 10 )
        uncertainty = numpy.sqrt( 0.5*0.5/( 2.0 ) )
        assert( isinstance( value, ucomponents.UncertainInput ) )
        assert( value.get_value() == 10 )
        assert( abs( value.get_uncertainty( value ) - uncertainty ) < 1e-4 )
        assert( value.get_dof() == arithmetic.INFINITY )
        
        value = ucomponents.UncertainComponent.arcsine( 10, 3 )
        assert( value.get_dof() == 3 )
        value = ucomponents.UncertainComponent.beta( 10, 2.0, 2, 3 )
        assert( value.get_dof() == 3 )
        value = ucomponents.UncertainComponent.gaussian( 10, 2, 3 )
        assert( value.get_dof() == 3 )
        value = ucomponents.UncertainInput( 1.0, 2.0, 3 )
        assert( value.get_dof() == 3 )
        
        
    def test_special_cases( self ):
        """! @brief Test some cases of scalar uncertainties (i.e. @f$sin(x) * x@f$).
              @param self
        """
        x = ucomponents.UncertainInput( 10.0, 1.0 )
        op = ucomponents.Mul( ucomponents.Sin( x ), x )
        
        # check serialization using all available protocols
        for i in range( 0, pickle.HIGHEST_PROTOCOL+1 ):
            # seems like python maintains references
            copy = TestUncertaintyComponents.TEST_COMPONENT_SERIALIZATION( op, 
                                              ucomponents.Mul, 1 )
        
            # is it the same input ?
            assert( len( copy.depends_on() ) == 1 )
            input = copy.depends_on()[0]
            assert( not ( input is x ) )
            assert( input.get_uncertainty( input ) == 1.0 )
            assert( input.get_value() == 10.0 )
        
            # same structure
            left = copy.get_left()
            right = copy.get_right()
            assert( isinstance( left, ucomponents.Sin ) )
            assert( isinstance( right, ucomponents.UncertainInput ) )
            subright = left.get_silbling()
            assert( isinstance( subright, ucomponents.UncertainInput ) )
            # has the identity been maintained
            assert( subright is right )
            
    def test_operator_aliases( self ):
        """! @brief Test operator broadcasting of the Module ucomponents.
              @param self
        """
        # __add__
        result = self.inputFloat + self.inputLong
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( result, 
                                                ucomponents.Add, 
                                                30.0, 5.0, 1e-4 )
        # __sub__
        result = self.inputFloat - self.inputLong
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( result, 
                                                ucomponents.Sub, 
                                                10.0, 1.0, 1e-4 )
        # __mul__
        result = self.inputFloat * self.inputLong
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( result, 
                                                ucomponents.Mul, 
                                                200.0, 70.0, 1e-4 )
        # __div__
        result = self.inputFloat / self.inputLong
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( result, 
                                                ucomponents.Div, 
                                                2.0, -1.0/10.0, 1e-4 )
        # __pow__
        result = self.inputFloat ** self.inputLong
        uncertty =  ( 20**9 )*10*3 + ( 20**10 ) * numpy.log( 20 ) * 2
        TestUncertaintyComponents.TEST_UNCERTAIN_COMPONENT( result, 
                                                ucomponents.Pow, 
                                                20**10, uncertty, 1e-4 )
                                                
        # __radd__
        result = 10 + self.inputFloat
        assert( isinstance( result, ucomponents.Add ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        result = arithmetic.RationalNumber( 10, 1 ) + self.inputFloat
        assert( isinstance( result, ucomponents.Add ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        # __rsub__
        result = 10 - self.inputFloat
        assert( isinstance( result, ucomponents.Sub ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        result = arithmetic.RationalNumber( 10, 1 ) - self.inputFloat
        assert( isinstance( result, ucomponents.Sub ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        # __rmul__
        result = 10 * self.inputFloat
        assert( isinstance( result, ucomponents.Mul ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        result = arithmetic.RationalNumber( 10, 1 ) * self.inputFloat
        assert( isinstance( result, ucomponents.Mul ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        # __rdiv__
        result = 10 / self.inputFloat
        assert( isinstance( result, ucomponents.Div ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        # rational numbers
        result = arithmetic.RationalNumber( 10, 1 ) / self.inputFloat
        assert( isinstance( result, ucomponents.Div ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        # __rpow__
        result = 10 ** self.inputFloat
        assert( isinstance( result, ucomponents.Pow ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
        
        # abs(20+-3)
        result = abs( self.inputFloat )
        assert( isinstance( result, ucomponents.Abs ) )
        silbling = result.get_silbling()
        assert( isinstance( silbling, ucomponents.UncertainInput ) )
        assert( silbling == self.inputFloat )
        assert( result.get_value() == 20 )
        
        # neg(20+-3)
        result = -self.inputFloat
        assert( isinstance( result, ucomponents.Neg ) )
        silbling = result.get_silbling()
        assert( isinstance( silbling, ucomponents.UncertainInput ) )
        assert( silbling == self.inputFloat )
        assert( result.get_value() == -20 )
        
        # rational numbers
        result = arithmetic.RationalNumber( 10, 1 ) ** self.inputFloat
        assert( isinstance( result, ucomponents.Pow ) )
        right = result.get_right()
        left  = result.get_left()
        assert( isinstance( right, ucomponents.UncertainInput ) )
        assert( isinstance( left, ucomponents.UncertainInput ) )
        assert( right == self.inputFloat )
        assert( left.get_value() == 10 )
    
    def test_numpy_broadcast( self ):
        """! @brief Test numpy broadcasting of the Module ucomponents.
              @param self
        """
        value1_1 = ucomponents.UncertainInput( 1.1, 0.0 )
        value0_9 = ucomponents.UncertainInput( 0.9, 0.0 )
        
        result = numpy.add( value1_1, value0_9 )
        assert( isinstance( result, ucomponents.Add ) )
        assert( result.get_left() is value1_1 )
        assert( result.get_right() is value0_9 )
        
        result = numpy.subtract( value1_1, value0_9 )
        assert( isinstance( result, ucomponents.Sub ) )
        assert( result.get_left() is value1_1 )
        assert( result.get_right() is value0_9 )

        result = numpy.multiply( value1_1, value0_9 )
        assert( isinstance( result, ucomponents.Mul ) )
        assert( result.get_left() is value1_1 )
        assert( result.get_right() is value0_9 )
        
        result = numpy.divide( value1_1, value0_9 )
        assert( isinstance( result, ucomponents.Div ) )
        assert( result.get_left() is value1_1 )
        assert( result.get_right() is value0_9 )
        
        result = numpy.power( value1_1, value0_9 )
        assert( isinstance( result, ucomponents.Pow ) )
        assert( result.get_left() is value1_1 )
        assert( result.get_right() is value0_9 )
        
        result = numpy.arccos( value0_9 )
        assert( isinstance( result, ucomponents.ArcCos ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.arccosh( value1_1 )
        assert( isinstance( result, ucomponents.ArcCosh ) )
        assert( result.get_silbling() is value1_1 )
        
        result = numpy.arcsin( value0_9 )
        assert( isinstance( result, ucomponents.ArcSin ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.arcsinh( value0_9 )
        assert( isinstance( result, ucomponents.ArcSinh ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.arctan( value0_9 )
        assert( isinstance( result, ucomponents.ArcTan ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.arctanh( value0_9 )
        assert( isinstance( result, ucomponents.ArcTanh ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.cos( value0_9 )
        assert( isinstance( result, ucomponents.Cos ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.cosh( value0_9 )
        assert( isinstance( result, ucomponents.Cosh ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.tan( value0_9 )
        assert( isinstance( result, ucomponents.Tan ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.tanh( value0_9 )
        assert( isinstance( result, ucomponents.Tanh ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.log10( value0_9 )
        assert( isinstance( result, ucomponents.Div ) )
        left = result.get_left()
        right = result.get_right()
        assert( isinstance( left, ucomponents.Log ) )
        assert( isinstance( right, ucomponents.Log ) )
        assert( left.get_silbling() is value0_9 )
        
        result = numpy.sin( value0_9 )
        assert( isinstance( result, ucomponents.Sin ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.sinh( value0_9 )
        assert( isinstance( result, ucomponents.Sinh ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.sqrt( value0_9 )
        assert( isinstance( result, ucomponents.Sqrt ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.absolute( value0_9 )
        assert( isinstance( result, ucomponents.Abs ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.fabs( value0_9 )
        assert( isinstance( result, ucomponents.Abs ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.exp( value0_9 )
        assert( isinstance( result, ucomponents.Exp ) )
        assert( result.get_silbling() is value0_9 )
        
        result = numpy.log( value0_9 )
        assert( isinstance( result, ucomponents.Log ) )
        assert( result.get_silbling() is value0_9 )
        
        error = 0
        try:
            result = numpy.remainder( value1_1, value0_9 )
        except TypeError:
            error = 1
        assert( error==0 )
        
        error = 0
        try:
            result = numpy.floor( value0_9 )
        except AttributeError:
            error = 1
        assert( error==0 )
        
        error = 0
        try:
            result = numpy.ceil( value0_9 )
        except AttributeError:
            error = 1
        assert( error==0 )
        
        error = 0
        try:
            result = numpy.fmod( value0_9, value1_1 )
        except AttributeError:
            error = 1
        assert( error==0 )
        
        error = 0
        try:
            result = numpy.conjugate( value0_9 )
        except AttributeError:
            error = 1
        assert( error==0 )

class TestComplexUncertaintyComponents( unittest.TestCase ): 
    """! @brief This class provides test-cases for the Module cucomponents.
        @see cucomponents
    """

    class OperationTest:
        """! @brief This is the abstract super class for testing all
        operations of the Module cucomponents.
        @see cucomponents
        """
        
        def __init__(self, component, dtype, value, uncertainty, 
                      dependents, max_err = 1e-6):
            """! @brief The Default Constructor
        @param self
        @param component The component to test.
        @param dtype The type of the component.
        @param value The expected value of the component.
        @param uncertainty The expected uncertainty of the component.
        @param dependents A list of components this component depends on.
        @param max_err The maximum acceptable numeric error.
        """
            self.__component   = component
            self.__type        = dtype
            self.__value       = value
            self.__uncertainty = uncertainty
            self.__dependents  = dependents
            self.__max_err     = max_err
            
            # self test
            assert(float(self.__max_err) == self.__max_err)
            
            # individual tests
            self.test_type()
            self.test_value()
            self.test_uncertainty()
            self.test_dependencies()
    
        def get_component(self):
            """! @brief This method returns the component to be tested.
            @param self
            @return The component that is currently tested.
            """
            return self.__component
        
        def get_max_error(self):
            """! @brief This method returns the maximum allowable error.
            @param self
            @return The maximum allowable error.
            """
            return self.__max_err
            
        def test_type(self):
            """! @brief This method checks for the type
            @param self
            """
            # self test
            assert(isinstance(self.__component, 
                    cucomponents.CUncertainComponent))
            # component test
            assert(isinstance(self.__component,
                              self.__type))
                              
        def test_uncertainty(self):
            """! @brief This method checks for the correct value.
            @param self
            """
            # self test
            assert(isinstance(self.__uncertainty, numpy.matrix))
            assert(self.__uncertainty.shape == (2, 2))
            assert(self.__uncertainty.dtype == float)
            
            e = self.__max_err
            desired_error = numpy.matrix([[e, e],[e, e]])
            
            dummy = cucomponents.CUncertainInput(1.0+0j,0.0,0.0)
            assert(numpy.all(
                    numpy.abs(self.__component.get_uncertainty(dummy)
                               - numpy.zeros((2,2)) < desired_error)))
            
            inputs = self.__component.depends_on()
            sum    = numpy.matrix([[0.0, 0.0],[0.0, 0.0]])
            for i in inputs:
                sum += self.__component.get_uncertainty(i)

            assert(numpy.all(abs(sum - self.__uncertainty) < desired_error))
                    
        def test_value(self):
            """! @brief This method checks for the correct uncertainty propagation.
            @param self
            """
            # self test
            assert(not isinstance(self.__value, quantities.Quantity))
            assert(complex(self.__value) == self.__value)
            
            assert(numpy.abs(self.__component.get_value() - self.__value)
                    < self.__max_err)
            
            # test transform
            e = self.__max_err
            desired_error   = numpy.matrix([[e, e],[e, e]])
            r = self.__value.real
            i = self.__value.imag
            dvalue = numpy.matrix([[r, -i],[i, r]])
            
            assert(numpy.all(numpy.abs(self.__component.get_a_value() - dvalue) <
                    desired_error))
                    
        def test_dependencies(self):
            """! @brief This method checks wheter the dependencies are carried out
            correctly.
            @param self
            """
            # self test
            assert(isinstance(self.__dependents, list))
            for i in self.__dependents:
                assert(isinstance(i, cucomponents.CUncertainInput))
            
            deps = self.__component.depends_on()
            for i in deps:
                assert(isinstance(i, cucomponents.CUncertainInput))
                self.__dependents.remove(i)
            
            assert(len(self.__dependents) == 0)
    
    def setUp(self):
        """! @brief This method sets up the testcase for every individual test.
        @param self
        """
        self.__input_1 = cucomponents.CUncertainInput((1+2j),1.0,2.0)
        self.__input_2 = cucomponents.CUncertainInput((2+3j),2.0,3.0)
        
        # self test
        u = numpy.matrix([[1.0, 0.0],[0.0, 2.0]])
        self.OperationTest(self.__input_1, cucomponents.CUncertainInput, (1+2j), 
                       u, [self.__input_1])
        u = numpy.matrix([[2.0, 0.0],[0.0, 3.0]])
        self.OperationTest(self.__input_2, cucomponents.CUncertainInput, (2+3j), 
                       u, [self.__input_2])

    def test_exp(self): 
        """! @brief Test instances of cucomponents.Exp.
        @see cucomponents.Exp
        """
    
        depends     = [self.__input_1]
        value       = -1.1312043837568135+2.4717266720048188j
        uncertainty = numpy.matrix([
                      [-1.1312043837568135, -2.4717266720048188*2.0],
                      [2.4717266720048188, -1.1312043837568135*2.0]])
        
        # Test direct invocation
        t = cucomponents.Exp(self.__input_1)
        self.OperationTest(t, cucomponents.Exp, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.exp(self.__input_1)
        self.OperationTest(t, cucomponents.Exp, value, uncertainty, 
                            [self.__input_1])
                     
    def test_log(self):
        """! @brief Test instances of cucomponents.Log.
        @see cucomponents.Log
        """
        depends     = [self.__input_1]
        value       = 0.34948500216800943+0.48082857878423407j
        diff        = 1.0/((1+2j) * numpy.log(10.0))
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Log(self.__input_1, 10)
        self.OperationTest(t, cucomponents.Log, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.log10(self.__input_1)
        self.OperationTest(t, cucomponents.Log, value, uncertainty, 
                            [self.__input_1])
                                           
    def test_sqrt(self):
        """! @brief Test instances of cucomponents.Sqrt.
        @see cucomponents.Sqrt
        """
        
        depends     = [self.__input_1]
        value       = 1.272019649514069+0.78615137775742328j
        diff        = 0.5/numpy.sqrt(1+2j)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Sqrt(self.__input_1)
        self.OperationTest(t, cucomponents.Sqrt, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.sqrt(self.__input_1)
        self.OperationTest(t, cucomponents.Sqrt, value, uncertainty, 
                            [self.__input_1])
                             
    def test_sin(self):
        """! @brief Test instances of cucomponents.Sin.
        @see cucomponents.Sin
        """
    
        depends     = [self.__input_1]
        value       = 3.1657785132161682+1.9596010414216061j
        diff        = numpy.cos(1+2j)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Sin(self.__input_1)
        self.OperationTest(t, cucomponents.Sin, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.sin(self.__input_1)
        self.OperationTest(t, cucomponents.Sin, value, uncertainty, 
                            [self.__input_1])
                                          
    def test_cos(self):
        """! @brief Test instances of cucomponents.Cos.
    @see cucomponents.Cos
    """

        depends     = [self.__input_1]
        value       = 2.0327230+3.0518977j
        value       = 2.0327230070196656-3.0518977991517997j
        diff        = -numpy.sin(1+2j)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Cos(self.__input_1)
        self.OperationTest(t, cucomponents.Cos, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.cos(self.__input_1)
        self.OperationTest(t, cucomponents.Cos, value, uncertainty, 
                            [self.__input_1])
                                                
    def test_tan(self):
        """! @brief Test instances of cucomponents.Tan.
        @see cucomponents.Tan
        """
    
        depends     = [self.__input_1]
        value       = 0.033812826079896725+1.0147936161466335j
        diff        = 1.0/numpy.cos(1+2j)**2.0
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Tan(self.__input_1)
        self.OperationTest(t, cucomponents.Tan, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.tan(self.__input_1)
        self.OperationTest(t, cucomponents.Tan, value, uncertainty, 
                            [self.__input_1])
                          
    def test_arcsin(self):
        """! @brief Test instances of cucomponents.ArcSin.
        @see cucomponents.ArcSin
        """
        
        depends     = [self.__input_1]
        value       = 0.42707858639247592+1.5285709194809975j
        diff        = 1.0/numpy.sqrt(1.0 - (1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.ArcSin(self.__input_1)
        self.OperationTest(t, cucomponents.ArcSin, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.arcsin(self.__input_1)
        self.OperationTest(t, cucomponents.ArcSin, value, uncertainty, 
                            [self.__input_1])
                                            
    def test_arccos(self):
        """! @brief Test instances of cucomponents.ArcCos.
        @see cucomponents.ArcCos
        """
    
        depends     = [self.__input_1]
        value       = 1.1437177404024206-1.528570919480998j
        diff        = -1.0/numpy.sqrt(1.0 - (1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.ArcCos(self.__input_1)
        self.OperationTest(t, cucomponents.ArcCos, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.arccos(self.__input_1)
        self.OperationTest(t, cucomponents.ArcCos, value, uncertainty, 
                            [self.__input_1])
                                            
    def test_arctan(self):
        """! @brief Test instances of cucomponents.ArcTan.
        @see cucomponents.ArcTan
        """
        
        depends     = [self.__input_1]
        value       = 1.3389725222944935+0.40235947810852513j
        diff        = -1.0/(1.0 + (1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.ArcTan(self.__input_1)
        self.OperationTest(t, cucomponents.ArcTan, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.arctan(self.__input_1)
        self.OperationTest(t, cucomponents.ArcTan, value, uncertainty, 
                            [self.__input_1])
                                          
    def test_sinh(self):
        """! @brief Test instances of cucomponents.Sinh.
        @see cucomponents.Sinh
        """
    
        depends     = [self.__input_1]
        value       = -0.48905625904129368+1.4031192506220405j
        diff        = numpy.cosh(1+2j)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Sinh(self.__input_1)
        self.OperationTest(t, cucomponents.Sinh, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.sinh(self.__input_1)
        self.OperationTest(t, cucomponents.Sinh, value, uncertainty, 
                            [self.__input_1])
                                      
    def test_cosh(self):
        """! @brief Test instances of cucomponents.Cosh.
        @see cucomponents.Cosh
        """
    
        depends     = [self.__input_1]
        value       = -0.64214812471551996+1.0686074213827783j
        diff        = numpy.sinh(1+2j)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Cosh(self.__input_1)
        self.OperationTest(t, cucomponents.Cosh, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.cosh(self.__input_1)
        self.OperationTest(t, cucomponents.Cosh, value, uncertainty, 
                            [self.__input_1])
                                              
    def test_tanh(self):
        """! @brief Test instances of cucomponents.Tanh.
        @see cucomponents.Tanh
        """
    
        depends     = [self.__input_1]
        value       = 1.1667362572409199-0.24345820118572528j
        diff        = 1.0/numpy.cosh(1+2j)**2
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Tanh(self.__input_1)
        self.OperationTest(t, cucomponents.Tanh, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.tanh(self.__input_1)
        self.OperationTest(t, cucomponents.Tanh, value, uncertainty, 
                            [self.__input_1])
                                              
    def test_arcsinh(self):
        """! @brief Test instances of cucomponents.ArcSinh.
        @see cucomponents.ArcSinh
        """
        
        depends     = [self.__input_1]
        value       = 1.4693517443681854+1.0634400235777521j
        diff        = 1.0/numpy.sqrt(1.0+(1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.ArcSinh(self.__input_1)
        self.OperationTest(t, cucomponents.ArcSinh, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.arcsinh(self.__input_1)
        self.OperationTest(t, cucomponents.ArcSinh, value, uncertainty, 
                            [self.__input_1])
                                              
    def test_arccosh(self):
        """! @brief Test instances of cucomponents.ArcCosh.
        @see cucomponents.ArcCosh
        """
        
        depends     = [self.__input_1]
        value       = 1.528570919480998+1.1437177404024206j
        diff        = 1.0/(numpy.sqrt(1.0+(1+2j))*numpy.sqrt((1+2j)-1.0))
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.ArcCosh(self.__input_1)
        self.OperationTest(t, cucomponents.ArcCosh, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.arccosh(self.__input_1)
        self.OperationTest(t, cucomponents.ArcCosh, value, uncertainty, 
                            [self.__input_1])
                     
    def test_arctanh(self):
        """! @brief Test instances of cucomponents.ArcTanh.
        @see cucomponents.ArcTanh
        """
        
        depends     = [self.__input_1]
        value       = 0.17328679513998635+1.1780972450961724j
        diff        = 1.0/(1.0-(1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.ArcTanh(self.__input_1)
        self.OperationTest(t, cucomponents.ArcTanh, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.arctanh(self.__input_1)
        self.OperationTest(t, cucomponents.ArcTanh, value, uncertainty, 
                            [self.__input_1])
                                               
    def test_abs(self):
        """! @brief Test instances of cucomponents.Abs.
        @see cucomponents.Abs
        """
        
        depends     = [self.__input_1]
        value       = complex(2.2360679774997898)
        uncertainty = numpy.matrix([
                      [0.2, 0.4*2.0],
                      [0, 0]])
        
        # Test direct invocation
        t = cucomponents.Abs(self.__input_1)
        self.OperationTest(t, cucomponents.Abs, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.abs(self.__input_1)
        self.OperationTest(t, cucomponents.Abs, value, uncertainty, 
                            [self.__input_1])
                                            
    def test_conjugate(self):
        """! @brief Test instances of cucomponents.Conjugate.
        @see cucomponents.Conjugate
        """
        
        depends     = [self.__input_1]
        value       = 1-2j
        uncertainty = numpy.matrix([
                      [1.0,  0],
                      [0, -2]])
        
        # Test direct invocation
        t = cucomponents.Conjugate(self.__input_1)
        self.OperationTest(t, cucomponents.Conjugate, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = numpy.conj(self.__input_1)
        self.OperationTest(t, cucomponents.Conjugate, value, uncertainty, 
                            [self.__input_1])
        t = numpy.conjugate(self.__input_1)
        self.OperationTest(t, cucomponents.Conjugate, value, uncertainty, 
                            [self.__input_1])
                                           
    def test_neg(self):
        """! @brief Test instances of cucomponents.Neg.
        @see cucomponents.Neg
        """
        depends     = [self.__input_1]
        value       = -1-2j
        uncertainty = numpy.matrix([
                      [-1.0,  0],
                      [0, -2]])
        
        # Test direct invocation
        t = cucomponents.Neg(self.__input_1)
        self.OperationTest(t, cucomponents.Neg, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = -self.__input_1
        self.OperationTest(t, cucomponents.Neg, value, uncertainty, 
                            [self.__input_1])
                                                                 
    def test_inv(self):
        """! @brief Test instances of cucomponents.Inv.
        @see cucomponents.Inv
        """
        depends     = [self.__input_1]
        value       = 1.0/(1+2j)
        diff        = -1.0/((1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff.real, -diff.imag*2.0],
                      [diff.imag, diff.real*2.0]])
        
        # Test direct invocation
        t = cucomponents.Inv(self.__input_1)
        self.OperationTest(t, cucomponents.Inv, value, uncertainty, 
                            [self.__input_1])
        
        # Test numpy integration
        t = ~self.__input_1
        self.OperationTest(t, cucomponents.Inv, value, uncertainty, 
                            [self.__input_1])
                        
    def test_add(self): 
        """! @brief Test instances of cucomponents.Add.
        @see cucomponents.Add
        """
        depends     = [self.__input_1,self.__input_2]
        value       = (1+2j)+(2+3j)
        diff        = -1.0/((1+2j)**2)
        uncertainty = numpy.matrix([
                      [3.0, 0.0],
                      [0.0, 5.0]])
        
        # Test direct invocation
        t = cucomponents.Add(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.Add, value, uncertainty, 
                            [self.__input_1,self.__input_2])
        
        # Test numpy integration
        t = self.__input_1 + self.__input_2
        self.OperationTest(t, cucomponents.Add, value, uncertainty, 
                            [self.__input_1,self.__input_2])
    
    def test_sub(self):
        """! @brief Test instances of cucomponents.Sub.
        @see cucomponents.Sub
        """
        depends     = [self.__input_1,self.__input_2]
        value       = (1+2j)-(2+3j)
        diff        = -1.0/((1+2j)**2)
        uncertainty = numpy.matrix([
                      [-1.0, 0.0],
                      [0.0, -1.0]])
        
        # Test direct invocation
        t = cucomponents.Sub(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.Sub, value, uncertainty, 
                            [self.__input_1,self.__input_2])
        
        # Test numpy integration
        t = self.__input_1 - self.__input_2
        self.OperationTest(t, cucomponents.Sub, value, uncertainty, 
                            [self.__input_1,self.__input_2])
    
    def test_mul(self):
        """! @brief Test instances of cucomponents.Mul.
        @see cucomponents.Mul
        """
        depends     = [self.__input_1,self.__input_2]
        value       = (1+2j)*(2+3j)
        diff        = -1.0/((1+2j)**2)
        uncertainty = numpy.matrix([
                      [2.0, -3.0*2.0],
                      [3.0, 2.0*2.0]]) + numpy.matrix([
                      [1.0*2.0, -2.0*3.0],
                      [2.0*2.0, 1.0*3.0]])
        
        # Test direct invocation
        t = cucomponents.Mul(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.Mul, value, uncertainty, 
                            [self.__input_1,self.__input_2])
        
        # Test numpy integration
        t = self.__input_1 * self.__input_2
        self.OperationTest(t, cucomponents.Mul, value, uncertainty, 
                            [self.__input_1,self.__input_2])
    
    def test_div(self):
        """! @brief Test instances of cucomponents.Div.
        @see cucomponents.Div
        """
        depends     = [self.__input_1,self.__input_2]
        value       = (1+2j)/(2+3j)
        diff_1      = 1.0/(2+3j)
        diff_2      = -1.0*(1+2j)/(2+3j)**2
        uncertainty = numpy.matrix([
                      [diff_1.real, -diff_1.imag*2.0],
                      [diff_1.imag, diff_1.real*2.0]]) \
                    + numpy.matrix([
                      [diff_2.real*2.0, -diff_2.imag*3.0],
                      [diff_2.imag*2.0, diff_2.real*3.0]])
        
        # Test direct invocation
        t = cucomponents.Div(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.Div, value, uncertainty, 
                            [self.__input_1,self.__input_2])
        
        # Test numpy integration
        t = self.__input_1 / self.__input_2
        self.OperationTest(t, cucomponents.Div, value, uncertainty, 
                            [self.__input_1,self.__input_2])
    
    def test_pow(self):
        """! @brief Test instances of cucomponents.Pow.
        @see cucomponents.Pow
        """
        depends     = [self.__input_1,self.__input_2]
        value       = (1+2j)**(2+3j)
        diff_1      = (2+3j)*(1+2j)**(1+3j)
        diff_2      = (1+2j)**(2+3j)*numpy.log(1+2j)
        uncertainty = numpy.matrix([
                      [diff_1.real, -diff_1.imag*2.0],
                      [diff_1.imag, diff_1.real*2.0]]) \
                    + numpy.matrix([
                      [diff_2.real*2.0, -diff_2.imag*3.0],
                      [diff_2.imag*2.0, diff_2.real*3.0]])
        
        # Test direct invocation
        t = cucomponents.Pow(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.Pow, value, uncertainty, 
                            [self.__input_1,self.__input_2])
        
        # Test numpy integration
        t = self.__input_1 ** self.__input_2
        self.OperationTest(t, cucomponents.Pow, value, uncertainty, 
                            [self.__input_1,self.__input_2])
    
    def test_atan2(self):
        """! @brief Test instances of cucomponents.ArcTan2.
        @see cucomponents.ArcTan2
        """
        depends     = [self.__input_1,self.__input_2]
        value       = (0-1j) * numpy.log(((1+2j) + (0-1j)*(2+3j)) \
                                 /numpy.sqrt((1+2j)**2 + (2+3j)**2))
        diff_1      = (2+3j)/((2+3j)**2+(1+2j)**2)
        diff_2      = (1+2j)/((2+3j)**2+(1+2j)**2)
        uncertainty = numpy.matrix([
                      [diff_1.real, -diff_1.imag*2.0],
                      [diff_1.imag, diff_1.real*2.0]]) \
                    + numpy.matrix([
                      [diff_2.real*2.0, -diff_2.imag*3.0],
                      [diff_2.imag*2.0, diff_2.real*3.0]])
        
        # Test direct invocation
        t = cucomponents.ArcTan2(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.ArcTan2, value, uncertainty, 
                            [self.__input_1,self.__input_2])
        
        # Test numpy integration
        t = numpy.arctan2(self.__input_1, self.__input_2)
        self.OperationTest(t, cucomponents.ArcTan2, value, uncertainty, 
                            [self.__input_1,self.__input_2])
                            
    def test_context(self):
        """! @brief Test correlating / creating complex-valued uncertain components.
        @see cucomponents.Context
        """
        c = cucomponents.Context()
        
        # Test uncorrelated inputs
        cor_1 = c.get_correlation(self.__input_1,self.__input_2)
        cor_2 = c.get_correlation(self.__input_2,self.__input_1)
        assert(numpy.all(cor_1 == numpy.zeros((2,2))))
        assert(numpy.all(cor_2 == numpy.zeros((2,2))))
        assert(self.__input_1.get_context() == None)
        assert(self.__input_2.get_context() == None)
        
        # Set correlation, test symmetry
        corr = numpy.matrix([[1,0.5],[0.5,1.0]])
        c.set_correlation(self.__input_1,self.__input_2, corr)
        
        cor_1 = c.get_correlation(self.__input_1,self.__input_2)
        cor_2 = c.get_correlation(self.__input_2,self.__input_1)
        
        assert(numpy.all(cor_1 == cor_2))
        assert(numpy.all(corr == cor_2))
        assert(self.__input_1.get_context() == c)
        assert(self.__input_2.get_context() == c)
        
        # Test identity
        id = c.get_correlation(self.__input_1, self.__input_1)
        my_id = numpy.matrix([[1.0,0.0],[0.0,1.0]])
        assert(numpy.all(id == my_id))
        
        # Test creation
        corr   = numpy.matrix([[1.0, 0.5],[0.5, 1.0]])
        var = c.gaussian(1.0, 2.0, 3.0, 1.0, corr)
        uncert = numpy.matrix([[2.0, 0.0],[0.0, 3.0]])
        self.OperationTest(var, cucomponents.CUncertainInput, complex(1.0), 
                            uncert, [var])
        assert(numpy.all(c.get_correlation(var,var) == corr))
        
    def test_quantities(self):
        """! @brief Test the integration of quantities of the Module cucomponents.
        @see cucomponents.Context
        """
        return  

class TestGUMTree( unittest.TestCase ):
    """! @brief These classes test the function of the global elements of the
      GUM-tree, namely the Context class.
    """
    
    def test_correlations( self ):
        """! @brief Test correlating scalar uncertain components.
              @param self
              @see ucomponents.Context.set_correlation
              @see ucomponents.Context.get_correlation
        """
        input1 = ucomponents.UncertainInput( 1.0, 0.5 )
        input2 = ucomponents.UncertainInput( 0.5, 1.0 )
        aliarcsinput1 = input1
        q1     = quantities.Quantity(si.NEWTON, input1)
        q2     = quantities.Quantity(si.NEWTON, input2)
        
        # no corelation known beforehand
        someContext = ucomponents.Context()
        corr = someContext.get_correlation( input1, input2 )
        assert( corr == 0.0 )
        corr = someContext.get_correlation( input2, input1 )
        assert( corr == 0.0 )
        
        # autocorrelation
        corr = someContext.get_correlation( input1, input1 )
        assert( corr == 1.0 )
        corr = someContext.get_correlation( input2, input2 )
        assert( corr == 1.0 )
        corr = someContext.get_correlation( aliarcsinput1, input1 )
        assert( corr == 1.0 )
        
        # defined correlation
        someContext.set_correlation( input1, input2, 0.5 )
        corr = someContext.get_correlation( input1, input2 )
        assert( corr == 0.5 )
        # symmetry
        corr = someContext.get_correlation( input2, input1 )
        assert( corr == 0.5 )
        
        # reset correlation
        someContext.set_correlation( input1, input2, 1.5 )
        corr = someContext.get_correlation( input1, input2 )
        assert( corr == 1.5 )
        # symmetry
        corr = someContext.get_correlation( input2, input1 )
        assert( corr == 1.5 )
        
        # quantities
        corr = someContext.get_correlation( q1, q2 )
        assert( corr == 1.5 )
        # symmetry
        corr = someContext.get_correlation( q2, q1 )
        assert( corr == 1.5 )
        
        # reset correlation
        someContext.set_correlation( input1, input2, 2.5 )
        corr = someContext.get_correlation( input1, input2 )
        assert( corr == 2.5 )
    
    def test_GUM_integration( self ):
        """! @brief Check the Module ucomponents by evaluating a GUM-example.
              @param self
              @see "Guidlines for Evaluating and Expressing the uncertainty
                    in Measurements"; B.N.Taylor and C.E. Kuyatt; NIST 1297 (1994)
        """
        someContext = ucomponents.Context()
        
        V   = ucomponents.UncertainInput( 4.999, 0.0032 )
        I   = ucomponents.UncertainInput( 19.661e-3, 0.0095e-3 )
        phi = ucomponents.UncertainInput( 1.04446, 0.00075 )
        
        someContext.set_correlation( V, I, -0.36 )
        someContext.set_correlation( V, phi, 0.86 )
        someContext.set_correlation( I, phi, -0.65 )
        
        R = V * ucomponents.Cos( phi ) / I
        X = V * ucomponents.Sin( phi ) / I
        Z = V / I
        
        #print
        #print "R = ",R.get_value()," (",someContext.uncertainty(R),")"
        #print "X = ",Z.get_value()," (",someContext.uncertainty(X),")"
        #print "Z = ",Z.get_value()," (",someContext.uncertainty(Z),")"
        
        # check model correctness
        assert( abs( R.get_value() - 127.732169928 ) < 5e-9 )
        assert( abs( X.get_value() - 219.846511913 ) < 5e-9 )
        assert( abs( Z.get_value() - 254.259701948 ) < 5e-9 )
        
        assert( abs( someContext.uncertainty( R ) - 0.069978727988 ) < 5e-9 )
        assert( abs( someContext.uncertainty( X ) - 0.295716826846 ) < 5e-9 )
        assert( abs( someContext.uncertainty( Z ) - 0.236602971835 ) < 5e-9 )
        
        
    def test_GUM_tree_example( self ):
        """! @brief Check the Module ucomponents by evaluating another GUM-example.
              @param self
              @see "Guidlines for Evaluating and Expressing the uncertainty
                    in Measurements"; B.N.Taylor and C.E. Kuyatt; NIST 1297 (1994)
        """
        someContext = ucomponents.Context()
        
        # Voltage
        v   = 5.0
        # uncertainty of the Voltage
        u_v = 0.01
        # Resistance
        r   = 50.0
        # uncertainty of the resistance
        u_r = 0.1
        # Dissipated Power
        p = v**2/r
        # Standard uncertainty
        u_c = v/r * numpy.sqrt( 4.0*u_v**2 + v**2/r**2 * u_r**2 )
        
        #Same Model using GUM-Tree
        V   = ucomponents.UncertainInput( 5.0, 0.01 )
        R   = ucomponents.UncertainInput( 50, 0.10 )
        
        P   = V ** 2 / R
        assert( abs( P.get_value() - p ) < 1e-4 )
        assert( abs( someContext.uncertainty( P ) - u_c ) < 1e-4 )
        
    def test_automatic_differentiation_example( self ):
        """! @brief Check the Module ucomponents by evaluating an example from a paper.
              @param self
              @see "Calculating measurement uncertainty using automatic
                    differentiation"; B.D.Hall; 
                    Measurement Science Technology Issue 13 (2002)
        """
        someContext = ucomponents.Context()
        
        x1 = ucomponents.UncertainInput( 4.9990, 0.0032 )
        x2 = ucomponents.UncertainInput( 19.661e-3, 0.0095e-3 )
        x3 = ucomponents.UncertainInput( 1.04446, 0.00075 )
        
        someContext.set_correlation( x1, x2, -0.36 )
        someContext.set_correlation( x1, x3, 0.86 )
        someContext.set_correlation( x2, x3, -0.65 )
        
        model = x1 * ucomponents.Cos( x3 ) / x2
        
        assert( abs( model.get_value() - 127.732 ) < 5e-3 )
        assert( abs( someContext.uncertainty( model ) - 0.0699787 ) < 5e-7 )
        assert( abs( model.get_uncertainty( x1 ) - 0.0817649 ) < 5e-7 )
        assert( abs( model.get_uncertainty( x2 ) + 0.0617189 ) < 5e-7 )
        assert( abs( model.get_uncertainty( x3 ) + 0.164885 ) < 5e-6 )
        
    def test_GUM_example( self ):
        """! @brief Check the Module ucomponents by evaluating another GUM-example.
              @param self
              @see ISO GUM
        """
        someContext = ucomponents.Context()
        
        nanometer = si.METER / 1e+9
        celsius   = si.CELSIUS
        
        l_s       = quantities.Quantity( nanometer, 
                    ucomponents.UncertainComponent.gaussian( 5e+7, 25, 18 ) )
        d_1       = quantities.Quantity( nanometer, 
                    ucomponents.UncertainComponent.gaussian( 0.0, 5.8, 24 ) )
        d_2       = quantities.Quantity( nanometer, 
                    ucomponents.UncertainComponent.gaussian( 0.0, 3.9, 5 ) )
        d_3       = quantities.Quantity( nanometer, 
                    ucomponents.UncertainComponent.gaussian( 0.0, 6.7, 8 ) )
                    
        alpha_s   = quantities.Quantity( units.ONE / celsius, 
                    ucomponents.UncertainComponent.uniform( 11.5e-6, 2e-6 ) )
        theta_1   = quantities.Quantity( celsius, 
                    ucomponents.UncertainComponent.gaussian( 0.1, 0.2 ) )
        theta_2   = quantities.Quantity( celsius, 
                    ucomponents.UncertainComponent.arcsine( 0.0 ) )
        delta_alpha = quantities.Quantity( units.ONE / celsius, 
                      ucomponents.UncertainComponent.uniform( 0.0, 1e-6, 50 ) )
        delta_theta = quantities.Quantity( celsius, 
                      ucomponents.UncertainComponent.uniform( 0.0, 0.05, 2 ) )
        
        d = d_1 + d_2 + d_3
        
        #alpha_s
        # value from the GUM
        desired_alpha_s = quantities.Quantity( units.ONE / celsius, 1.2e-6 )
        # error of the GUM value (due to statement)
        mu_alpha_s      = quantities.Quantity( units.ONE / celsius, 0.5e-7 )
        assert( someContext.uncertainty( alpha_s ) - 
                desired_alpha_s < mu_alpha_s )
        
        #delta_alpha
        # value from the GUM
        desired_delta_alpha = quantities.Quantity( units.ONE / celsius, 
                                                   0.58e-6 )
        # error of the GUM value (due to statement)
        mu_delta_alpha      = quantities.Quantity( units.ONE / celsius, 
                                                   0.005e-6 )
        assert( abs( someContext.uncertainty( delta_alpha ) - 
                desired_delta_alpha ) < mu_delta_alpha )
        
        theta = theta_1 + theta_2
        
        #theta
        # value from the GUM
        desired_theta  = quantities.Quantity( celsius, 0.41 )
        # error of the GUM value (due to statement)
        mu_theta       = quantities.Quantity( celsius, 0.005 )
        assert( abs( someContext.uncertainty( theta ) - desired_theta ) 
                < mu_theta )
        
        tmp1  = -l_s * theta * delta_alpha
        
        #-l_s * theta * delta_alpha
        # value from the GUM
        desired_tmp1 = quantities.Quantity( nanometer, 2.9 )
        # error of the GUM value (due to statement)
        mu_tmp1      = quantities.Quantity( nanometer, 0.05 )
        assert( abs( someContext.uncertainty( tmp1 ) - desired_tmp1 ) 
                < mu_tmp1 )
        
        tmp2  = l_s * alpha_s * delta_theta
                
        #l_s * alpha_s * delta_theta
        # value from the GUM
        desired_tmp2 = quantities.Quantity( nanometer, 16.6 )
        # error of the GUM value (due to statement)
        mu_tmp2      = quantities.Quantity( nanometer, 0.05 )
        assert( abs( someContext.uncertainty( tmp2 ) - desired_tmp2 ) 
                < mu_tmp2 )
        
        l = l_s + d + tmp1 + tmp2
        
        #All together
        # value from the GUM
        desired_l    = quantities.Quantity( nanometer, 32 )
        # error of the GUM value (due to statement)
        mu_l         = quantities.Quantity( nanometer, 0.5 )
        assert( abs( someContext.uncertainty( l ) - desired_l ) < mu_l )
        
#        print
#        print "u(alpha_s):",someContext.uncertainty(alpha_s)
#        print "u(delta_alpha):",someContext.uncertainty(delta_alpha)
#        print "u(theta):",someContext.uncertainty(theta)
#        print "u(-l_s * delta_alpha * theta):",someContext.uncertainty(tmp1)
#        print "u(l_s * alpha_s * delta_theta):",someContext.uncertainty(tmp2)
#        print "u(l):",someContext.uncertainty(l)
#        print "dof(l)",someContext.dof(l)

    def testByGUMComplexExample(self):
        """! @brief Check the Module ucomponents by evaluating a ByGUM-example.
              @param self
              @see "ByGUM: A Python software package for calculating measurement uncertainty";
                        B. D. Hall; Industral Research Limited Report 1305; 2005
        """
        c   = cucomponents.Context()
        _J_ = c.constant(0+1j)
        
        # Values from the manual
        V   = c.gaussian(4.999, 0.003209, 0.0)
        I   = c.gaussian(19.661e-3, 9.47e-6, 0.0)
        PHI = c.gaussian(1.04446, 7.521e-4, 0)
        
#        print V
#        print I
#        print PHI
        
        c.set_correlation(V, I, numpy.matrix([[-0.36,0.0],[0.0,0.0]]))
        c.set_correlation(V, PHI, numpy.matrix([[0.86,0.0],[0.0,0.0]]))
        c.set_correlation(I, PHI, numpy.matrix([[-0.65,0.0],[0.0,0.0]]))
        
        z = V * numpy.exp( _J_ * PHI) / I
        
        # The values from the manual
        desired_value = 127.732169928 + 219.846511913j
        desired_covm  = numpy.matrix([[ 0.00493636, -0.01237897],
                                      [-0.01237897,  0.08766197]])
                                      
        # Maximum acceptable error
        desired_err   = numpy.matrix([[ 1e-8, 1e-8],
                                      [ 1e-8, 1e-8]])
                                      
        assert(numpy.abs(desired_value - z.get_value()) < 1e-5)
        assert(numpy.all(numpy.abs(c.uncertainty(z) - desired_covm) 
                < desired_err))
                
    def testByGUMComplexExampleU(self):
        """! @brief Check the Module ucomponents by evaluating a ByGUM-example using units.
              @param self
              @see "ByGUM: A Python software package for calculating measurement uncertainty";
                        B. D. Hall; Industral Research Limited Report 1305; 2005
        """
        c   = cucomponents.Context()
        _J_ = quantities.Quantity(units.ONE, c.constant(0+1j))
        
        # Values from the manual
        V_u   = c.gaussian(4.999, 0.003209, 0.0)
        I_u   = c.gaussian(19.661e-3, 9.47e-6, 0.0)
        PHI_u = c.gaussian(1.04446, 7.521e-4, 0)
        V   = quantities.Quantity(si.VOLT, V_u)
        I   = quantities.Quantity(si.AMPERE, I_u)
        PHI = quantities.Quantity(si.RADIAN, PHI_u)
        
        c.set_correlation(V, I, numpy.matrix([[-0.36,0.0],[0.0,0.0]]))
        c.set_correlation(V, PHI, numpy.matrix([[0.86,0.0],[0.0,0.0]]))
        c.set_correlation(I, PHI, numpy.matrix([[-0.65,0.0],[0.0,0.0]]))
        
        z = V * numpy.exp( _J_ * PHI) / I
        
        # The values from the manual
        desired_value = 127.732169928 + 219.846511913j
        desired_unit  = si.OHM
        desired_covm  = numpy.matrix([[ 0.00493636, -0.01237897],
                                      [-0.01237897,  0.08766197]])
        desired_uunit = si.OHM**2
        # Maximum acceptable error
        desired_err   = numpy.matrix([[ 1e-8, 1e-8],
                                      [ 1e-8, 1e-8]])

        u_z = z.get_default_unit()
        res = c.uncertainty(z)
        u_r = res.get_default_unit()

        quantities.set_strict(False)
        assert(u_z.get_dimension() == desired_unit.get_dimension())
        assert(u_r.get_dimension() == desired_uunit.get_dimension())
        quantities.set_strict(True)
        
        v_z = z.get_value(u_z).get_value()
        v_r = res.get_value(u_r)
                                      
        assert(numpy.abs(desired_value - v_z) < 1e-5)
        assert(numpy.all(numpy.abs(v_r - desired_covm) 
                < desired_err))
        
# initialize tests
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite( TestSIUnits ) )
    suite.addTest( unittest.makeSuite( TestArithmetic ) )
    suite.addTest( unittest.makeSuite( TestOperators ) )
    suite.addTest( unittest.makeSuite( TestQuantity ) )
    suite.addTest( unittest.makeSuite( TestUncertaintyComponents ) )
    suite.addTest( unittest.makeSuite( TestGUMTree ) )
    suite.addTest( unittest.makeSuite( 
                   TestComplexUncertaintyComponents) )
    unittest.TextTestRunner( verbosity=2 ).run( suite )

## @}
