## \file units.py
#  \brief This file is evaluated whenever the units module is loaded.
#
#  It loads the classes necessary to operate the units module and
#  performs some global initialization.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#          Thomas Reidemeister</a>

## \namespace scuq::units
# \brief This namespace contains the classes and constants to model 
#        units.

## \defgroup units Units Module
#
# This module contains the classes necessary to define, handle, and
# work with physical units and dimensions.
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \addtogroup units 
# @{

# standard module
#import operator
import numbers

# local modules
import scuq.arithmetic as arithmetic
import scuq.operators as operators
import scuq.qexceptions as qexceptions

class PhysicalModel(object):
    """! @brief       This class models the abstract interface for physical models.
     
       This class provides an interface for defining physical models.
       @attention This class is only an abstract interface. You will have to
                  override it in order to get any effect.
       @see si.SIModel
    """
    def __init__( self ):
        """! @brief This is the default constructor.
              @param self
        """
        raise NotImplementedError

    def get_dimension( self, unit ):
        """! @brief Get the pysical dimension that corresponds to the
               given unit.
               @param self
               @param unit to check the dimension for.
               @return The corresponding physical dimension.
        """
        raise NotImplementedError
    

def set_default_model( physicalModel ):
    """! @brief       Set the default physical model to use.
      @param physicalModel The physical model to use.
      @see PhysicalModel.
    """
    assert( isinstance( physicalModel, PhysicalModel ) )
    _UNITS_MANAGER.set_model( physicalModel )
    
def get_default_model():
    """! @brief       Get the physical model currently in use.
       This function returns None, if no model is currently in use.
       @return The physical model that is currently in use.
       @see PhysicalModel.
    """
    return _UNITS_MANAGER.get_model()
    
    
class Dimension(object):    
    """! @brief       This class provides an interface to model physical dimensions.
     
       In order to distinguish between different dimensions, we add
       an unique symbol to each dimension. In order to aviod confusion,
       the symbols for physical dimensions must not interfer with
       the symbols used for base units and alternate units.
       @see BaseUnit
       @see AlternateUnit
       @attention This class should not be inherited. It describes
                  the any phyiscal dimension correctly.
      @note Instances of this class can be serialized using pickle.
    """
    
    ## A pseudo unit representing the physical unit.
    # All Operations that can be performed on units are also
    # applicable to Dimensions. Therefore each dimension is
    # represented internally by a pseudo Unit. 
    _pseudoUnit = None
    
    def __init__( self, value ):
        """! @brief This is the default constructor.
             
               This function creates a physical dimension.
              @param  self
              @param  value An unique symbol that is used to model the dimension.
              @exception UnitExistsException If the same symbol already
                         exists in the dictionary of units.
        """
        # Because physical dimensions could also be created using operations,
        # the pseudo unit can also be assigned.
        if( isinstance( value, Unit ) ):
            self._pseudoUnit = value
        else:
            assert( isinstance( value, str ) )
            assert( len( value ) > 0 )
            self._pseudoUnit = BaseUnit( value )

    def __str__( self ):
        """! @brief Return a string describing the physical dimension.
             
               The physical dimensions are described in the same way as units.
               @param  self
               @return A string describing this dimension.
               @see Unit.__str__
        """
        return str( self._pseudoUnit )
    
    def __mul__( self, other ):
        """! @brief Return a dimension that describes the product of the current and 
               another dimension.
              @param self
              @param other Another instance of a Dimension.
              @return A new dimension representing the product.
        """
        assert( isinstance( other, Dimension ) )
        return Dimension( self._pseudoUnit * other._pseudoUnit )
    
    def __truediv__( self, other ):
        """! @brief Return a dimension that describes the fraction of the current and 
               another dimension.
              @param self
              @param other Another instance of a Dimension.
              @return A new dimension representing the fraction.
        """
        assert( isinstance( other, Dimension ) )
        return Dimension( self._pseudoUnit // other._pseudoUnit )
    
    def __pow__( self, value ):
        """! @brief Return a dimension that represents the current dimension 
               raised to an integer power.
              @param self
              @param value An integer to be used as power.
              @return A new dimension representing the power.
        """
        assert( isinstance( value, int ))
        value = int( value )
        
        return Dimension( self._pseudoUnit ** value )
    
    def root( self, value ):
        """! @brief Return a dimension that represents the root of the 
               current dimension.
              @param self
              @param value An integer to be used as root.
              @return A new dimension representing the root.
        """
        assert( isinstance( value, int ) or isinstance( value, int ) )
        value = int( value )
        
        return Dimension( self._pseudoUnit.root( value ) )

    def __eq__( self, other ):
        """! @brief This function checks if two dimensions are equal.
              @param self
              @param other Another dimension.
              @return True, if the dimensions are equal.    
        """
        assert( isinstance( other, Dimension ) )
        return self._pseudoUnit == other._pseudoUnit
    
    def get_symbol( self ):
        """! @brief Same as __eq__
              @param self
               @see Dimension.__eq__
        """
        return self.__str__()
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self._pseudoUnit )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self._pseudoUnit = state

