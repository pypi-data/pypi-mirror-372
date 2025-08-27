## \mainpage SCUQ - A Class Library for the Evaluation of Scalar- and Complex-valued Uncertain Quantities.
#
#  This class library supports the evaluation of scalar (real) and complex-valued uncertain quantities.
#  We divided the the library into the following modules. 
#  <ul>
#    <li> The module scuq.units supports modeling and converting physical units. 
#    <li> The module scuq.si uses the units module to support SI units.
#    <li> The module scuq.arithmetic. This module contains functions
#         to assist the other modules in this libary. It also
#         contains a RationalNumber type according to PEP-239 (see link shown below).
#    <li> The module scuq.quantities allows combining units, numeric
#         types, and uncertain components modeling physical quantities.
#    <li> The module scuq.ucomponents module models uncertain values. 
#         It can be used in combination with the other modules  
#         to model uncertainty in measurements by assigning an uncertainty 
#         to a numeric value and propagating it through a mathematical
#         model. The implementation uses the GUM-Tree pattern 
#         (see references shown below).
#    <li> The module scuq.cucomponents can be used to evaluate the
#         uncertainty of complex-valued models in a similar way as the
#         module scuq.ucomponents does.
#  </ul>
#  \attention In contrast to the practice of explicit type checking and 
#  raising a <tt>TypeError</tt> if an argument is invalid, we use assertions. This
#  gives you the opportunity to check your assignments in debug mode and 
#  running (relatively) fast code in release mode. The debug mode is enabled 
#  by default when invoking Python with <tt>python \<Your Code\></tt> and 
#  <tt>python -O \<Your Code\></tt> for release mode.
#  \attention You should use <tt>UTF-8</tt> as default encoding because Greek 
#  letters represent some physical quantities, units, and dimensions. However, 
#  you will still be able to use this library if you have another default encoding. 
#  The symbols will then not print correctly.
#  \attention In this documentation the term <tt>integer</tt> refers to
#             they Python type <tt>int</tt> as well as <tt>long</tt>. This
#             library casts all <tt>int</tt> arguments to <tt>long</tt> 
#             where applicable. 
#             This makes overflows unlikely, since the precision of 
#             <tt>long</tt> is limited by the platforms available memory in Python; 
#             that said, you will most likely encounter a 
#             <tt>MemoryError</tt> if the accuracy of a long variable is 
#             exausted. 
#  \note The patterns used to create the units, dimensions, and unit-operators
#        have been inspired by Java Specification Request 275 that is 
#        implemented in <tt>JScience</tt> (see link shown below), an
#        open-source library for scientific computing in Java.
#  \note The design patterns used for the evaluation of uncertainty are 
#        subject to United States patent number 7,130,761. You should 
#        arrange with the patent holders if you want to use this software 
#        within the 
#        United States of America for commercial purposes. Their patent claims
#        cover a wide variety of the field of automatic uncertainty 
#        propagation. Therefore our extensions to their proposal may also be 
#        subject to the claims of that patent. In order to stop the 
#        spread of e-patents in Europe, please support us 
#        and sign the petition for Software Patent Free Europe (see link shown below).
#  \note There exists an alternative package for Python issued by the patent 
#        holders that allows the automatic propagation of uncertainty.
#        Unfortunately this package does not provide any support for
#        physical quantities and units. This package does also not
#        integrate the standard numpy module and is therefore less flexible than
#        our package. 
#  \author Thomas Reidemeister
#  \see <ul>
#         <li> \ref install "Installation Instructions".
#					<li> The Java Scientific Library<br>
#       	     (<a href="http://www.jscience.org">http://www.jscience.org</a>)
#         <li> Java Specification Request - 275<br>
#              (<a href="http://www.jcp.org/jsr/detail/275.jsp">http://www.jcp.org/jsr/detail/275.jsp</a>)
#         <li> "The "GUM Tree": A software design pattern for handling<br>
#               measurement uncertainty"; B. D. Hall; Industrial Research
#               Report 1291; Measurements Standards Laboratory New Zealand (2003).
#         <li> "byGUM: A Python software package for calculating measurement
#              uncertainty"; B. D. Hall; Industrial Research
#              Report 1305; Measurements Standards Laboratory New Zealand (2005).
#         <li> Petition for a Software Patent Free Europe<br>
#              (<a href="http://www.noepatents.org/">http://www.noepatents.org/</a>).
#         <li> United States Patent and Trademark Office<br>
#              (<a href="http://www.uspto.gov/patft/index.html">http://www.uspto.gov/patft/</a>)
#         <li> PEP-239 - Adding a Rational Type to Python<br>
#              (<a href="http://www.python.org/dev/peps/pep-0239/">http://www.python.org/dev/peps/pep-0239/</a>)
#       </ul>

