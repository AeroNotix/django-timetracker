ALTER TABLE tbluser modify uPassword varchar(128);
ALTER TABLE tbluser ADD COLUMN salt varchar(128);