class UnitsManager(object):
    """! @brief       This manages the alternate and base units as well as the physical 
       dimensions.
       @see AlternateUnit
       @see BaseUnit
       @see Dimension
    """
    
    ## Physical Model used for units.
    _physicalModel     = None
    
    ## Dictionary of BaseUnits and AlternateUnits created.
    # 
    # It maps the symbol from the respective base or alternate unit 
    # to an instance of the BaseUnit created.
    _unitsDictionary = {None:None}
    

    def __init__( self ):
        """! @brief This is the default constructor.
              @param self
        """
        self._unitsDictionary.clear()
        
    def addUnit( self, unit ):
        """! @brief This is a helper function to add the units to the dictionary.
              @param self
              @param unit An instance of an BaseUnit or AlternateUnit to add.
              @exception UnitExistsException If the same symbol already
                         exists in the dictionary of units.
        """
        assert( isinstance( unit, BaseUnit ) or 
                isinstance( unit, AlternateUnit ) )
        
        if ( self.existsUnit( unit ) ):
            raise qexceptions.UnitExistsException( unit, 
                  "The following base unit has already been defined" )
        
        self._unitsDictionary[unit.get_symbol()] = unit
    

    def existsUnit( self, unit ):
        """! @brief Check if a BaseUnit, AlternateUnit or Dimension is already contained.
             
              This function checks only for the existence of a Symbol.
              So that no Symbols of units and dimensions are defined twice.
              @param self
              @param unit An instance of a BaseUnit, AlternateUnit or Dimension 
                     to be checked for.
              @return True, if the Symbol of the unit/dimension already existed.
                      False, otherwise.
        """
        assert( ( isinstance( unit, BaseUnit ) 
                or isinstance( unit, AlternateUnit ) ) \
                or isinstance( unit, Dimension ) )
        #print unit.get_symbol(), repr(unit.get_symbol())
        #print self._unitsDictionary
        #print self._unitsDictionary.has_key( unit.get_symbol() )
        return unit.get_symbol() in self._unitsDictionary
    
    def set_model( self, physicalModel ):
        """! @brief Set the global physical model to be used.
              @param self
              @param physicalModel The model to be used.
        """
        assert( isinstance( physicalModel, PhysicalModel ) )
        self._physicalModel = physicalModel
        
    def get_model( self ):
        """! @brief Return the global physical model used.
              @param self
              @return The current physical model used.
              @attention This function returns None, if no model is currently in use.
        """
        return self._physicalModel
        

