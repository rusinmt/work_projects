The 'format_title' function, developed for bank transfer automation, formats transaction titles by splitting them into user-defined parts,<br> by 'part_length'. The divided chunks are separated by a chosen character, like, for instance, '|', ensuring compliance with banking system requirements while maintaining readability and proper data processing in automated payment workflows.

```sql
CREATE OR REPLACE FUNCTION format_title(
    input_text text,
    part_length integer,
    separator_sign text
)
RETURNS text AS $$
DECLARE
    result text;
    remaining text;
    chunk text;
BEGIN
    -- Input validation
    IF part_length <= 0 THEN
        RAISE EXCEPTION 'part_length must be > 0';
    END IF;

    IF separator_sign IS NULL THEN
        RAISE EXCEPTION 'separator_sign cannot be null';
    END IF;

    result := '';
    remaining := input_text;

    WHILE length(remaining) > part_length LOOP
        chunk := substring(remaining from 1 for part_length);

        IF result = '' THEN
            result := chunk;
        ELSE
            result := result || separator_sign || chunk;
        END IF;

        remaining := substring(remaining from part_length + 1);
    END LOOP;

    IF length(remaining) > 0 THEN
        IF result = '' THEN
            result := remaining;
        ELSE
            result := result || separator_sign || remaining;
        END IF;
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```
