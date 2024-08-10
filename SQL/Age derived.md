## Age from Universal Electronic Population Register System

As part of an analysis, I have developed a PostgreSQL CTE to derive a person’s age from their Universal Electronic Population Register System (PESEL) number in the database.

```sql
SELECT
        CASE
            WHEN
                substring(, 3, 2) ~ '^\d{2}$' AND
                substring(number, 5, 2) ~ '^\d{2}$' AND
                (substring(number, 3, 2)::int BETWEEN 1 AND 12 OR substring(number, 3, 2)::int BETWEEN 21 AND 42) AND
                substring(number, 5, 2)::int BETWEEN 1 AND 31
            THEN
                case
                    when to_char(substring(number, 3, 2)::int, '00') < '20'
                        then
                            btrim(to_char((19 || left(number, 6))::int, '0000-00-00'))
                        else btrim(to_char((20 || left(number, 2))::int, '0000'))
                        ||'-'||
                        case
                            when to_char(substring(number, 3, 2)::int, '00') > '20' and to_char(substring(number, 3, 2)::int, '00') <= '42'
                                then btrim(to_char((substring(number, 3, 2)::int - 20)::int, '00'))
                            else null
                        end
                        ||'-'||
                        btrim(to_char(substring(number, 5, 2)::int, '00'))
                end
            ELSE NULL
        END AS age
FROM table
```
The CTE is suitable for individuals born both before and after the year 2000, as it correctly handles the different date encoding schemes used for each century in the PESEL system.