class Unit(object):
    """! @brief       An abstract class to model physical units.
     
      This class provides an interface to model physical units.
      @attention You have to use one of its silblings to get any effect.
    """


    def __eq__( self, other ):
        """! @brief Check for if two units are equal.
             
              @param self
              @param other Another instance of a Unit or its subclasses.
              @return True, if this unit and the argument are equal.
        """
        raise NotImplementedError
    
    def __ne__( self, other ):
        """! @brief Check for if two units are unequal.
             
              @param self
              @param other Another instance of a Unit or its subclasses.
              @return True, if this unit and the argument are unequal.
        """
        return not( self == other )
    

    def get_system_unit( self ):
        """! @brief Get the corresponding system unit.
              The physical model is used to determine the mapping to the system
              unit.
              @param self
              @return The system unit.
              @see PhysicalModel
              @attention The subclasses override this method, 
                         calling Unit.get_system_unit has no effect.
        """
        raise NotImplementedError
    

    def get_dimension( self ):
        """! @brief Get the corresponding physical dimension.
              @param self
              @return The corresponding physical dimension.
              @attention This method is intended to be final for the predefined
                         silblings of Unit. You only have to override it if you are
                         directly inheriting from Unit.
        """
        sysUnit = self.get_system_unit()
        if( isinstance( sysUnit, BaseUnit ) ):
            return _UNITS_MANAGER.get_model().get_dimension( sysUnit )
        if( isinstance( sysUnit, AlternateUnit ) or isinstance( sysUnit, 
                                                 TransformedUnit ) ):
            return sysUnit.get_parent().get_dimension()
        if( isinstance( sysUnit, CompoundUnit ) ):
            return sysUnit.get_first().get_dimension()
        # only product Unit left
        assert( isinstance( sysUnit, ProductUnit ) )
        
        dimension = NONE
        for i in range( 0, sysUnit.get_unitCount() ):
            unit = sysUnit.get_unit( i )
            dim  = ( unit.get_dimension() ** 
                     sysUnit.get_unitPow(i)).root(sysUnit.get_unitRoot(i))
            dimension = dimension * dim
        
        return dimension
            
    

    def is_compatible( self, other ):
        """! @brief Check if two units can be converted to each other.
             
              Two units are compatible if their corresponding system units
              match, or if both units describe the same physical dimension.
              @param self
              @param other Another unit to compare to.
              @return True, if the units are compatible.
        """
        assert( isinstance( other, Unit ) )
        return ( ( self.get_system_unit() == other.get_system_unit() ) or
            self.get_dimension() == other.get_dimension() )
    
    def __add__( self, other ):
        """! @brief Support of Adding an offset to the current unit 
              (i.e. @f$Celsus = Kelvin + 253.15@f$).
              This function returns a TransformedUnit that represents adding the
              offset to the current unit.
              @param self
              @param other A numerical value to add to the unit.
              @return A transformed unit that represents adding the
              offset to the current unit.
              @see TransformedUnit
        """
        assert( isinstance(other, numbers.Number) )
        return self.__transformUnit( operators.AddOperator( other ) )
    
    def __sub__( self, other ):
        """! @brief Support for Substracting an offset.
               This function works in a similar way as Unit.__add__.
              @param self
              @param other A numerical value to substract from the unit.
              @return A transformed unit that represents substracting the
              offset from the current unit.
              @see TransformedUnit
              @see Unit.__add__
        """
        return self + ( -other )
    
    def __mul__( self, other ):
        """! @brief Suport for multiplying a numeric value or unit.
              This function returns a new Unit that represents multiplying the
              factor or unit to the current unit.
              @param self
              @param other A number or unit.
              @return A new unit representing the operation.
              @see TransformedUnit
              @see ProductUnit
              @see ONE
        """
        assert( isinstance( other, Unit ) or isinstance(other, numbers.Number) )
        if( isinstance( other, Unit ) ):
            if( other == ONE ):
                return self
            if( self == ONE ):
                return other
            return ProductUnit( self, other )
        else:
            return self.__transformUnit( operators.MultiplyOperator( other ) )
    
    def __pow__( self, other ):
        """! @brief Support integer powers.
              This function returns a new Unit that represents the power of the
              current unit.
              @attention In order to preserve dimensional consistency we do only
                         allow integers or rational numbers as powers of units.
              @param self
              @param other An integer.
              @return A new unit representing the operation.
              @see ProductUnit
        """
        if( self == ONE or other == ONE ):
            return self
        
        if( isinstance( other, int )):
            if( other == 1 ):
                return self
            if( other > 0 ):
                return self.__mul__( self.__pow__( other-1 ) )
            elif( other == 0 ):
                return ONE
            else:
                return ONE.__truediv__( self.__pow__( -other ) )
        
        if( isinstance( other, arithmetic.RationalNumber ) ):
            power = other.get_dividend()
            root  = other.get_divisor()
            
            powered = self ** power
            rooted  = powered.root(root)
            return rooted
        
        # unknown type, raise error
        assert(0)
        
    def root( self, other ):
        """! @brief Support of integer roots.
              This function returns a new Unit that represents the root of the
              current unit.
              @param self
              @param other An integer.
              @exception ArithmeticError If the root is zero this function fails.
              @return A new unit representing the operation.
              @see ProductUnit
        """
        assert( isinstance( other, int ) or isinstance( other, int ) )
        value = int( other )

        if( value > 0 ):
            return self.__rootInstance( self, value )
        elif( value == 0 ):
            raise ArithmeticError( "The root cannot be zero." )
        else:
            return ONE.__truediv__( self.root( -value ) )
        
    def sqrt( self ):
        """! @brief Support of square root.
              This function returns a new Unit that represents the 
              square root of the current unit.
              @param self
              @return A new unit representing the operation.
              @see ProductUnit
              @see root
        """
        return self.root( 2 )
        
    def __truediv__( self, other ):
        """! @brief Support for dividing units and numeric values.
              This function returns a new Unit that represents the operation.
              @param self
              @param other A number or unit.
              @exception ZeroDivisionError This error is raised if the divisor 
                         is zero.
              @return A new unit representing the operation.
              @see ProductUnit
              @see TransformedUnit
        """
        assert( isinstance( other, Unit ) or isinstance(other, numbers.Number) )
        if( isinstance( other, Unit ) ):
            if( other == ONE ):
                return self
            return self.__mul__( ~other )
        else:
            return self.__transformUnit( 
                    operators.MultiplyOperator( 1.0/other ) )
    
    def __invert__( self ):
        """! @brief Support inversion of units.
              This function returns a new Unit that represents the operation.
              Suppose your unit is @f$[U]@f$, then the inverted unit is 
              @f$[\frac{1}{U}]@f$.
              @return A new unit representing the operation.
              @see ProductUnit
        """
        unit =  ONE.__truediv__(self)
        return unit
    
    def compound( self, other ):
        """! @brief Support compound units.
              This method returns a compound unit of the current unit and the 
              argument.
              Both units have to describe the same physical dimension.
              @param self
              @param other Another unit describing the same dimension.
              @return A new compound unit.
              @exception TypeError If the units describe different dimensions.
        """
        assert( isinstance( other, Unit ) )
        return CompoundUnit( self, other )
    
    def __str__( self ):
        """! @brief Support of printing units.
              The silblings of unit override this method. It should print the 
              symbols of the units that form the unit. For example a ProductUnit
              might print <tt>kg*m*s^(-2)</tt>.
              @param self
              @return A string describing this unit.
              @attention The subclasses override this method, calling Unit.__str__
                         has no effect.
        """
        raise NotImplementedError
    
    def to_system_unit( self ):
        """! @brief Abstract Function to convert to corresponding system unit.
              @param self
              @return The corresponding system unit.
              @attention The subclasses override this method, calling 
                         Unit.to_system_unit has no effect.
        """
        raise NotImplementedError
    
    def get_operator_to( self, unit ):
        """! @brief Convert units.
              This method returns an operator that converts values that have been
              formed with the current unit to another other unit.
              @param self
              @param unit The unit to convert to.
              @return A converter to the argument.
              @exception qexceptions.ConversionException If a conversion is not 
                         possible an exception is raised (i.e. if the units describe
                         different physical dimensions).
              @see operators
        """
        assert( isinstance( unit, Unit ) )
        # same unit
        if( unit == self ):
            return operators.IDENTITY
        selfUnit = self.get_system_unit()
        otherUnit = unit.get_system_unit()
        # Same Base Unit -> convert own to SystemUnit and invert other
        # to SystemUnit
        if( selfUnit == otherUnit ):
            op=unit.to_system_unit() * ( ~self.to_system_unit() )
            op.fromUnit=selfUnit
            op.toUnit=unit
            return op
        
        # last chance: same physical dimension?
        selfDim = self.get_dimension()
        otherDim = unit.get_dimension()
        if( not otherDim == selfDim ):
            raise qexceptions.ConversionException( self, 
                " has not the same physical dimension as "+str( unit ) )
        
        selfTransform  = self.to_system_unit() * selfUnit._getTransformOf()
        otherTransform = unit.to_system_unit() * otherUnit._getTransformOf()
        
        op=( ~otherTransform ) * selfTransform
        op.fromUnit=selfUnit
        op.toUnit=unit
        return op
        
    def _getTransformOf( self ):
        """! @brief Helper function to get the transformation to the system unit.
              This method returns an operator that converts values that have been
              formed with the current unit to its system unit.
              @param self
              @return A converter to the system unit.
              @exception qexceptions.ConversionException If a conversion is not 
                         possible an exception is raised (e.g. if the unit has
                         a fractional exponent, or if the transformation is
                         not linear).
              @see operators
        """
        
        # Abort condition
        if( isinstance( self, BaseUnit ) ):
            return operators.IDENTITY
        
        # Renamed unit?
        if( isinstance( self, AlternateUnit ) ):
            return self.get_parent()._getTransformOf()
        # Transformed Unit?
        if( isinstance( self, TransformedUnit ) ):
            return self.get_operator_to(self.get_system_unit())

        # Product unit
        operator = operators.IDENTITY
        for i in range( 0, self.get_unitCount() ):
            unit = self.get_unit( i )
            op   = unit._getTransformOf()
            if( not op.is_linear() ):
                raise qexceptions.ConversionException( unit, 
                                 " has been created using non-linear operation"
                                 + str( op ) )
            if( self.get_unitRoot( i ) != 1 ):
                raise qexceptions.ConversionException( unit, \
                                 " has has fractional exponent" )
            pow_ = self.get_unitPow( i )
            if( pow_ < 0 ):
                pow_ = -pow_
                op  = ~op
            
            for _ in range( 0, pow_ ):
                operator = operator * op
        
        return operator

    
    def __rootInstance( self, unit, root ):
        """! @brief Helper function to get the n-th root instance of the unit.
              @param self
              @param unit The unit to be rooted.
              @param root An integer to be used as root.
              @return A new unit representing the operation.
              @see ProductUnit
        """
        assert( isinstance( unit, Unit ) )
        assert( isinstance(root, numbers.Number) )
        newElts = []
        if( isinstance( unit, ProductUnit ) ):
            elts     = unit.__elements__
            for elt in elts:
                elt_pow  = elt.get_pow()
                elt_root = elt.get_root()*root
                new_elt  = __ProductElement__( elt.get_unit(), 
                                                elt_pow, 
                                                elt_root )
                new_elt.normalize()

                newElts += [ new_elt ]
        else:
            newElts += [__ProductElement__( unit, 1, root )]
        
        result = ProductUnit( ONE, ONE )
        result.__elements__ = newElts
        result.normalize()
        return result
    
    def __transformUnit( self, operation ):
        """! @brief Helper function that applies a transformation to the current unit.
              @param self
              @param operation The operation to be performed.
              @return A new unit representing the current unit after applying the
                      operation.
        """
        assert( isinstance( operation, operators.UnitOperator ) )
        
        if( isinstance( self, TransformedUnit ) ):
            parent     = self.get_parent()
            toParentOp = self.to_parent_unit()
            newOp      = ~toParentOp * operation
            return TransformedUnit( parent, newOp )
        else:
            return TransformedUnit( self, operation )
        
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
    
    def __coerce__(self, other):
        """! @brief Implementation of coercion rules.
        This implementation ensures that transformed units can be created
        from units.
"""
        if(isinstance(other, Unit)):
            return (self, other)
        elif(isinstance(other, int) or
             isinstance(other, int) or
             isinstance(other, float) or
             isinstance(other, complex) or
             isinstance(other, arithmetic.RationalNumber)):
            return (self,other)
        else:
            raise NotImplementedError()
        

