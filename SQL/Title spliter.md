The 'format_title' function developed for bank transfer automation formats transaction titles by splitting them into 35-character chunks separated by pipe characters '|', ensuring compliance with banking system requirements while maintaining readability and proper data processing in automated payment workflows.
```sql
CREATE OR REPLACE FUNCTION format_title(input_text text)
RETURNS text AS $$
DECLARE
    stripped_text text;
    result text;
    remaining text;
    chunk text;
BEGIN
    stripped_text := trim(both '"' from input_text);
    result := '';
    remaining := stripped_text;

    WHILE length(remaining) > 35 LOOP
        chunk := substring(remaining from 1 for 35);

        IF result = '' THEN
            result := chunk;
        ELSE
            result := result || '|' || chunk;
        END IF;

        remaining := substring(remaining from 36);
    END LOOP;

    IF length(remaining) > 0 THEN
        IF result = '' THEN
            result := remaining;
        ELSE
            result := result || '|' || remaining;
        END IF;
    END IF;

    RETURN '"' || result || '"';
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```
