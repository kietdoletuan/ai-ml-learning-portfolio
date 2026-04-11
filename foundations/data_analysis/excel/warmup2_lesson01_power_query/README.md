## Factory Supplier Invoice Cleaner

**What it does:** Power Query ETL pipeline that cleans messy supplier invoice exports that fills null supplier names, standardises payment terms, calculates line totals, removes cancelled lines, and aggregates by supplier.
**Dataset:** Synthetic factory supplier invoice data, self-generated for project.

**Approach:** Power Query pipeline (Fill Down, Replace Values, Add Column, Filter Rows, Group By).

**Result:** Cleaned supplier invoices and a summary table with total invoice value and line count per supplier. 