class BaseUnit( Unit ):
    """! @brief       This class provides the interface to define and use base units.
     
      A base unit is a unit that describes a single physical dimension.
      It can not be formed from other base units from other physical 
      dimensions. Therefore, a base unit has to be unique. In order to 
      ensure this, we do assign a unique symbol to each base unit.
      @note Instances of this class can be serialized using pickle.
    """
    
    ## Unique symbol describing the BaseUnit.
    __symbol__ = None
    
    
    def __init__( self, symbol ):
        """! @brief Default constructor.
             
              Assigns the desired symbol to the respective BaseUnit and
              checks if an other instance of a unit already
              exists that has the same symbol.
              @param self
              @param symbol A symbol identifying the BaseUnit.
              @exception UnitExistsException If a unit having the same
                         symbol already exists.
              @see AlternateUnit
        """
        assert( isinstance( symbol, str ) )
        assert( len( symbol ) > 0 )
        self.__symbol__ = symbol
        _UNITS_MANAGER.addUnit( self )    
    
    def get_symbol( self ):
        """! @brief Return the symbol of this unit.
             
              @param self
              @return The symbol of the BaseUnit.
        """
        return self.__symbol__

    def __str__( self ):
        """! @brief Return a string describing this unit.
              @param self
              @return The symbol of this unit.
              @see BaseUnit.get_symbol
        """
        return self.get_symbol()

    def __eq__( self, other ):
        """! @brief Check two if two base units are equal.
             
              Two base units are equal if they have the same unit symbol.
              @param self
              @param other Another unit.
        """
        # Not a BaseUnit
        if( isinstance( other, ProductUnit ) ):
            other = ProductUnit.strip_unit( other )
        if( not isinstance( other, BaseUnit ) ):
            return False
        # check if the units have the same symbols
        return ( self.get_symbol() == other.get_symbol() )
    
    def get_system_unit( self ):
        """! @brief Get the corresponding system unit.
              Since it is a base unit, it returns itself.
              @param self
              @return The corresponding system unit.
              @see Unit.get_system_unit
        """
        return self
    
    def to_system_unit( self ):
        """! @brief Get the operator to the system unit.
              Since it is a system unit, it returns operators.IDENTITY
              @return operators.IDENTITY
              @see Unit.to_system_unit
        """
        return operators.IDENTITY
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self.__symbol__ )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
              @exception UnknownUnitException If the unit to be 
              unpickled is not contained in the global repository
              _UNITS_MANAGER.
              @see UnitsManager
              @see _UNITS_MANAGER
        """
        self.__symbol__ = state
        #print state
        if( not _UNITS_MANAGER.existsUnit( self ) ):
            raise qexceptions.UnknownUnitException( self, " is unknown, and can"
                                           +" therefore not  be unpickled" )
    

class DerivedUnit( Unit ):
    """! @brief       This class provides an abstract interface for all units that 
       have been transformed from other units.
     
      @attention This class is intended to be abstract. Instancing it
                 makes no effect.
      @see AlternateUnit
      @see CompoundUnit
      @see ProductUnit
      @see TransformedUnit
    """
    def __init__( self ):
        """! @brief abstract default constructor.
              @param self
        """
        raise NotImplementedError
    

class AlternateUnit( DerivedUnit ):
    """! @brief       This class provides an interface for units that describe
       the same dimension as another unit, but need to be distinguished
       from it by another symbol (e.g. to abbreviate them, or to
       distinguish their purpose).
     
      For examle @f$ [N] := \left[\frac{kg \times m}{s^2}\right] @f$.
      @note Instances of this class can be serialized using pickle.
    """
    
    ## Symbol for the alternate unit.
    __symbol__ = None
    
    ## System unit that parents this unit.
    __parentUnit__ = None

    def __init__( self, symbol, parentUnit ):
        """! @brief Default constructor.
             
              @param self
              @param symbol Symbol of the alternate Unit.
              @param parentUnit Parent unit.
              @exception UnitExistsException If a unit having the same
                         symbol already exists.
              @exception TypeError If the parentUnit is not a SystemUnit.
        """
        assert( isinstance( parentUnit, Unit ) )
        assert( isinstance( symbol, str ) )
        assert( len( symbol ) > 0 )
        
        if ( not parentUnit.get_system_unit().get_dimension().__eq__( parentUnit.get_dimension() ) ):
            raise TypeError( "ParentUnit has to be a System unit" )
        
        self.__symbol__ = symbol
        self.__parentUnit__ = parentUnit
        
        _UNITS_MANAGER.addUnit( self )
    

    def get_parent( self ):
        """! @brief Returns the parent unit of the this unit.
              @param self
              @return Parent unit.
        """
        return self.__parentUnit__
    

    def get_symbol( self ):
        """! @brief Returns the symbol of this unit.
              @param self
              @return Symbol of current unit.    
        """
        return self.__symbol__
    
    def get_system_unit( self ):
        """! @brief Returns the corresponding system unit.
              Since the parent unit is a system unit, this unit is
              supposed to be a system unit too. Therefore this function
              returns this instance.
              @param self
              @return self
        """
        return self
    
    def to_system_unit( self ):
        """! @brief Get the operator to convert to the system unit.
              Since the parent unit is a system unit, this unit is
              supposed to be a system unit too. Therefore this function
              returns operators.IDENTITY.
              @param self
              @return operators.IDENTITY
              @see operators.IDENTITY
        """
        return operators.IDENTITY
    
    
    def __eq__( self, other ):
        """! @brief Checks if two alternate units are equal.
              @param self
              @param other Another alternate unit to compare to.
              @return True, if the units are equal.
        """
        if( isinstance( other, ProductUnit ) ):
            other = ProductUnit.strip_unit( other )
        if( not isinstance( other, AlternateUnit ) ):
            return False
        
        return ( self.get_symbol() == other.get_symbol() )
    
    def __str__( self ):
        """! @brief Print the current unit.
              This function is an alias for AlternateUnit.get_symbol
              @param self
              @return A string describing this unit.
              @see AlternateUnit.get_symbol
        """
        return self.get_symbol()
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self.__symbol__, self.__parentUnit__ )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
              @exception UnknownUnitException If the unit to be 
              unpickled is not contained in the global repository
              _UNITS_MANAGER.
              @see UnitsManager
              @see _UNITS_MANAGER
        """
        self.__symbol__, self.__parentUnit__ = state
        if( not _UNITS_MANAGER.existsUnit( self ) ):
            raise qexceptions.UnknownUnitException( self, " is unknown, and can therefore"
                                           +" not be unpickled" )
    
