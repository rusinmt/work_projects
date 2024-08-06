## E-mail template

As part of our team's collaborative effort to create an automated template for a client, I have combined PostgreSQL with HTML to generate an elegant and slick table that can be added to mass letter campaigns.

```sql
SELECT
    '<table style="font-family: ''Segoe UI'', Arial, sans-serif; border-collapse: separate; border-spacing: 0; margin: 20px auto; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">' ||
    '<thead>' ||
    '<tr>' ||
    '<th style="background-color: #3a6ea5; color: #ffffff; text-align: left; padding: 18px 20px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap;">Number</th>' ||
    '<th style="background-color: #3a6ea5; color: #ffffff; text-align: right; padding: 18px 20px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap;">Amount</th>' ||
    '</tr>' ||
    '</thead>' ||
    '<tbody>' ||
    string_agg(
        '<tr style="background-color: ' || CASE WHEN number % 2 = 0 THEN '#f8f9fa' ELSE '#ffffff' END || ';">' ||
        '<td style="padding: 16px 20px; border-bottom: 1px solid #e9ecef; white-space: nowrap;">' || number || '</td>' ||
        '<td style="padding: 16px 20px; border-bottom: 1px solid #e9ecef; text-align: right; white-space: nowrap;">' || to_char(amount, 'FM$999,999,999.00') || '</td>' ||
        '</tr>',
        ''
    ) ||
    '</tbody>' ||
    '</table>'
FROM base
```
<p align="center">
    <img src=D:\portfolio\date\git\table.jpg>
</p>
