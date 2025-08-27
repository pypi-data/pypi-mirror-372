## \file si.py
#  \brief This file contains the predefined SI units. 
# 
#  It models SI base units
#  and SI alternate units. The alternate units have been formed as
#  product other alternate SI units where possible as described in
#  NIST 330.
#  \see "The International System of Units"; Barry N. Taylor; NIST 330 (2001)
#  \author <a href="http://thomas.reidemeister.org/" target="_blank">
#  Thomas Reidemeister</a>

## \namespace scuq::si
# \brief This namespace contains the SI-units.

## \defgroup si The Standard System of Units Module
#
#  This module contains the predefined SI units. It models SI base units
#  and SI alternate units. The alternate units have been formed as
#  product other alternate SI units where possible as described in
#  NIST 330.
#  \see "The International System of Units"; Barry N. Taylor; NIST 330 (2001)
# \author <a href="http://thomas.reidemeister.org/" target="_blank">
#  Thomas Reidemeister</a>
# \addtogroup si 
# @{

# standard modules
import locale
import string
import sys

# local modules
import scuq.units as units
import scuq.qexceptions as qexceptions

class SIModel( units.PhysicalModel ):
    """! @brief       The interface for a physical model for SI units.
     
       The basic intend of this class is to provide an mapping between
       SI base units and physical dimensions. 
    """
    
    def __init__( self ):
        """! @brief Default constructor.
              @param self 
        """
        return None

    def get_dimension( self, unit ):
        """! @brief Get the pysical dimension that corresponds to the
               given SI base unit.
               @param  self
               @param  unit The unit to check the dimension for.
               @exception qexceptions.UnknownUnitException If the given 
                          parameter is no SI base unit.
               @return The corresponding physical dimension.
        """
        if ( unit == METER ):
            return units.LENGTH
        if ( unit == KILOGRAM ):
            return units.MASS
        if ( unit == SECOND ):
            return units.TIME
        if ( unit == AMPERE ):
            return units.CURRENT
        if ( unit == MOLE ):
            return units.SUBSTANCE
        if ( unit == CANDELA ):
            return units.LUMINOUS_INTENSITY
        if ( unit == KELVIN ):
            return units.TEMPERATURE
        # This should not happen, since we assume that only SI
        # units are used.
        raise qexceptions.UnknownUnitException( "The unit is no SI-unit ", 
                                                unit )

# Check if unicode is enabled (i.e. if the symbols are shown correctly)
# language, encoding = locale.getdefaultlocale()
# if( string.lower( encoding ) != "utf-8" ):
#     sys.stderr.write( "You should use UTF-8 instead of "+encoding
#                       +" as encoding, or the "
#                       +"SI units won't display correctly\n" )

# Change the default model for the Quantities.units module to 
# the physical model of SI units
_model     = SIModel()
units.set_default_model( _model )

## Unit instance to model the BaseUnit Ampere.
AMPERE   = units.BaseUnit( "A" )
## Unit instance to model the BaseUnit Candela.
CANDELA  = units.BaseUnit( "cd" )
## Unit instance to model the BaseUnit Kelvin.
KELVIN   = units.BaseUnit( "K" )
## Unit instance to model the BaseUnit Kilogram.
KILOGRAM = units.BaseUnit( "kg" )
## Unit instance to model the BaseUnit Meter.
METER    = units.BaseUnit( "m" )
## Unit instance to model the BaseUnit Mol.
MOLE     = units.BaseUnit( "mol" )
## Unit instance to model the BaseUnit Second.
SECOND   = units.BaseUnit( "s" )

# SI derived units.
# These units are modelled as product of the base unit and 
# other alternate SI units. They do have a different symbol.

## Unit instance to model the SI unit Radian.
# \attention Because this library keeps only the canonical form
#            of the product of base units the Radian is compatible 
#            to the neutral 1. Therefore its system unit is modelled 
#            as "1" not as \f$\frac{m}{m}\f$.
RADIAN      = units.AlternateUnit( "rad", units.ONE )

## Unit instance to model the SI base unit Steradian.
# \attention Because this library keeps only the canonical form
#            of the product of base units the Radian is compatible to 
#            the neutral 1. Therefore its system unit is modelled 
#            as "1" not as \f$\frac{m^2}{m^2}\f$.
STERADIAN   = units.AlternateUnit( "sr", units.ONE )

## Unit instance to model the SI unit Herz.
HERTZ       = units.AlternateUnit( "Hz", ~SECOND)

## Unit instance to model the SI unit Newton.
NEWTON      = units.AlternateUnit( "N", KILOGRAM * METER / ( SECOND ** 2 ) )

## Unit instance to model the SI unit Pascal.
PASCAL      = units.AlternateUnit( "Pa", NEWTON / ( METER ** 2 ) )

## Unit instance to model the SI unit Joule.
JOULE       = units.AlternateUnit( "J", NEWTON * METER )

## Unit instance to model the SI unit Watt.
WATT        = units.AlternateUnit( "W", JOULE / SECOND )

## Unit instance to model the SI unit Coulomb.
COULOMB     = units.AlternateUnit( "C", AMPERE * SECOND )

## Unit instance to model the SI unit Volt.
VOLT        = units.AlternateUnit( "V", WATT / AMPERE )

## Unit instance to model the SI unit Farad.
FARAD       = units.AlternateUnit( "F", COULOMB / VOLT )

## Unit instance to model the SI unit Ohm.
# \note The <tt>UTF-8</tt> encoded string stands for \f$\Omega\f$.  HGK: changed to Ohm
OHM         = units.AlternateUnit( 'u"\N{Greek Capital Letter Omega}"',                         # ( u"\u03A9" ).encode( "UTF-8" ), 
                                   VOLT / AMPERE )

## Unit instance to model the SI unit Siemens.
SIEMENS     = units.AlternateUnit( "S", AMPERE / VOLT )

## Unit instance to model the SI unit Weber.
WEBER       = units.AlternateUnit( "Wb", VOLT * SECOND )

## Unit instance to model the SI unit Tesla.
TESLA       = units.AlternateUnit( "T", WEBER / ( METER**2 ) )

## Unit instance to model the SI unit Henry.
HENRY       = units.AlternateUnit( "H", WEBER / AMPERE )

## Unit instance to model the SI unit degree Celsius.
CELSIUS     = KELVIN + 273.15

## Unit instance to model the SI unit Lumen.
LUMEN       = units.AlternateUnit( "lm", CANDELA*STERADIAN )

## Unit instance to model the SI unit Lux.
LUX         = units.AlternateUnit( "lx", LUMEN/( METER*METER ) )

## Unit instance to model the SI unit Becquerel.
BECQUEREL   = units.AlternateUnit( "Bq", ~SECOND )

## Unit instance to model the SI unit Gray.
GRAY        = units.AlternateUnit( "Gy", JOULE/KILOGRAM )

## Unit instance to model the SI unit Sivert.
SIVERT      = units.AlternateUnit( "Sv", JOULE/KILOGRAM )

## Unit instance to model the SI unit Katal.
KATAL       = units.AlternateUnit( "kat", MOLE/SECOND )


## @}
