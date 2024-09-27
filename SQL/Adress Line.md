## Solution for Street names

This query helps to unify street naming for the established naming convention used in Poland. In cases where a household in a city doesn't have a street name, it's named by the village name and house number if it's an individual residence. Therefore, the query goes through various cases to handle different address formats:

For addresses without an apartment number:
- If there's no street name, it uses the city name and house number.
- If there is a street name, it uses the street name and house number.

For addresses with an apartment number:
- If there's no street name, it combines the city name, house number, and apartment number.
- If there is a street name, it uses the street name, house number, and apartment number.

This approach ensures a consistent and standardized format for addresses, accommodating the unique naming conventions found in some Polish cities and villages. The query capitalizes the first letter of each word in city and street names, further standardizing the output. 

This effort helped to translate the hosts' database schema into conventions used in Poland to meet regional requirements.
```sql
SELECT
    id AS id,
    name AS name,
    CASE
        WHEN LENGTH(apart_nr) < 1 THEN
            CASE
                WHEN LENGTH(street= < 1 THEN CONCAT(INITCAP(city),' ', house_nr)
                ELSE CONCAT(INITCAP(street_name),' ', house_nr)
            END
        WHEN LENGTH(a.tanav) < 1 THEN CONCAT(INITCAP(a.city),' ',house_nr,'/',apart_nr)
        ELSE CONCAT(INITCAP(street_name),' ',house_nr,'/',apart_nr)
    END AS street,
    INITCAP(city) AS city,
    postal_code AS postal_code,
    voivodeship AS voivodeship
FROM table
```
