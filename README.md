# thegn_extraction
This project is made for extracting various spellings of the word "thegn" in historic sources.


# How to run

```
python fetch_links.py
```

# How it works

1. Generate all possible word forms including all possible spellings, morphological cases, and imaginable compounds.
2. Create URLs to queries for `http://clarino.uib.no/menota`.
3. Use Scrapy to fetch the results and the title of the context.

# Authors

- Denis Sukino-Khomenko 
- Mehdi Ghanimifard 
