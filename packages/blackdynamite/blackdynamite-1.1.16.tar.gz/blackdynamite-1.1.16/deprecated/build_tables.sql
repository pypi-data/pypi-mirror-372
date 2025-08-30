
-- quantities
CREATE TABLE SCHEMAS_IDENTIFIER.quantities (
       id SERIAL PRIMARY KEY, --id, standard 
       name TEXT NOT NULL, -- human readable name idendifying the quantity
       is_integer BOOLEAN NOT NULL, --whether the quantity is an integer quantity
       is_vector BOOLEAN NOT NULL, --whether the quantity is vectorial or scalar
       description TEXT , --general description the quantity (like units)
       UNIQUE (name));

-- integer scalar values
CREATE TABLE SCHEMAS_IDENTIFIER.scalar_integer (
       id SERIAL PRIMARY KEY, --id, standard
       run_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.runs
       quantity_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.quantities
       measurement INTEGER NOT NULL, -- measured value
       step INTEGER NOT NULL, --step at which this measurement has been taken
       computed_at TIMESTAMP NOT NULL, --time when the measurement has been added to the database. this column might be dropped later on
       FOREIGN KEY (run_id) REFERENCES SCHEMAS_IDENTIFIER.runs ON DELETE CASCADE,
       FOREIGN KEY (quantity_id) REFERENCES SCHEMAS_IDENTIFIER.quantities ON DELETE CASCADE);

CREATE INDEX scalar_integer_run_id on SCHEMAS_IDENTIFIER.scalar_integer (run_id,quantity_id,step);

-- real scalar values
CREATE TABLE SCHEMAS_IDENTIFIER.scalar_real (
       id SERIAL PRIMARY KEY, --id, standard
       run_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.runs
       quantity_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.quantities
       measurement DOUBLE PRECISION NOT NULL, -- measured value
       step INTEGER NOT NULL, --step at which this measurement has been taken
       computed_at TIMESTAMP NOT NULL, --time when the measurement has been added to the database. this column might be dropped later on
       FOREIGN KEY (run_id) REFERENCES SCHEMAS_IDENTIFIER.runs ON DELETE CASCADE,
       FOREIGN KEY (quantity_id) REFERENCES SCHEMAS_IDENTIFIER.quantities ON DELETE CASCADE);

CREATE INDEX scalar_real_run_id on SCHEMAS_IDENTIFIER.scalar_real (run_id,quantity_id,step);

-- real vector values
CREATE TABLE SCHEMAS_IDENTIFIER.vector_real (
       id SERIAL PRIMARY KEY, --id, standard
       run_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.runs
       quantity_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.quantities
       measurement DOUBLE PRECISION[] NOT NULL, -- measured value
       step INTEGER NOT NULL, --step at which this measurement has been taken
       computed_at TIMESTAMP NOT NULL, --time when the measurement has been added to the database. this column might be dropped later on
       FOREIGN KEY (run_id) REFERENCES SCHEMAS_IDENTIFIER.runs ON DELETE CASCADE,
       FOREIGN KEY (quantity_id) REFERENCES SCHEMAS_IDENTIFIER.quantities ON DELETE CASCADE);

CREATE INDEX vector_real_run_id on SCHEMAS_IDENTIFIER.vector_real (run_id,quantity_id,step);

-- int vector values
CREATE TABLE SCHEMAS_IDENTIFIER.vector_integer (
       id SERIAL PRIMARY KEY, --id, standard
       run_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.runs
       quantity_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.quantities
       measurement INTEGER [] NOT NULL, -- measured value
       step INTEGER NOT NULL, --step at which this measurement has been taken
       computed_at TIMESTAMP NOT NULL, --time when the measurement has been added to the database. this column might be dropped later on
       FOREIGN KEY (run_id) REFERENCES SCHEMAS_IDENTIFIER.runs ON DELETE CASCADE,
       FOREIGN KEY (quantity_id) REFERENCES SCHEMAS_IDENTIFIER.quantities ON DELETE CASCADE);

