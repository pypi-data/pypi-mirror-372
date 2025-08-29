## Embedding Selector Framework


#### - This framework helps you automatically select the most suitable text embedding model for a given downstream use case.

#### - It analyzes task requirements (e.g., retrieval, classification, summarization), matches them against available embedding models, and evaluates performance on relevant benchmarks.
---

##  Features


- **Use Case–Driven Selection:** Takes a natural-language description of a use case and extracts structured metadata (e.g., languages, token limits, complexity).
- **Metadata Extraction:** Uses advanced LLM models to normalize requirements into a standardized schema (parameters, memory, licensing, etc.).
- **Model Matching:** Filters embedding models based on attributes like size, efficiency, license, and language coverage.
- **Task Alignment:** Selects relevant evaluation tasks from MTEB (Massive Text Embedding Benchmark).
- **Performance Evaluation:** Loads benchmark results and computes average scores per candidate model.
---

##  How It Works

The pipeline runs in sequential steps:

- **Use Case Selection**
Choose from predefined scenarios (chatbots, legal retrieval, recommendations, sentiment analysis, summarization, etc.) or provide your own description.
- **Requirement Extraction (LLM Agent)**
GPT-4o parses the description into structured metadata, including:
Supported languages
Max token length
Memory usage & parameter limits
Task/domain classification
- **Model Filtering**
Candidate models from MTEB are filtered according to the extracted attributes.
- **Task Evaluation**
Candidate models are benchmarked on the most relevant MTEB tasks (retrieval, classification, summarization, etc.).
- **Ranking & Export**
Models are ranked by performance (with ties broken by efficiency) and exported to CSV for inspection.
## Usage 


To use the tool, follow these steps:

 ```bash
   pip install EmbedSelection

   EmbedSelection 



```

  
   
## Contributing

Contributions to improve the tool are welcome! Feel free to open issues for bugs or feature requests, or submit pull requests for enhancements.



## Acknowledgements

This project utilizes MTEB benchmark from huggingface : https://huggingface.co/spaces/mteb/leaderboard


