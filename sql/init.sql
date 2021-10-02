CREATE EXTENSION unaccent;


-- Cria uma nova configuração para o FTS
CREATE TEXT SEARCH CONFIGURATION pt (COPY = pg_catalog.portuguese);
ALTER TEXT SEARCH CONFIGURATION pt
ALTER MAPPING
FOR hword, hword_part, word with unaccent, portuguese_stem;


-- Trigger para a remoção de acentos
-- CREATE TRIGGER question_search_vector_trigger
--     BEFORE INSERT OR UPDATE 
--     ON public.question
--     FOR EACH ROW
--     EXECUTE PROCEDURE tsvector_update_trigger('search_vector', 'public.pt', 'question', 'answer');

CREATE UNIQUE INDEX ix_question_answer ON public.question USING btree (md5(answer), id);