# Example for AlternateUnit
## This example shows how to create and use instances of
# units.AlternateUnit. They are created from other units
# using transformations. A symbol is assigned to the new
# unit, to distinguish it from other units. This symbol
# has to be unique and must not interfer with symbols of 
# other units already created.
# We will show this by a simple example using SI units.
# \see units.AlternateUnit
# \example AlternateUnits.py


class CompoundUnit( DerivedUnit ):
    """! @brief       This class provides an interface for describing compound units.
      The units forming a compound unit have to describe the same 
      physical dimension.
      For example time @f$ \left[hour:min:second\right] @f$.
      @note Instances of this class can be serialized using pickle.
    """
    
    ## The first unit.
    __first__ = None
    ## The next unit.
    __next__  = None
    
    def __init__( self, firstUnit, nextUnit ):
        """! @brief Default constructor.
              Both arguments have to describe the same physical dimension and
              they have to have the same system unit.
              @param self
              @param firstUnit The first unit.
              @param nextUnit The unit to attach to the first unit.
              @exception TypeError If the units describe different dimensions.
        """
        assert( isinstance( firstUnit, Unit ) )
        assert( isinstance( nextUnit, Unit ) )
        
        if( not firstUnit.get_system_unit().__eq__( 
            nextUnit.get_system_unit() ) ):
            raise TypeError( "Both units have to describe  the same"
                            +" physical dimension" )
        
        # Optimize CompoundUnits
        if( isinstance( firstUnit, CompoundUnit ) ):
            self.__first__ = firstUnit.get_first()
            self.__next__  = CompoundUnit( firstUnit.get_next(), nextUnit )
        else:
            self.__first__ = firstUnit
            self.__next__  = nextUnit
    
    def get_first( self ):
        """! @brief Get the first unit.
              @param self
              @return The first unit of this compound unit.
        """
        return self.__first__
    
    def get_next( self ):
        """! @brief Get the next unit.
              @param self
              @return The first unit of this compound unit.
        """
        return self.__next__
    
    def get_system_unit( self ):
        """! @brief Returns the corresponding system unit.
              @note All units forming this unit have the same system unit.
              @return The corresponding system unit.
        """
        return self.__first__.get_system_unit()
    
    def to_system_unit( self ):
        """! @brief Get the operator to convert to the system unit.
              We assume that the operator of the first element of this
              compound unit performs the conversion correctly.
              @param self
              @return The operator to the system unit of the first element
              @see CompoundUnit.__first__
        """
        return self.__first__.to_system_unit()
    
    def __eq__( self, other ):
        """! @brief This function checks if two compound units are equal.
              Two compound units are equal, if they have equal
              first and next units. 
              @attention The order of the first and next units matters
                         (i.e. @f$hh:mm \neq mm:hh@f$)!
              @param self
              @param other Another compound unit to compare to.
              @return True, if the units are equal.
        """
        # if not an instance, it is not comparable
        if( not isinstance( other, CompoundUnit ) ):
            return False
        # compare recursively
        return ( other.get_first().__eq__( self.__first__ ) 
            and other.get_next().__eq__( self.__next__ ) )
    
    
    def __str__( self ):
        """! @brief Print the current unit.
              This function returns a string of the form <tt>first:next</tt>.
              @param self
              @return A string describing this unit.
        """
        return str( self.get_first() )+":"+str( self.get_next() )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self.__first__, self.__next__ )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self.__first__, self.__next__ = state

