# Deduplication estimate (not the formal EndNote deduplication)

Records before deduplication: 4906  |  estimated unique records: 2695  |  estimated duplicates: 2211

## Merges by tier (in the order applied)
- T1 DOI: 1293
- T2 title+author+year: 823
- T2b English title (cross-script): 3
- T3 similar title+author+year: 92
- identical-title pairs NOT merged (listed in dedup_estimate_ambiguous_pairs.csv): 2269
    - same title, different author: 2224
    - same title, author missing: 33
    - same title and author, year differs >1: 12
  (the large 'different author' count comes from generic titles such as 'Wandering spleen.' used by many different papers; only the 'author missing' and 'year differs' pairs need a manual look)
- cumulative unique records: after T1 only 3613; after T1+T2 2790; after all tiers 2695

## Per source
| source | records | distinct records within source | within-source duplicates | records also found in another source | found only in this source |
|---|---|---|---|---|---|
| PubMed | 1263 | 1263 | 0 | 1055 | 208 |
| WoS | 750 | 748 | 2 | 660 | 88 |
| Scopus | 1563 | 1554 | 9 | 1156 | 398 |
| CNKI | 486 | 479 | 7 | 256 | 223 |
| Wanfang | 423 | 412 | 11 | 287 | 125 |
| CBM | 421 | 418 | 3 | 267 | 151 |

## Unique records by number of sources that found them
- found by 1 source(s): 1193
- found by 2 source(s): 836
- found by 3 source(s): 656
- found by 4 source(s): 9
- found by 5 source(s): 1

- unique records found only by the three English-language sources: 1881
- unique records found only by the three Chinese-language sources: 800
- unique records found by both groups (cross-script matches): 14

## Pairwise overlap (unique records found by both sources)
| | PubMed | WoS | Scopus | CNKI | Wanfang | CBM |
|---|---|---|---|---|---|---|
| PubMed | 1263 | 527 | 1010 | 1 | 1 | 1 |
| WoS | 527 | 748 | 615 | 0 | 0 | 0 |
| Scopus | 1010 | 615 | 1554 | 13 | 12 | 13 |
| CNKI | 1 | 0 | 13 | 479 | 228 | 208 |
| Wanfang | 1 | 0 | 12 | 228 | 412 | 239 |
| CBM | 1 | 0 | 13 | 208 | 239 | 418 |

## Expected PRISMA numbers if EndNote agrees with this estimate
identified from six databases: 4906; duplicates removed: 2211; records to screen: 2695