## \file __init__.py
#  \brief This file is evaluated whenever the quantities package is loaded.
# 
#  It loads the modules neccessary for operating this package. It also
#  performs some global initialization.
#  \author Thomas Reidemeister

## \namespace scuq::__init__
#  \brief This namespace does only contain variables for global initialization.

## \namespace scuq
#  \brief The namespace containing this library.

## \page Notation Coercion Rules
# In this section we provide a complete set of coercion rules.
# These rules are used to convert among the data types of SCUQ to
# preserve the semantics. Coercion is performed whenever one of 
# SCUQs types is involved in a binary operation.
# The goal of the coercion rules is to provide equal data types
# for both arguments of a binary operation;
# for example, the multiplication of a rational number and a
# floating point number should be performed by converting
# the rational number to a floating point number. Coercion is symmeric. 
# Therefore the same applies to multiplications of floating point
# with rational numbers.
# We denote the rule as follows. 
# \f[{a} \times {f} \rightarrow {f(a)} \times {f} \f]
# We denote the rules as follows:
# <ul>
#   <li>\f${f}\f$ and \f${f(x)}\f$ refer to instances of 
#       <tt>float</tt>. The second argument is used to 
#       express the conversion of \f$x\f$ to a <tt>float</tt>.
#   <li>\f${z}\f$ and \f${z(x)}\f$ refer to instances of 
#       <tt>long</tt> and <tt>int</tt>. The second argument is used to 
#       express the conversion of \f$x\f$ to a <tt>long</tt>.
#   <li>\f${c}\f$ and \f${c(x)}\f$ refer to instances of 
#       <tt>complex</tt>. The second argument is used to 
#       express the conversion of \f$x\f$ to a <tt>complex</tt>.
#   <li>\f${nd}\f$ refers to instances of <tt>numpy.ndarray</tt>.
#   <li>\f${a}\f$ and \f${a(x)}\f$ refer to instances of 
#       arithmetic.RationalNumber. The second argument is used to 
#       express the conversion of \f$x\f$ to an instance of 
#       arithmetic.RationalNumber. The conversion is implemented in
#       arithmetic.RationalNumber.value_of.
#   <li>\f${q}\f$ and \f${q(x)}\f$ refer to instances of 
#       quantities.Quantity. The second argument is used to 
#       express the conversion of \f$x\f$ to an instance of 
#       quantities.Quantity. The conversion is implemented in
#       quantities.Quantity.value_of.
#   <li>\f${u_s}\f$ and \f${u_s(x)}\f$ refer to instances of 
#       ucomponents.UncertainComponent. The second argument is used to 
#       express the conversion of \f$x\f$ to an instance of 
#       ucomponents.UncertainComponent. The conversion is implemented in
#       ucomponents.UncertainComponent.value_of.
#   <li>\f${u_c}\f$ and \f${u_c(x)}\f$ refer to instances of 
#       cucomponents.CUncertainComponent. The second argument is used to 
#       express the conversion of \f$x\f$ to an instance of 
#       cucomponents.CUncertainComponent. The conversion is implemented in
#       cucomponents.CUncertainComponent.value_of.
#   <li>\f${u}\f$ denotes an instance of units.Unit.
#   <li>\f${\emptyset}\f$ denotes an undefined operation 
#       (i.e. the coercion raises an exception).
# </ul>
#
# <b>The cohercion rules by type:</b>
# <ul>
#    <li>Type: arithmetic.RationalNumber
#        \f{eqnarray}
#            a \times a & \rightarrow & a \times a \\
#            a \times z & \rightarrow & a \times a(z) \\
#            a \times c & \rightarrow & c(a) \times c \\
#            a \times f & \rightarrow & f(a) \times f \\
#            a \times q & \rightarrow & q(a) \times q \\
#            a \times u_s & \rightarrow & u_s(a) \times u_s \\
#            a \times u_c & \rightarrow & u_c(a) \times u_c \\
#            a \times u & \rightarrow & \emptyset \\
#            a \times nd & \rightarrow & \emptyset
#        \f}
#    <li>Type: quantities.Quantity
#        \f{eqnarray}
#            q \times q & \rightarrow & q \times q \\
#            q \times z & \rightarrow & q \times q(z) \\
#            q \times c & \rightarrow & q \times q(c) \\
#            q \times f & \rightarrow & q \times q(f) \\
#            q \times u_s & \rightarrow & q \times q(u_s) \\
#            q \times u_c & \rightarrow & q \times q(u_c) \\
#            q \times nd & \rightarrow & q \times q(nd) \\
#            q \times u & \rightarrow & \emptyset
#        \f}
#    <li>Type: ucomponents.UncertainComponent
#        \f{eqnarray}
#            u_s \times u_s & \rightarrow & u_s \times u_s \\
#            u_s \times z & \rightarrow & u_s \times u_s(z) \\
#            u_s \times f & \rightarrow & u_s \times u_s(f) \\
#            u_s \times nd & \rightarrow & \emptyset \\
#            u_s \times u_c & \rightarrow & \emptyset \\
#            u_s \times c & \rightarrow & \emptyset \\
#            u_s \times u & \rightarrow & \emptyset
#        \f}
#    <li>Type: cucomponents.CUncertainComponent
#        \f{eqnarray}
#            u_c \times u_c & \rightarrow & u_c \times u_c \\
#            u_c \times z & \rightarrow & u_c \times u_c(z) \\
#            u_c \times f & \rightarrow & u_c \times u_c(f) \\
#            u_c \times c & \rightarrow & u_c \times u_c(c) \\
#            u_c \times nd & \rightarrow & \emptyset \\
#            u_c \times u & \rightarrow & \emptyset
#        \f}
#
# </ul> 
# \attention The binary operators from <tt>numpy</tt>, such as 
#            numpy.arctan2, and numpy.hypot, do not implement
#            coercion. Instead, they broadcast arctan2 to the first
#            argument. Therefore our coercion rules are not 
#            symmetric when using operators from numpy.