class __ProductElement__(object):
    """! @brief       A helper class for ProductUnit classes.
      This class helps to maintain the factors of a product unit.
      @note Instances of this class can be serialized using pickle.
    """
    ## The unit of the current factor.
    __unit__ = None
    ## The power of the current factor.
    __pow__  = None
    ## The root of the current factor.
    __root__ = None
    
    def __init__( self, unit, power, root ):
        """! @brief Default constructor.
              @param self
              @param unit The unit of the factor to create.
              @param power The power assigned to this factor.
              @param root The root assigned to this factor.
        """
        assert( isinstance( unit, Unit ) )
        assert( isinstance( power, int ) )
        assert( isinstance( root, int ) )
        
        self.__unit__ = unit
        self.__pow__  = int( power )
        self.__root__ = int( root )
    
    def get_unit( self ):
        """! @brief Get the unit of this factor.
              @param self
              @return The unit of this factor.
        """
        return self.__unit__
    
    def get_pow( self ):
        """! @brief Get the power of this factor.
              @param self
              @return The power of this factor.
        """
        return int(self.__pow__)

    def get_root( self ):
        """! @brief Get the root of this factor.
              @param self
              @return The root of this factor.    
        """
        return int(self.__root__)
    
    def __eq__( self, other ):
        """! @brief This method checks two factors for equality.
              Two factors are equal if they have the same units,
              powers, and roots.
              @param self
              @param other Another instance of a factor.
              @return True, if the factors are equal.
        """
        if( not isinstance( other, __ProductElement__ ) ):
            return False
        return self.__unit__ == other.__unit__ and \
            self.__pow__ == other.__pow__ and \
            self.__root__ == other.__root__

    def set_pow( self, value ):
        """! @brief This method changes the power.
              @param self
              @param value An interget to be used as new power.
        """
        assert( isinstance( value, int ) )
        
        self.__pow__ = int( value )

    def set_root( self, value ):
        """! @brief This method changes the root.
              @param self
              @param value An interger to be used as new root.        
        """
        assert( isinstance( value, int ) or isinstance( value, int ) )

        self.__root__ = int( value )
        
    def normalize( self ):
        """! @brief Transform the current factor into its canonical form.
              @param self
        """
        divisor = arithmetic.gcd( abs( self.__pow__ ), self.__root__ )
        self.__pow__ //= divisor
        self.__root__ //= divisor
        
    def __str__( self ):
        """! @brief Print this factor.
              This function returns a string of the form <tt>unit^(pow/root)</tt>.
              @param self
              @return A string describing this factor.
        """
        if( self.__pow__ == 1 and self.__root__ == 1 ):
            return str( self.__unit__ )
        elif( self.__root__ == 1 ):
            return str( self.__unit__ )+"^("+str( self.__pow__ )+")"
        else:
            return str( self.__unit__ )+"^("+str( self.__pow__ )+"/" \
                   + str( self.__root__ )+")"
        
    def clone( self ):
        """! @brief Return a new instance of this factor.
              @param self
              @return A new instance of this factor.
        """
        return __ProductElement__( self.__unit__, self.__pow__, self.__root__ )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self.__unit__, self.__pow__, self.__root__ )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self.__unit__, self.__pow__, self.__root__ = state


