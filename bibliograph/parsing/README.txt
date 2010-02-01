bibliograph.parsing 
===================

Each parser accepts input from a given bibliographic reference format and outputs
a list of python dictionaries, one for each entry listed in the input source.  Each
of these dictionaries will contain some  number of the following fields:
    
+---------------------+-----------+---------------------------------------------------+
| Field Name:         | Required: |  Description of Field Contentsx:                  |
+=====================+===========+===================================================+
|**reference_type**   |Yes        |the type of content referenced by this entry       |
+---------------------+-----------+---------------------------------------------------+
|**title**            |Yes        |the title of the content referenced by this entry  |
+---------------------+-----------+---------------------------------------------------+
|**abstract**         |No         |short description or summary of the content        |
|                     |           | referenced by this entry                          |
+---------------------+-----------+---------------------------------------------------+
|**publisher**        |?          |name of the publishing company                     |
+---------------------+-----------+---------------------------------------------------+
|**publication_year** |?          |year in which the content was published            |
+---------------------+-----------+---------------------------------------------------+
|**publication_month**|?          |month in which the content was published           |
+---------------------+-----------+---------------------------------------------------+
|**publication_url**  |?          |fully-qualified url pointing to an online version  |
|                     |           | of the content                                    |
+---------------------+-----------+---------------------------------------------------+
|**authors**          |Yes        |list of dictionaries, one for each author of the   |
|                     |           | content.  The dictionaries will contain three     |
|                     |           | items: 'firstname' (given name), 'lastname'       |
|                     |           | (surname, family name), middlename (any name or   |
|                     |           | names in-between the first and last names)        |
+---------------------+-----------+---------------------------------------------------+
|**journal**          |No         |Title of the journal in which the content appears  |
+---------------------+-----------+---------------------------------------------------+
|**volume**           |No         |Volume of the periodical in which the content      |
|                     |           | appears                                           |
+---------------------+-----------+---------------------------------------------------+
|**number**           |No         |Number of the periodical in which the content      |
|                     |           | appears                                           |
+---------------------+-----------+---------------------------------------------------+
|**pages**            |No         |Page numbers within the given volume:number of the |
|                     |           | periodical in which the content appears           |
+---------------------+-----------+---------------------------------------------------+

Requirements
------------
* requires Bibutils 4.6 or higher

Configuration
-------------
``bibliograph.parsing`` honors the environment variable ``FIX_BIBTEX``. If set, the module
will clean up BibTeX import data through the "bib2xml | xml2bib" pipeline in order cleanup
up improper or misformatted BixTeX data. However you may lose some data (e.g. the ``anotate``
field will be filtered out through Bibutils).                                                                                       


                                                                                       
Sources
-------

Formats for input files have been gleaned from a number of sources:  
RIS: http://www.refman.com/support/risformat_intro.asp

Contributors
-------------

- Paul Bugni, pbugni@u.washington.edu, author
- Cris Ewing, cewing@u.washington.edu, author
- Raphael Ritz, r.ritz@biologie.hu-berlin.de, parsers
- Andreas Jung, info@zopyx.com, bug fixes
   
