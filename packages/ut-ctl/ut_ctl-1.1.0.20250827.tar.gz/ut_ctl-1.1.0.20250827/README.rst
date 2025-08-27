######
ut_ctl
######

********
Overview
********

.. start short_desc

**IO Control and Package Management Utilities**

.. end short_desc

************
Installation
************

.. start installation

The package ``ut_ctl`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_ctl

To install with ``conda``:

.. code-block:: shell

	$ conda install -c conda-forge ut_ctl

.. end installation

***************
Package logging 
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Package ``ut_ctl`` consist of the following file types (c.f.: **Appendix**):

#. **Special files:** (c.f.: **Appendix:** *Special python package files*)

#. **Dunder modules:** (c.f.: **Appendix:** *Special python package modules*)

#. **Sub-packages**

   a. **ioc:** *(I/O Control)*

      #. **Special files:** (c.f.: **Appendix:** *Special python package files*)

      #. **Dunder modules:** (c.f.: **Appendix:** *Special python package modules*)

      #. **Modules**

          #. *jinja2_.py*
          #. *yaml_.py*

   #. **utils:** *(Utilities)*

      #. **Special files:** (c.f.: **Appendix:** *Special python package files*)

      #. **Dunder modules:** (c.f.: **Appendix:** *Special python package modules*)

      #. **Modules**

         #. *fnc.py*
         #. *pacmod.py*
         #. *pac.py*
         #. *srv.py*


********************************
Sub-package: `ioc (I/O Control)`
********************************

Modules
=======

The Sub-package ``ioc`` contains the following modules.

  .. Modules-of-Sub-package-ioc-label:
  .. table:: *Modules of Sub-package ioc*

   +----------+-------------------------------------+
   |Name      |Decription                           |
   +==========+=====================================+
   |jinja\_.py|I/O Control methods for jinja2 files.|
   +----------+-------------------------------------+
   |yaml\_.py |I/O Control methods for yaml files.  |
   +----------+-------------------------------------+

Module: jinja2\_.py
-------------------

The Module ``jinja2_.py`` contains the static class ``Jinja2``

jinja2\_.py Class: Jinja2
^^^^^^^^^^^^^^^^^^^^^^^^^

The static Class ``Jinja2`` provides I/O Control methods for Jinja2 files;
it contains the subsequent methods.

Jinja2 Methods
""""""""""""""

  .. Jinja2-Methods-label:
  .. table:: *Jinja2 Methods*

   +-------------+------------------------------+
   |Name         |Description                   |
   +=============+==============================+
   |read         |Read log file path with jinja |
   +-------------+------------------------------+
   |read_template|Read log file path with jinja2|       
   +-------------+------------------------------+

Jinja2 Method: read
"""""""""""""""""""

Parameter
.........

  .. Jinja2-Method-read-Parameter-label:
  .. table:: *Jinja2 Method read: Parameter*

   +--------+-----+---------------+
   |Name    |Type |Description    |
   +========+=====+===============+
   |pacmod  |TnDic|               |
   +--------+-----+---------------+
   |filename|str  |               |
   +--------+-----+---------------+

Jinja2 Method: read_template
""""""""""""""""""""""""""""

Parameter
.........

  .. Jinja2-Method-read_template-Parameter-label:
  .. table:: *Jinja2 Method read_template: Parameter*

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |path|TyPath|Path string|
   +----+------+-----------+

Return Value
............

  .. Jinja2-Method-read_template-Return-Value-label:
  .. table:: *Jinja2 Method read_template: Return Value*

   +----+----------------+---------------+
   |Name|Type            |Description    |
   +====+================+===============+
   |    |TyJinja2Template|Jinja2 Template|
   +----+----------------+---------------+

Module: yaml\_.py
-----------------

The Module ``yaml_.py`` contains the static class ``Yaml``.

yamml\_.py Class: Yaml
^^^^^^^^^^^^^^^^^^^^^^

The static Class ``Yaml`` provides I/O Control functions for Yaml files;
it contains the subsequent methods

Yaml Methods
""""""""""""

  .. Yaml-Methods-label:
  .. table:: *Yaml Methods*

   +----+----------------------------------------------+
   |Name|Description                                   |
   +====+==============================================+
   |load|Load yaml string into any object using yaml   |
   |    |loader; default loader is yaml.safeloader     |
   +----+----------------------------------------------+
   |read|Read yaml file path into any object using yaml|
   |    |loder; default loader is yaml.safeloader      |
   +----+----------------------------------------------+

Yaml Method: read_with_safeloader
"""""""""""""""""""""""""""""""""

Parameter
.........

  .. Yaml-Method-read_with_safeloader-Parameter-label:
  .. table:: *Yaml Method read_with_safeloader: Parameter*

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |path|TyPath|Path string|
   +----+------+-----------+

Yaml Method: write
""""""""""""""""""

Parameter
.........

  .. Yaml-Method-write-Parameter:
  .. table:: *Yaml Method write: Parameter*

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |path|TyPath|Path string|
   +----+------+-----------+
   |obj |TyAny |Object     |
   +----+------+-----------+

******************
Sub package: utils
******************

utils Modules
=============

The Sub-package ``utils`` contains the following modules.

  .. utils-Modules-label:
  .. table:: *utils Modules*

   +---------+---------------------------+
   |Name     |Functionality              |
   +=========+===========================+
   |pacmod.py|Manage Packages and Modules|
   +---------+---------------------------+
   |pac.py   |Manage Packages            |
   +---------+---------------------------+

utils Module: pacmod.py
-----------------------

The Module ``pacmod.py`` contains the static class ``PacMod``.

pacmod.py Class: PacMod
^^^^^^^^^^^^^^^^^^^^^^^

The static Class ``PacMod`` is used to get the Package- and Module-name.
it contains the subsequent methods

PacMod Methods
""""""""""""""

  .. PacMod Methods-label:
  .. table:: *PacMod Methods*

   +-------------------+-----------------------------------+
   |Name               |Description                        |
   +===================+===================================+
   |sh_d_pacmod        |Show (Get) package module          |
   |                   |dictionary for class.              |
   +-------------------+-----------------------------------+
   |sh_path_module_yaml|show package module yaml file path.|
   +-------------------+-----------------------------------+
   |sh_path_keys_yml   |show keys.yaml file path.          |
   +-------------------+-----------------------------------+
   |sh_path_cfg_yml    |show cfg.yaml file path.           |
   +-------------------+-----------------------------------+
   |sh_dir_type        |show type specific file directory. |
   +-------------------+-----------------------------------+
   |sh_path_pattern    |show pattern file path.            |
   +-------------------+-----------------------------------+

PacMod Method: sh_d_pacmod
""""""""""""""""""""""""""

Parameter
.........

  .. PacMod-Method-sh_d_pacmod-label:
  .. table:: *PacMode Method sh_d_pacmod: Parameter*

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |path|TyPath|Path string|
   +----+------+-----------+

########
Appendix
########

***************
Package Logging
***************

Description
===========

The Standard or user specifig logging is carried out by the log.py module of the logging
package **ka_uts_log** using the standard- or user-configuration files in the logging
package configuration directory:

* **<logging package directory>/cfg/ka_std_log.yml**,
* **<logging package directory>/cfg/ka_usr_log.yml**.

The Logging configuration of the logging package could be overriden by yaml files with the
same names in the application package- or application data-configuration directories:

* **<application package directory>/cfg**
* **<application data directory>/cfg**.

Log message types
=================

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Log types and Log directories
-----------------------------

Single or multiple Application log directories can be used for each message type:

  .. Log-types-and-Log-directories-label:
  .. table:: *Log types and directoriesg*

   +--------------+---------------+
   |Log type      |Log directory  |
   +--------+-----+--------+------+
   |long    |short|multiple|single|
   +========+=====+========+======+
   |debug   |dbqs |dbqs    |logs  |
   +--------+-----+--------+------+
   |info    |infs |infs    |logs  |
   +--------+-----+--------+------+
   |warning |wrns |wrns    |logs  |
   +--------+-----+--------+------+
   |error   |errs |errs    |logs  |
   +--------+-----+--------+------+
   |critical|crts |crts    |logs  |
   +--------+-----+--------+------+

Application parameter for logging
---------------------------------

  .. Application-parameter-used-in-log-naming-label:
  .. table:: *Application parameter used in log naming*

   +-----------------+---------------------------+------+------------+
   |Name             |Decription                 |Values|Example     |
   +=================+===========================+======+============+
   |dir_dat          |Application data directory |      |/otev/data  |
   +-----------------+---------------------------+------+------------+
   |tenant           |Application tenant name    |      |UMH         |
   +-----------------+---------------------------+------+------------+
   |package          |Application package name   |      |otev_xls_srr|
   +-----------------+---------------------------+------+------------+
   |cmd              |Application command        |      |evupreg     |
   +-----------------+---------------------------+------+------------+
   |pid              |Process ID                 |      |681025      |
   +-----------------+---------------------------+------+------------+
   |log_ts_type      |Timestamp type used in     |ts,   |ts          |
   |                 |logging files|ts, dt       |dt'   |            |
   +-----------------+---------------------------+------+------------+
   |log_sw_single_dir|Enable single log directory|True, |True        |
   |                 |or multiple log directories|False |            |
   +-----------------+---------------------------+------+------------+

Log files naming
----------------

Naming Conventions
^^^^^^^^^^^^^^^^^^

  .. Naming-conventions-for-logging-file-paths-label:
  .. table:: *Naming conventions for logging file paths*

   +--------+-------------------------------------------------------+-------------------------+
   |Type    |Directory                                              |File                     |
   +========+=======================================================+=========================+
   |debug   |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |info    |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |warning |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |error   |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |critical|/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+

Naming Examples
^^^^^^^^^^^^^^^

  .. Naming-examples-for-logging-file-paths-label:
  .. table:: *Naming examples for logging file paths*

   +--------+----------------------------------------+------------------------+
   |Type    |Directory                               |File                    |
   +========+========================================+========================+
   |debug   |/data/otev/umh/RUN/otev_srr/evupreg/logs|debs_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |info    |/data/otev/umh/RUN/otev_srr/evupreg/logs|infs_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |warning |/data/otev/umh/RUN/otev_srr/evupreg/logs|wrns_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |error   |/data/otev/umh/RUN/otev_srr/evupreg/logs|errs_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |critical|/data/otev/umh/RUN/otev_srr/evupreg/logs|crts_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+

******************
Python Terminology
******************

Python Packages
===============

Overview
--------

  .. Python Packages-Overview-label:
  .. table:: *Python Packages Overview*

   +---------------------+-----------------------------------------------------------------+
   |Name                 |Definition                                                       |
   +=====================+=================================================================+
   |Python package       |Python packages are directories that contains the special module |
   |                     |``__init__.py`` and other modules, packages files or directories.|
   +---------------------+-----------------------------------------------------------------+
   |Python sub-package   |Python sub-packages are python packages which are contained in   |
   |                     |another pyhon package.                                           |
   +---------------------+-----------------------------------------------------------------+
   |Python package       |directory contained in a python package.                         |
   |sub-directory        |                                                                 |
   +---------------------+-----------------------------------------------------------------+
   |Python package       |Python package sub-directories with a special meaning like data  |
   |special sub-directory|or cfg                                                           |
   +---------------------+-----------------------------------------------------------------+


Examples
--------

  .. Python-Package-sub-directory-Examples-label:
  .. table:: *Python Package sub-directory-Examples*

   +-------+------------------------------------------+
   |Name   |Description                               |
   +=======+==========================================+
   |bin    |Directory for package scripts.            |
   +-------+------------------------------------------+
   |cfg    |Directory for package configuration files.|
   +-------+------------------------------------------+
   |data   |Directory for package data files.         |
   +-------+------------------------------------------+
   |service|Directory for systemd service scripts.    |
   +-------+------------------------------------------+

Python package files
====================

Overview
--------

  .. Python-package-files-overview-label:
  .. table:: *Python package overview files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python package|Files within a python package.                           |
   |files         |                                                         |
   +--------------+---------------------------------------------------------+
   |Python package|Package files which are not modules and used as python   |
   |special files |marker files like ``__init__.py``.                       |
   +--------------+---------------------------------------------------------+
   |Python package|Files with suffix ``.py``; they could be empty or contain|
   |module        |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Python package|Modules like ``__init__.py`` or ``main.py`` with special |
   |special module|names and functionality.                                 |
   +--------------+---------------------------------------------------------+

Examples
--------

Python package special files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. Python-package-special-files-label:
  .. table:: *Python package special files*

   +--------------+-----------+-----------------------------------------------------------------+
   |Name          |Type       |Description                                                      |
   +==============+===========+=================================================================+
   |py.typed      |Type       |The ``py.typed`` file is a marker file used in Python packages to|
   |              |checking   |indicate that the package supports type checking. This is a part |
   |              |marker     |of the PEP 561 standard, which provides a standardized way to    |
   |              |file       |package and distribute type information in Python.               |
   +--------------+-----------+-----------------------------------------------------------------+

Python package special modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. Python-package-special-modules-label:
  .. table:: *Python package special modules*

   +--------------+-----------+-----------------------------------------------------------------+
   |Name          |Type       |Description                                                      |
   +==============+===========+=================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to |
   |              |directory  |execute initialisation code or mark the directory it contains as |
   |              |marker     |a package. The Module enforces explicit imports and thus clear   |
   |              |file       |namespace use and call them with the dot notation.               |
   +--------------+-----------+-----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as an entry point for   |
   |              |for the    |the package. The module is executed when the package is called   |
   |              |package    |by the interpreter with the command **python -m <package name>**.|
   +--------------+-----------+-----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment       |
   |              |file       |statements used in Versioning.                                   |
   +--------------+-----------+-----------------------------------------------------------------+

Python methods
==============

Overview
--------

  .. Python-methods-overview-label:
  .. table:: *Python methods overview*

   +---------------------+--------------------------------------------------------+
   |Name                 |Description                                             |
   +=====================+========================================================+
   |Python method        |Python functions defined in python modules.             |
   +---------------------+--------------------------------------------------------+
   |Python special method|Python functions with special names and functionalities.|
   +---------------------+--------------------------------------------------------+
   |Python class         |Classes defined in python modules.                      |
   +---------------------+--------------------------------------------------------+
   |Python class method  |Python methods defined in python classes                |
   +---------------------+--------------------------------------------------------+

Examples
--------

  .. Python-methods-examples-label:
  .. table:: *Python methods examples*

   +--------+------------+----------------------------------------------------------+
   |Name    |Type        |Description                                               |
   +========+============+==========================================================+
   |__init__|class object|The special method ``__init__`` is called when an instance|
   |        |constructor |(object) of a class is created; instance attributes can be|
   |        |method      |defined and initalized in the method.                     |
   +--------+------------+----------------------------------------------------------+

#################
Table of Contents
#################

.. contents:: **Table of Content**