class ProductUnit( DerivedUnit ):
    """! @brief       The unit is a combined unit of the product of the powers
       of units. 
     
       The unit is stored in its canonical form. That
       is the simplest form. 
       For example @f$ \left[m\right] := \left[\frac{m^2}{m}\right] @f$.
      @note Instances of this class can be serialized using pickle.
    """
    
    ## The factors forming the product unit.
    # \see __ProductElement__
    __elements__ = []
    
    def __init__( self, left=None, right=None ):
        """! @brief Default constructor.
              @param self
              @param left  A unit to left-multiply.
              @param right A unit to right-multiply.
        """
        self.__elements__ = []
        if( right == None or left == None ):
            return
        
        assert( isinstance( right, Unit ) )
        assert( isinstance( left, Unit ) )
        
        if( isinstance( left, ProductUnit ) ):
            self.__elements__ += left.__cloneElements()
        else:
            self.__elements__ += [__ProductElement__( left, 1, 1 )]
            
        if( isinstance( right, ProductUnit ) ):
            self.__elements__ += right.__cloneElements()
        else:
            self.__elements__ += [__ProductElement__( right, 1, 1 )]
            
        self.normalize()

    def get_system_unit( self ):
        """! @brief Get the corresponding system unit. 
             
              If no system unit is found, the unit is formed from the system units
              of the factors of the current unit.
              @return The corresponding system unit.
        """
        if( self.__isSystemUnit() ):
            return self
        
        result = ONE
        for item in self.__elements__:
            unit = item.get_unit()
            unit = unit ** item.get_pow()
            unit = unit.root( item.get_root() )
            result = result * unit
        
        return result
    
    def to_system_unit( self ):
        """! @brief Get the operator to convert to the system unit.
              This method concatenates the individual operators and
              returns the joint operator to the system unit, if this
              unit is not a system unit.
              @return The operator to the system unit.
              @exception qexceptions.ConversionException If one of the
                         system units is formed using a non linear operator, or
                         if a factor has a rational exponent.
        """
        if( self.__isSystemUnit() ):
            return operators.IDENTITY
        
        result = operators.IDENTITY
        for item in self.__elements__:
            operator = item.get_unit().to_system_unit()
            if( not operator.is_linear() ):
                raise qexceptions.ConversionException( self, \
                    "Can not concat nonlinear Operator" )
            if( item.get_root() != 1 ):
                raise qexceptions.ConversionException( self, \
                    "Unit has rational exponent" )
            pow_ = item.get_pow()
            if( pow_ < 0 ):
                pow_ = -pow_
                operator = ~operator
            for _ in range( 0, pow_ ):
                result = result * operator
                
        return result

    def get_unit( self, index ):
        """! @brief Returns the unit at the given index.
              @param self
              @param index Index of the desired unit.
              @return The unit at index.
        """
        assert( isinstance( index, int ) or isinstance( index, int ) )
        assert( index >= 0 )
        assert( index < len( self.__elements__ ) )
        return self.__elements__[index].get_unit()

    
    def get_unitCount( self ):
        """! @brief Get the total count of factors of this product unit.
              @param self
              @return The number of factors.
        """
        return len( self.__elements__ )
    
    def get_unitPow( self, index ):
        """! @brief Get the power exponent of a factor at the given index.
             
              @attention Since roots are rational, you have to call
                         <tt>get_unitPow</tt> and <tt>get_unitRoot</tt> in order to 
                         obtain the complete exponent of this unit. For example for
                         @f$ \sqrt{m^3} @f$ the results would be 3 for 
                         <tt>get_unitPow</tt> and 2 for <tt>get_unitRoot</tt>.
              @param self
              @param index Index of the desired unit.
              @return The (integer) power of the current unit
        """
        assert( isinstance( index, int ) or isinstance( index, int ) )
        assert( index >= 0 )
        assert( index < len( self.__elements__ ) )
        return self.__elements__[index].get_pow()
    
    
    def get_unitRoot( self, index ):
        """! @brief Get the root exponent of a factor at the given index.
             
              @attention Since roots are rational, you have to call
                         <tt>get_unitPow</tt> and <tt>get_unitRoot</tt> in order to 
                         obtain the complete exponent of this unit. For example for
                         @f$ \sqrt{m^3} @f$ the results would be 3 for 
                         <tt>get_unitPow</tt> and 2 for <tt>get_unitRoot</tt>.
             
              @param self
              @param index Index of the desired unit.
              @return The (integer) root of the current unit
        """
        assert( isinstance( index, int ) or isinstance( index, int ) )
        assert( index >= 0 )
        assert( index < len( self.__elements__ ) )
        return self.__elements__[index].get_root()
    
    def __eq__( self, other ):
        """! @brief Checks if two product units are equal.
              @param self
              @param other Unit to compare to
              @return True If the units are equal, False if the units 
                           are unequal.
        """
        # convert to product unit, this is necessary
        # to compare product units having one element.
        try:
            other = ProductUnit.value_of( other )
        except Exception:
            return False   # not a unit
        
        if( other == None ):
            return False

        if( self.get_unitCount() != other.get_unitCount() ):
            return False
        
        for ownElt in self.__elements__ :
            found = False
            # check wether current element is others list
            for otherElt in other.__elements__:
                if( ownElt == otherElt ):
                    found = True
                    break
            # not contained -> break
            if( not found ):
                return False
        # no break occured -> match
        return True
    
    def __truediv__( self, other ):
        """! @brief Divide two units.
              @param self
              @param other A divisor.
              @see Unit.__truediv__
        """
        if( not isinstance(other, Unit) ):
            return Unit.__truediv__(self, other)
					
        elements = self.__cloneElements()
        if( isinstance( other, ProductUnit ) ):
            # Invert the Elements
            for item in other.__cloneElements():
                item          = item.clone()
                item.__pow__ = - item.__pow__
                elements += [item]
        else:
            elements += [__ProductElement__( other, -1, 1 )]
        
        unit = ProductUnit()
        unit.__elements__ = elements
        unit.normalize()
       
        return unit
            
    def normalize( self ):
        """! @brief This function merge duplicate factors and converts this unit 
               into its canonical form.
              @param self
        """
        if( len( self.__elements__ ) == 0 ):
            return
        
        newElts = []
        # merge duplicates, concat elements
        for i in range( 0, len( self.__elements__ ) ):
            elt = self.__elements__[i]

            # already processed
            if( elt == None ):
               continue
           
            # neutral element
            if( elt.get_pow() == 0 ):
                continue
            
            # mark as processed
            self.__elements__[i] = None
            for j in range( i, len( self.__elements__ ) ):
                tmp = self.__elements__[j]
                # check wether already processed
                if( tmp == None ):
                    continue
                
                # Same unit, update root, power + cancel
                if( elt.get_unit() == tmp.get_unit() ):
                    rightPow = tmp.get_pow()*elt.get_root()
                    leftPow  = elt.get_pow()*tmp.get_root()
                    divisor  = tmp.get_root()*elt.get_root()
                    newPow   = rightPow + leftPow
                    
                    elt.set_pow( newPow )
                    elt.set_root( divisor )
                    elt.normalize()
                    # mark as processed
                    self.__elements__[j] = None
            
            newElts = newElts + [elt]
            
        # pass 2, remove all 0 powers
        self.__elements__ = []
        for elt in newElts:
            if( elt.get_pow() != 0 ):
                self.__elements__ += [elt]

        
    def __str__( self ):
        """! @brief Print the current unit.
              This function returns a string of the form <tt>factor1*factor2</tt>.
              @param self
              @return A string describing this unit.
              @see __ProductElement.__str__
        """
        if( self.get_unitCount() == 0 ):
            return "1"
        
        string = ""
        for i in range( 0, len( self.__elements__ ) ):
            if( i == len( self.__elements__ )-1 ):
                string += str( self.__elements__[i] )
            else:
                string += str( self.__elements__[i] )+"*"
        
        return string
    
    def __isSystemUnit( self ):
        """! @brief Check if the current unit is a system unit.
              This product unit is a system unit, if all of its
              factors are system units.
              @param self
              @return True if it is a system unit.
        """
        for item in self.__elements__:
            unit = item.get_unit()
            if( unit.get_system_unit() != unit ):
                return False
        return True
    
    def __cloneElements( self ):
        """! @brief Return a copy of the sequence of factors.
              @param self
              @return A copy of __elements__.
              @see self.__elements__
        """
        retElems = []
        for elem in self.__elements__:
            if( elem == None ):
                continue
            retElems += [elem.clone()]
        return retElems
    
    def value_of( unit ):
        """! @brief Factory method for generating 
               product units. Used to compare other units.
               @param unit A unit.
               @return The argument, if it is a product unit, or
                       a new instance of ProductUnit if the argument
                       is not a product unit.
        """
        if( unit == None ):
            return None
        assert( isinstance( unit, Unit ) )
        
        if( isinstance( unit, ProductUnit ) ):
            return unit
        else:
            return ProductUnit( unit, ONE )
    value_of = staticmethod( value_of )
    
    def strip_unit( unit ):
        """! @brief Return the contained unit of a unit, if
               it is a product unit,
               contains only one element,
               and has an exponent equal to one.
        """
        if( not isinstance( unit, ProductUnit ) ):
            return unit
        # strip unit if possible
        if( ( unit.get_unitCount() == 1 ) and\
           ( unit.get_unitPow( 0 ) == 1 ) and\
           ( unit.get_unitRoot( 0 ) == 1 ) ):
               return unit.get_unit( 0 )
        # unit can not be stripped
        return unit
    strip_unit = staticmethod( strip_unit )
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self.__elements__ )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self.__elements__ = state

