bibliograph.parsing Package Readme
=========================

Overview
--------

Parsers for bibliograph packages

Each parser accepts input from a given bibliographic reference format and outputs
a list of python dictionaries, one for each entry listed in the input source.  Each
of these dictionaries will contain some  number of the following fields:
    
    Field Name:         Required:   Description of Field Contents:
   |-------------------|-----------|---------------------------------------------------
   |'reference_type':  |Yes        |the type of content referenced by this entry
   |-------------------|-----------|---------------------------------------------------
   |'title'            |Yes        |the title of the content referenced by this entry
   |-------------------|-----------|---------------------------------------------------
   |'abstract'         |No         |short description or summary of the content 
   |                   |           | referenced by this entry
   |-------------------|-----------|---------------------------------------------------
   |'publisher'        |?          |name of the publishing company
   |-------------------|-----------|---------------------------------------------------
   |'publication_year' |?          |year in which the content was published
   |-------------------|-----------|---------------------------------------------------
   |'publication_month'|?          |month in which the content was published
   |-------------------|-----------|---------------------------------------------------
   |'publication_url'  |?          |fully-qualified url pointing to an online version
   |                   |           | of the content
   |-------------------|-----------|---------------------------------------------------
   |'authors'          |Yes        |list of dictionaries, one for each author of the
   |                   |           | content.  The dictionaries will contain three
   |                   |           | items: 'firstname' (given name), 'lastname'
   |                   |           | (surname, family name), middlename (any name or 
   |                   |           | names in-between the first and last names)
   |-------------------|-----------|---------------------------------------------------
   |'journal'          |No         |Title of the journal in which the content appears
   |-------------------|-----------|---------------------------------------------------
   |'volume'           |No         |Volume of the periodical in which the content 
   |                   |           | appears
   |-------------------|-----------|---------------------------------------------------
   |'number'           |No         |Number of the periodical in which the content 
   |                   |           | appears
   |-------------------|-----------|---------------------------------------------------
   |'pages'            |No         |Page numbers within the given volume:number of the
   |                   |           | periodical in which the content appears
   |-------------------|-----------|---------------------------------------------------

   
Sources
-------

Formats for input files have been gleaned from a number of sources:  
RIS: http://www.refman.com/support/risformat_intro.asp
   