# documentation of supplementary files

## \page sup_files Files and Directories
# In this section we describe the files that are not included in the file documentation.
#
# <h2>AUTHORS</h2><br>
#
# This file contains the contact information of the authors of SCUQ.
#
# At the time this document was created, only Thomas Reidemeister is involved.
#
#
# <h2>doc.cfg</h2><br>
#
# Doxygen (see link below) uses this file to create the SCUQ reference manual automatically. 
#
# It contains the style- and output format definitions. Please do not directly invoke Doxygen on 
# this file; use the respective make target instead (<tt>make clean</tt>).
#
#
# <h2>Makefile</h2><br>
# 
# This file is used by GNU make to assist the installation of SCUQ and 
# perform a variety of administrative tasks.
#
# <ul>
# <li> Performing the self test (<tt>make test</tt>).
# <li> Creating the reference manual (<tt>make doc</tt>).
# <li> Building backups of the current state of the library (<tt>make backup</tt>).
# <li> Cleaning temporary files (<tt>make clean</tt>).
# </ul>
#
# A companion file is <tt>make_latex.sh</tt>. It is a script to create the PDF 
# documentation whenever <tt>make doc</tt> is invoked.
#
#
# <h2>examples</h2><br>
# 
# This directory contains the application examples described in this programming manual and in the Reidemeister thesis.
#
#
# <h2>doc</h2><br>
# 
# This directory is a placeholder for the reference manual if it is created from the source code. 
# By default the documentation is created in PDF- and HTML format.
#
# \see <ul>
# <li> SCUQ Installation Instructions
# <li> SCUQ Example Documentation (included in this manual)
# <li> "SCUQ - A Class Library for the Evaluation of Scalar- and Complex-valued Uncertain Quantities"; 
#      Thomas Reidemeister; Diploma-Thesis; Otto-von-Guericke University, Magdeburg, Germany (2007)
# <li> GNU Make (<a href="http://www.gnu.org/software/make/">http://www.gnu.org/software/make/</a>)
# <li> Doxygen (<a href="http://www.stack.nl/~dimitri/doxygen/">http://www.stack.nl/~dimitri/doxygen/</a>)
# </ul>

