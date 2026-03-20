# Auditing Google's AI Overviews and Featured Snippets: A Case Study on Baby Care and Pregnancy

This repository contains the code and data accompanying the paper:

> **Auditing Google's AI Overviews and Featured Snippets: A Case Study on Baby Care and Pregnancy**
> Desheng Hu, Joachim Baumann, Aleksandra Urman, Elsa Lichtenegger, Robin Forsberg, Aniko Hannak, Christo Wilson

---

## Overview

Google Search increasingly surfaces AI-generated content through **AI Overviews (AIO)** and **Featured Snippets (FS)**, which users frequently rely on despite having no control over their presentation. Through a systematic algorithm audit of **1,508 real baby care and pregnancy-related queries**, we evaluate the quality and consistency of these information displays across multiple dimensions:

- **Consistency** between AIO and FS answers co-appearing on the same search result page
- **Relevance** of answers to the query
- **Medical safeguards** (disclaimers, warnings, guidance cues)
- **Source credibility** by domain category
- **Sentiment alignment** between query and response (confirmation bias test)

Key findings:
- AIO and FS answers are **inconsistent with each other in 33% of co-appearing cases** (41% for highlighted content)
- Medical safeguards are critically absent: present in only **11% of AIO** and **7% of FS** responses
- FS disproportionately links to **commercial sources** compared to AIO
- No evidence of confirmation bias in AIO responses

---

## Repository Structure

```
.
├── code/
│   ├── crawler/
│   │   ├── main.py                  # Crawls Google SERPs and saves raw HTML
│   │   └── websurfer/
│   │       └── websurfer.py         # Selenium-based browser automation
│   └── parser/
│       └── parser_for_AI_overview_and_featured_snippet.py  # Parses AIO and FS from saved HTML
└── data/
    ├── full_qry_to_be_crawled.csv
    ├── AIO_FS_Answers_with_relevance_labels.csv
    ├── AIO_FS_Answers_with_safeguard_labels.csv
    ├── AIO_answers_with_sentiment_labels.csv
    ├── questions_and_coappearing_AIO_FS_answers_with_consistency_labels.csv
    └── urls_and_domains_of_ten_blue_link_and_AIO_FS_answers.csv
```

---

## Data

| File | Description |
|------|-------------|
| `full_qry_to_be_crawled.csv` | Query list with topic, question type, and index |
| `AIO_FS_Answers_with_relevance_labels.csv` | Relevance ratings (High/Medium/Low) for AIO and FS answers |
| `AIO_FS_Answers_with_safeguard_labels.csv` | Medical safeguard presence labels |
| `AIO_answers_with_sentiment_labels.csv` | Sentiment labels for AIO responses (confirmation bias analysis) |
| `questions_and_coappearing_AIO_FS_answers_with_consistency_labels.csv` | Consistency labels for co-occurring AIO+FS pairs |
| `urls_and_domains_of_ten_blue_link_and_AIO_FS_answers.csv` | Source domains for AIO, FS, and organic blue links with FortiGuard category labels |

Queries were sourced from the [ORCAS dataset](https://microsoft.github.io/ORCAS/) (10.4M Bing queries), filtered to baby care and pregnancy topics, and validated using GPT-4o-mini. Crawls were conducted in September 2024 from five US cities (New York City, Kansas City, San Francisco, Houston, Madison).

---

## Code

### Crawler (`code/crawler/`)

Uses Selenium with Chrome to crawl Google Search result pages (SERPs) and save the rendered HTML. Supports geolocation spoofing to simulate searches from different US cities. Reads queries from `full_qry_to_be_crawled.csv`.

**Requirements:**
- Python 3.x
- `selenium`
- Chrome + ChromeDriver (matching versions)

### Parser (`code/parser/`)

Parses the saved HTML files to extract:
- AIO text (visible and hidden portions), highlighted text, source links and domains
- Featured snippet text, highlighted text, source links and domains, and layout type

The parser handles multiple HTML layout variants used by Google across the crawl period.

**Requirements:**
- Python 3.x
- `beautifulsoup4`
- `pandas`
- `selenium` (used to fully render saved HTML files before parsing)

---

## Citation

If you use this code or data, please cite our paper:

```bibtex
@article{hu2025auditing,
  title={Auditing Google's AI Overviews and Featured Snippets: A Case Study on Baby Care and Pregnancy},
  author={Hu, Desheng and Baumann, Joachim and Urman, Aleksandra and Lichtenegger, Elsa and Forsberg, Robin and Hannak, Aniko and Wilson, Christo},
  journal={arXiv preprint arXiv:2511.12920},
  year={2025}
}
```

---

## License

This repository is released for research purposes. Please refer to the paper for details on data collection methodology and any applicable terms from third-party data sources (ORCAS dataset, Google Search).
