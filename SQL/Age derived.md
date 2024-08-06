## Age from Universal Electronic Population Register System

AS a part of analysis I have come up with a PostgreSQl code for deriving persons age from his Universal Electronic Population Register System number.

```sql
select
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
    from table
```
