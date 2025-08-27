## \file qexceptions.py
#  \brief This file contains a variety of exception definitions that are used 
#  by the quantities package.
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#          Thomas Reidemeister</a>

## \namespace scuq::qexceptions
# \brief This namespace contains classes defining custom exceptions of
#        this library.

## \defgroup qexceptions The Exceptions Module
#
# This module contains the classes to model, handle, and use special
#  qexceptions that may occur while using of units and quantities.
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#         Thomas Reidemeister</a>
# \addtogroup qexceptions 
# @{

class QuantitiesException( BaseException ):
    """! @brief       General class for qexceptions of this module.
    """
    
    def __init__( self, *args ):
        """! @brief Default constructor.
             
               @param self
               @param args Arguments of this exception
        """
        BaseException.__init__( self, *args )

class UnitExistsException( QuantitiesException ):
    """! @brief       Exception that is raised when a dimension, base unit, or
       alternate unit of the same type has already been created.
      @see units.BaseUnit
      @see units.AlternateUnit
      @see units.Dimension
    """
    
    def __init__( self, unit, *args ):
        """! @brief Default constructor.
             
               @param self
               @param unit The unit that raised this exception.
               @param args Additional arguments of this exception.
        """
        QuantitiesException.__init__( self, *args )
        self._unit = unit
        
    def __str__( self ):
        """! @brief Returns a string describing this exception.
              @param self
              @return A string that describes this exception.
        """
        return QuantitiesException.__str__( self )+" :"+\
               self._unit.__str__()
    
class ConversionException( QuantitiesException ):
    """! @brief       General exception that is raised whenever a
       unit conversion fails.
       @see units.Unit.to_system_unit
       @see units.Unit.get_operator_to
       @see operators.UnitOperator
    """
    
    def __init__( self, unit, *args ):
        """! @brief Default constructor
              @param self
              @param unit Instance of a unit that raised
                     the exception.
              @param args Additional arguments of this exception.
        """
        QuantitiesException.__init__( self, *args )
        self._unit = unit
        
    def __str__( self ):
        """! @brief Returns a string describing this exception.
              @param self
              @return A string that describes the exception.
        """
        return QuantitiesException.__str__( self )+" :"+\
               self._unit.__str__()
               
class NotDimensionlessException( QuantitiesException ):
    """! @brief       Exception that is raised whenever a
       a unit is not dimensionless where it has to be.
    """
    
    def __init__( self, unit, *args ):
        """! @brief Default constructor
              @param self
              @param unit Instance of a unit that raised
                     the exception.
              @param args Additional arguments of this exception.
        """
        QuantitiesException.__init__( self, *args )
        self._unit = unit
        
    def __str__( self ):
        """! @brief Returns a string describing this exception.
              @param self
              @return A string that describes the exception.
        """
        return QuantitiesException.__str__( self )+" :"+\
               self._unit.__str__()

class UnknownUnitException( QuantitiesException ):
    """! @brief       An exception that is raised whenever an unexpected unit was used.
       @see si.SIModel.get_dimension
    """
    
    def __init__( self, unit, *args ):
        """! @brief The default constructor.
              @param self
              @param unit An instance of a unit that is unknown.
              @param args Additional arguments of this exception.
        """
        QuantitiesException.__init__( self, *args )
        self._unit = unit
        
    def __str__( self ):
        """! @brief Returns a string describing this exception.
              @param self
              @return String that describes the exception.
        """
        return QuantitiesException.__str__( self )+" :"+\
               self._unit.__str__()

## @}
