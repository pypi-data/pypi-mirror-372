Command Reference
=================

Many of the references below deal with the terms WORKBOOK and WORKSHEET.  These
terms have the following meaning in the context of the artemis_sg project.

* WORKBOOK: A spreadsheet object.  This object is a container that may have one
  or more WORKSHEET objects inside of it.  These objects are expected to be one
  of the following sources.
  * Google Sheet: As identified by a Google Sheet ID string.
  * Excel (xlsx) file: As identified by a file path.
* WORKSHEET: A specific sheet that contains data.  This object is always contained
  within a WORKBOOK.  These objects are identified by a string name.  Both Excel
  and Google Sheets set the default name to the first sheet object as "Sheet1".

The documentation refers to the combination of these identifiers by combining them
with a colon in the format WORKBOOK:WORKSHEET.

Hello, there!

.. click:: artemis_sg.cli:cli
  :prog: artemis_sg
  :nested: full
