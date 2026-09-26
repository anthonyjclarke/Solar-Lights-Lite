> Reviewed project copy: S9013 classification corrected to NPN. Quantities retain the original assumptions; verify physical parts. See ../BOARD_AND_PARTS.md for evidence.

# Transistor Inventory

3 kits, 25 unique parts, 2,280 pcs. All are TO-92.

---

## Kits

| Kit | Label (abbr.)         | Vals | Pcs |
|-----|-----------------------|------|-----|
| A   | TO-92 NPN Assortment  | 24   | 840 |
| B   | 2N2222–S9018          | 15   | 600 |
| C   | 2N2222–558            | 24   | 840 |

---

## Consolidated

| Part   | Type | A* | B  | C  | Tot |
|--------|------|----|----|----|-----|
| 2N2222 | NPN  | 35 | 40 | 35 | 110 |
| 2N3904 | NPN  | 35 | 40 | 35 | 110 |
| 2N3906 | PNP  | 35 | 40 | 35 | 110 |
| 2N5401 | PNP  | 35 | 40 | 35 | 110 |
| 2N5551 | NPN  | 35 | 40 | 35 | 110 |
| A1015  | PNP  | 35 | 40 | 35 | 110 |
| C1815  | NPN  | 35 | 40 | 35 | 110 |
| C945   | NPN  | 35 | 40 | 35 | 110 |
| S8050  | NPN  | 35 | 40 | 35 | 110 |
| S8550  | PNP  | 35 | 40 | 35 | 110 |
| S9012  | PNP  | 35 | 40 | 35 | 110 |
| S9013  | NPN  | 35 | 40 | 35 | 110 |
| S9014  | NPN  | 35 | 40 | 35 | 110 |
| S9015  | PNP  | 35 | 40 | 35 | 110 |
| S9018  | NPN  | –  | 40 | –  | 40  |
| BC327  | PNP  | 35 | –  | 35 | 70  |
| BC337  | NPN  | 35 | –  | 35 | 70  |
| BC517  | NPN  | 35 | –  | 35 | 70  |
| BC547  | NPN  | 35 | –  | 35 | 70  |
| BC548  | NPN  | 35 | –  | 35 | 70  |
| BC549  | NPN  | 35 | –  | 35 | 70  |
| BC550  | NPN  | 35 | –  | 35 | 70  |
| BC556  | PNP  | 35 | –  | 35 | 70  |
| BC557  | PNP  | 35 | –  | 35 | 70  |
| BC558  | PNP  | 35 | –  | 35 | 70  |

\* Kit A's label gives no per-value counts. I assumed 35 each (840 ÷ 24), matching kit C.

---

## Summary

| Type | Parts | Pcs   |
|------|-------|-------|
| NPN  | 15    | 1,340 |
| PNP  | 10    | 940   |

---

## Notes

- Kit A's title says "NPN", but its 24 values are the same mix as kit C, which includes 10 PNP types after correcting S9013. The original polarity column came from labels B and C; this copy corrects S9013 using manufacturer documentation.
- If A and C are two labels on the same box rather than two kits, halve the A and C columns. The total would be 1,440 pcs.
- Pinouts vary between families (e.g. `BC547` vs `2N3904` vs `C945`), so check each datasheet before wiring.