# Example for ProductUnit
## This example shows how to create and use instances of
# units.ProductUnit. In general, instances of this class
# are not created directly. They are created by
# multiplying several other units.
# We will show this by a simple example using SI units.
# \see units.Unit.__mul__
# \see units.ProductUnit
# \example ProductUnits.py

class TransformedUnit( DerivedUnit ):
    """! @brief       This class provides an interface for a unit that has been
       derived from a unit using an operator.
     
       For example feet can be derived from meter.
      @see Unit.__mul__
      @see Unit.__truediv__
      @see Unit.__add__
      @see Unit.__sub__
      @note Instances of this class can be serialized using pickle.
    """
    
    ## What was the original unit.
    __parentUnit__ = None
    
    ## What is the operator to the parent unit.
    __operator__ = None
    
    def __init__( self, parent, operator ):
        """! @brief Default constructor.
             
              @param self
              @param parent The parent unit of the current unit.
              @param operator The operator that forms this unit from the parent unit.
        """
        assert( isinstance( parent, Unit ) )
        assert( isinstance( operator, operators.UnitOperator ) )
        
        self.__parentUnit__ = parent
        self.__operator__ = operator    
    
    def get_parent( self ):
        """! @brief Return the parent unit.
              @param self
              @return The unit before the transformation.
        """
        return self.__parentUnit__
    
    def get_system_unit( self ):
        """! @brief Get the corresponding system unit.
              @param self
              @return The corresponding system unit.
        """
        return self.__parentUnit__.get_system_unit()
    
    def to_parent_unit( self ):
        """! @brief Get the operator to convert to the parent unit.
              @param self
              @return The operator to the parent unit.
        """
        return ~self.__operator__
    
    def to_system_unit( self ):
        """! @brief Get the operator to convert to the corresponding system unit.
              @param self
              @return The operator to the system unit.
        """
        return self.__parentUnit__.to_system_unit() * ~self.__operator__
    
    def __eq__( self, other ):
        """! @brief Compare two transformed units.
              Two transformed units are equal, if their transformation as
              well as their parent units are equal.
              @param self
              @param other Another instance of a transformed unit.
              @return True, if the units are equal.
        """
        if( isinstance( other, ProductUnit ) ):
            other = ProductUnit.strip_unit( other )
        if( not isinstance( other, TransformedUnit ) ):
            return False
        else:
            return self.__parentUnit__ == other.__parentUnit__ and \
                self.__operator__ == other.__operator__
                
    def __str__( self ):
        """! @brief Print the current unit.
              This function returns a string of the form 
              @f$(op\left(parentunit\right)@f$, for
              example @f$(K+273.15)@f$ for degrees celsius transformed from
              kelvins.
              @param self
              @return A string describing this unit.
              @see __ProductElement.__str__
              @see operators.UnitOperator.__str__
        """
        return "("+str( str( self.get_parent() ) +\
                str( ~self.to_parent_unit() ) )+")"
    
    def __getstate__( self ):
        """! @brief Serialization using pickle.
              @param self
              @return A string that represents the serialized form
                      of this instance.
        """
        return ( self.__parentUnit__, self.__operator__ )
    
    def __setstate__( self, state ):
        """! @brief Deserialization using pickle.
              @param self
              @param state The state of the object.
        """
        self.__parentUnit__, self.__operator__ = state

# Example for TransformedUnits
## This example shows how to use the instances of units.TransformedUnit.
# In general, it is not necessary to instance the units.TransformedUnit
# class directly. Instances of units.TransformedUnit are intended to be 
# created implicitly by applying transformation to other units 
# (i.e. BaseUnits). We will show this here by transforming
# a SI base unit.
# \see units.Unit.__add__
# \see units.Unit.__truediv__
# \see units.Unit.__mul__
# \see units.TransformedUnit
# \example TransformedUnits.py

### Global Variables ###

## \brief Global units Manager that keeps track of the units and dimensions
# created.
_UNITS_MANAGER = UnitsManager()

## Predefined global dimension for the Length.
LENGTH      = Dimension( "L" )
## Predefined global dimension for the Mass.
MASS        = Dimension( "M" )
## Predefined global dimension for the Time.
TIME        = Dimension( "t" )
## Predefined global dimension for the Electric Current.
CURRENT     = Dimension( "I" )

#__unicode   = u"\u03b8"
#__char      = __unicode.encode( "UTF-8" )
## Predefined global dimension for the Temperature.
TEMPERATURE = Dimension( 'u"\N{Greek Small Letter Theta}"' )
## Predefined global dimension for the Amount of Substance.
SUBSTANCE   = Dimension( "n" )
## Predefined global dimension for Luminous Intensity.
LUMINOUS_INTENSITY = Dimension( "Li" )

## Dimensionless unit ONE.
ONE = ProductUnit()

## Predefined global dimension for a dimensionless quantity.
NONE = Dimension( ONE )

## @}