## \page install Installation
#
# <p>In this section we describe the installation of SCUQ in the user space. Note that the version 
# numbers of the tools refers to the minimum version required. SCUQ may also run using later versions.
# </p>
# 
# <p><h2>Minimum Requirements:</h2></p>
# <ul>
# <li>	Python 2.4, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	NumPy 1.0.1, installed as module in the Python distribution.
# <li>	A tool uncompressing zip files (e.g. Info-ZIP or 7-ZIP). We assume that a 
#   console application exists to unzip files from the command line that is registered in 
#   the <tt>PATH</tt> environment variable.
# </ul>
# 
# <p><h2>Optional Requirements:</h2></p>
# <ul>
# <li>	GNU Make, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	GNU Tar, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	Bzip2, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	Doxygen 1.5.1, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	Ghostscript 8.15.0, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	BSD Shell, installed and registered in the <tt>PATH</tt> environment variable.
# <li>	LaTeX and PDFLaTex, installed and registered in the <tt>PATH</tt> environment variable.
# </ul>
# 
# <p>Most of the optional tools required are included in recent Linux distributions 
# and Cygwin. Doxygen can be obtained using the link shown below.</p>
# 
# <p>We describe two types of the installation:</p>
# <ul>
# <li>	A minimal installation that installs SCUQ for the use in Python only.
# <li>	A comprehensive installation that installs the class library for the use in Python, 
#   performs the self-test, and generates the SCUQ reference manual. This installation 
#   can also generate backups of the current state of SCUQ 
#   (i.e. if it is modified by the user).
# </ul>
# 
# <p><h2>Minimal Installation</h2></p>
# 
# <ol>
# <li>	Copy the archive SCUQ.zip to the directory desired. We denote it as \<your project dir\>.
# <li>	Open a console (e.g. BASH on Linux, CMD.EXE on Windows)
# <li>	Change to the project directory using
#
#       <tt>cd \<your project dir\></tt>
#
# <li>	Unzip the archive SCUQ.zip using
#
#       <tt>unzip SCUQ.zip</tt>
#
#       You may also use other tools to uncompress the archive.
# <li>	The classes and modules are now unzipped into the directory
#
#       <tt>\<your project dir\>/SCUQ/</tt>
#
# <li>	Change to this directory using
#
#       <tt>cd SCUQ</tt>
#
# <li>Verify the compatibility of your platform running the suite of test cases using
#
#   <tt>python scuq/testcases.py</tt>
#
#   <p>The console output must not contain any exceptions. If it contains any exceptions then 
#   SCUQ will most likely not run on your system. These failures maybe due to a wrong 
#   configured Python installation or your platform does not meet the required floating-point 
#   accuracy.
# <li>If SCUQ passed the self-verification, you can use it in your software. Please copy the 
#   subdirectory <tt>scuq</tt> to the root of your project directory. Then you can import SCUQ using
#
#   <tt>from scuq import *</tt>
#
#   <p>in your projects code.</p>
# </ol>
# 
# <p><h2>Comprehensive Installation</h2></p>
#
# <ol>
# <li>	Perform the steps 1-6 of the minimal installation
# <li>Create the documentation and perform the self-verification using
#   
#   <tt>make</tt>
#
#   <p>The output of this command must not print any errors. Errors maybe 
#   due to a wrong installation of the tools required or your platform 
#   does meet the required floating-point accuracy.</p>
# <li><p>If SCUQ passed the self-verification, you can use it in your software. 
#   Please copy the subdirectory <tt>scuq</tt> to the root of your project directory. 
#   Then you can import SCUQ in your project using</p>
# 
#   <tt>from scuq import *</tt>
#
#   <p>The programming manual in HTML and PDF format is stored in the subdirectory doc.</p>
# </ol>
# 
# \see <ul>
# <li> Doxygen (<a href="http://www.stack.nl/~dimitri/doxygen/">http://www.stack.nl/~dimitri/doxygen/</a>)
# <li> Python (<a href="http://www.python.org/">http://www.python.org/</a>)
# <li> GNU (<a href="http://www.gnu.org/">http://www.gnu.org/</a>)
# <li> teTeX (<a href="http://www.tug.org/teTeX/">http://www.tug.org/teTeX/</a>)
# <li> MiKTeX (<a href="http://www.miktex.org/">http://www.miktex.org/</a>)
# <li> NumPy (<a href="http://www.scipy.org/">http://www.scipy.org/</a>)
# <li> Ghostscript (<a href="http://www.cs.wisc.edu/~ghost/">http://www.cs.wisc.edu/~ghost/</a>)
# <li> Info-ZIP (<a href="http://www.info-zip.org/">http://www.info-zip.org/</a>)
# <li> 7-ZIP (<a href="http://www.7-zip.org/">http://www.7-zip.org/</a>)
# <li> CygWin (<a href="http://cygwin.com/">http://cygwin.com/</a>)
# </ul>

## The modules contained within the quantities package.
__all__ = ["arithmetic", "units", "qexceptions", "si", "quantities", "operators", "ucomponents", "cucomponents"]