CREATE INDEX vector_integer_run_id on SCHEMAS_IDENTIFIER.vector_integer (run_id,quantity_id,step);

-- configuration files
CREATE TABLE SCHEMAS_IDENTIFIER.configfiles (
       id SERIAL PRIMARY KEY, --id, standard 
       filename TEXT NOT NULL, -- name of the config file
       file TEXT NOT NULL -- content of the config file
       );

CREATE UNIQUE INDEX configfiles_md5file_key ON SCHEMAS_IDENTIFIER.configfiles ((md5(file)));
--ALTER TABLE SCHEMAS_IDENTIFIER.configfiles ADD UNIQUE (SCHEMAS_IDENTIFIER.configfiles_md5file_key);

-- configuration files
CREATE TABLE SCHEMAS_IDENTIFIER.runconfig (
       id SERIAL PRIMARY KEY, --id, standard 
       run_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.runs
       configfile_id INTEGER NOT NULL, --referencing SCHEMAS_IDENTIFIER.configfiles
       FOREIGN KEY (run_id) REFERENCES SCHEMAS_IDENTIFIER.runs ON DELETE CASCADE,
       FOREIGN KEY (configfile_id) REFERENCES SCHEMAS_IDENTIFIER.configfiles);

-- create functions for the different triggers

--create run_inserter
CREATE FUNCTION SCHEMAS_IDENTIFIER.run_inserter()
       RETURNS TRIGGER AS $run_inserter$
       BEGIN
        NEW.state := 'CREATED';
--        NEW.run_name := 'run' || NEW.id || ':' || NEW.run_name; 
        RETURN NEW;
       END;
       $run_inserter$ LANGUAGE PLPGSQL VOLATILE;

CREATE TRIGGER run_inserter BEFORE INSERT ON SCHEMAS_IDENTIFIER.runs FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.run_inserter();

--create measurement inserter
CREATE FUNCTION SCHEMAS_IDENTIFIER.measurement_inserter()
       RETURNS TRIGGER AS $measurement_inserter$
       BEGIN
        NEW.computed_at := CURRENT_TIMESTAMP;
        RETURN NEW;
       END;
       $measurement_inserter$ LANGUAGE PLPGSQL VOLATILE;

--create set start time trigger
CREATE FUNCTION SCHEMAS_IDENTIFIER.set_start_time()
       RETURNS TRIGGER AS $set_start_time$
       BEGIN
	IF NEW.state = 'START' THEN NEW.start_time := CURRENT_TIMESTAMP; END IF;
        RETURN NEW;
       END;
       $set_start_time$ LANGUAGE PLPGSQL VOLATILE;

--automagic clean of config files
CREATE FUNCTION SCHEMAS_IDENTIFIER.delete_file()
       RETURNS TRIGGER AS $delete_file$
       BEGIN
        DELETE FROM SCHEMAS_IDENTIFIER.configfiles;
	RETURN NEW;
        EXCEPTION WHEN FOREIGN_KEY_VIOLATION THEN NULL;
	RETURN NEW;
       END;
       $delete_file$ LANGUAGE PLPGSQL;

CREATE TRIGGER int_scal_insert BEFORE INSERT ON SCHEMAS_IDENTIFIER.scalar_integer FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.measurement_inserter();
CREATE TRIGGER int_vect_insert BEFORE INSERT ON SCHEMAS_IDENTIFIER.vector_integer FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.measurement_inserter();
CREATE TRIGGER real_scal_insert BEFORE INSERT ON SCHEMAS_IDENTIFIER.scalar_real FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.measurement_inserter();
CREATE TRIGGER real_vect_insert BEFORE INSERT ON SCHEMAS_IDENTIFIER.vector_real FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.measurement_inserter();
CREATE TRIGGER update_start_time BEFORE UPDATE ON SCHEMAS_IDENTIFIER.runs FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.set_start_time();
CREATE TRIGGER delete_conffile AFTER DELETE ON SCHEMAS_IDENTIFIER.runs FOR EACH ROW EXECUTE PROCEDURE SCHEMAS_IDENTIFIER.delete_file();

