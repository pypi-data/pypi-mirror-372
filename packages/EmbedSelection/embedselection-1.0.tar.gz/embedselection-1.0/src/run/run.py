import warnings
warnings.filterwarnings('ignore')
import argparse

from openai import AzureOpenAI
import pandas as pd
import mteb
import json
from dotenv import load_dotenv, find_dotenv
import os
import sys

def main():


    envfilepath = str(input("\nEnter the path to your env file ")) or ".env"


    _ = load_dotenv(envfilepath)


    # Environment variables
    openai_api_key = os.getenv("API_KEY")
    openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_openai_endpoint = os.getenv("AZURE_ENDPOINT")
    embedding_deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")

    gpt_4_model_deployment_name = 'gpt-4o'

    gpt4o_client = AzureOpenAI(
        api_version=openai_api_version,
        azure_endpoint=azure_openai_endpoint,
        api_key=openai_api_key,
    )
    def gpt40_oneshot(prompt_sys, prompt_usr, temperature=0):
        prompt_sys = prompt_sys.replace("\n", " ")
        prompt_usr = prompt_usr.replace("\n", " ")
        

        response = gpt4o_client.chat.completions.create(
                temperature = 0.0,
                messages=[
                {"role": "system", "content": prompt_sys},
                {"role": "user", "content": prompt_usr},
                ],
                model=gpt_4_model_deployment_name,

            )
            
        return response.choices[0].message.content

    use_cases = [
        'An e-commerce company wants to deploy an intelligent chatbot to handle customer inquiries and support requests. By using text embeddings, the chatbot can understand and respond to customer queries more accurately, improving the overall customer service experience. Languages needed: English, French.',
        'A legal firm needs an efficient document search and retrieval system to quickly find relevant case documents and legal precedents. Using text embeddings, they can convert documents into vectors and implement a semantic search engine that retrieves documents based on the meaning of the query rather than keyword matching. Languages needed: German, English',
        'A streaming service wants to enhance its recommendation system by using text embeddings to analyze user preferences based on their watch history and reviews. By embedding textual data from movie descriptions, reviews, and user interactions, they can provide more accurate and personalized content recommendations. Languages needed: Chinese, English',
        'A retail company wants to analyze customer feedback from various sources like social media, product reviews, and surveys to understand the overall sentiment towards their products and services. By using text embeddings, they can convert customer feedback into numerical vectors and apply machine learning algorithms to classify sentiments as positive, negative, or neutral. Languages needed: Spanish, EnglishWe need to power a product search and recommendation system over a catalog of 1 million items. Queries come from users typing short English phrases (up to 32 tokens), and documents consist of title and description (up to 128 tokens).'  
        'We ingest full-length news articles (up to 2 000 tokens) across News, Government, and Legal domains. The system should perform Summarization to generate 3 to 5 sentence abstracts and Classification into predefined topics. Supported languages include English (eng), French (fra), and Arabic (ara). It must operate in real time (under 1 s per article) on CPU-only servers and rely on open-source models with Apache2.0 licensing.',
    ]

    print("\nAvailable Use Cases:")
    for i, uc in enumerate(use_cases):
        print(f"[{i}] {uc}")  # show first 120 chars for readability

    usecase = str(input("\nEnter the use case description, please choose from above or enter a new one "))
    use_casesi = usecase
    print(f"\n Selected use case:\n{use_casesi}\n")

    extraction_prompt = '''
    You are an expert metadata‐extraction and classification agent. Given a free‐form description of a text‐embedding model or downstream use case, extract and return exactly the following JSON. If a value cannot be determined, use `null` for strings/numbers/arrays or `false` for booleans. Return only this JSON, no explanations:

    {
    "attributes": {
        "n_parameters": <int|null>,
        "memory_usage_mb": <int|null>,
        "max_tokens": <int|null>,
        "embed_dim": <int|null>,
        "license": <string|null>,
        "open_weights": <boolean>,
        "languages": <[string]|null>,
        "complexity_estimation": <string>
    },
    "tasks": {
        "types": <[string]>,
        "domains": <[string]>,
        "estimated_max_tokens": <int>,
        "required_languages": <[string]|null>   
    }
    }

    1. attributes

    n_parameters: total parameters (e.g., 7000000) or null.

    memory_usage_mb: RAM of CPU or GPU in MB (e.g., 512) or null.

    max_tokens: max sequence length (e.g., 1024) or null.

    embed_dim: embedding dimension (e.g., 768) or null.

    license: SPDX license (e.g., "MIT") or null. Must select among ['apache-2.0', None, 'mit', 'https://ai.google.dev/gemma/terms',
        'cc-by-nc-4.0', 'gpl-3.0', 'not specified',
        'https://aws.amazon.com/service-terms/',
        'https://huggingface.co/Qodo/Qodo-Embed-1-1.5B/blob/main/LICENSE',
        'cc-by-sa-4.0']

    open_weights: true if weights are open source/public, else false.

    languages: array of supported ISO-639-3 codes (e.g., ["eng","fra"]) or null.

    complexity_estimation — categorize the overall task difficulty based on required domain expertise, data complexity, and system integration needs; choose "Low", "Medium", or "High".


    2. tasks.types — choose only one EXACT entries from:

    ["Retrieval","VisualSTS(eng)","VisualSTS(multi)","Classification","Reranking","VisionCentricQA",
    "Any2AnyRetrieval","DocumentUnderstanding","Any2AnyMultilingualRetrieval","ImageClassification",
    "ImageClustering","Compositionality","ZeroShotClassification","BitextMining","Clustering",
    "InstructionRetrieval","MultilabelClassification","PairClassification","Speed","STS","Summarization"]

    3. tasks.domains — choose one or more EXACT entries from:

    ["Fiction","Constructed","Spoken","Medical","Government","Chemistry","News","Legal","Social",
    "Academic","Encyclopaedic","Engineering","Blog","Reviews","Written","Entertainment","Web","Scene",
    "Subtitles","Non-fiction","Religious","Programming","Financial"]

    4. tasks.estimated_max_tokens — your best integer estimate of the maximum token length for this use case.

    5. tasks.required_languages — array of ISO-639-3 codes mentioned or null.


    Normalization rules:

    Convert “7 M” → 7000000, “128 MB” → 128.

    Strip script tags from codes (“eng-Latn” → "eng").

    Do not include any additional text.
    '''

    def match_count(required, lang_list):
        res = []
        for langi in lang_list:
            codes = {lang.split("-")[0].lower() for lang in langi}
            res.append(len(required & codes))
        return res


    def filter_models(df: pd.DataFrame, req: dict) -> pd.DataFrame:
        df_filtered = df.dropna().copy()
        complexity_defaults = {
            "Low":    [0, 1.0e8],
            "Medium": [1.0e8, 8.0e8],
            "High":  [1.0e8, float("inf")],
        }   
        # Exact match filters   
        if req["license"] is not None:
            df_filtered = df_filtered[df_filtered["license"] == req["license"]]
        if req["open_weights"] is not None:
            df_filtered = df_filtered[df_filtered["open_weights"] == True]
        
        # Language support: full or best partial match
        if req["languages"] is not None:
            required = set(code.lower() for code in req["languages"])
            if len(required) > 0: 
                df_filtered["lang_match_count"] = match_count(required, df_filtered["languages"].values)
            
            # otherwise best partial
            df_filtered = df_filtered[df_filtered["lang_match_count"] == df_filtered["lang_match_count"].max()]
            df_filtered =  df_filtered.drop(columns="lang_match_count")
        
        
        # Numeric threshold filters
        if req["memory_usage_mb"] is not None:
            df_filtered1 = df_filtered[df_filtered["memory_usage_mb"] <= req["memory_usage_mb"]]
            if df_filtered.shape[0] == 0:
                return df_filtered
        else:
            df_filtered1 = df_filtered

        if req["max_tokens"] is not None:
            df_filtered2 = df_filtered1[df_filtered1["max_tokens"] >= req["max_tokens"]]
            if df_filtered2.shape[0] == 0:
                return df_filtered1
        else:
            df_filtered2 = df_filtered1
            
        if req["embed_dim"] is not None:
            df_filtered3 = df_filtered2[df_filtered2["embed_dim"] <= req["embed_dim"]] 
            if df_filtered3.shape[0] == 0:
                return df_filtered2
        else:
            df_filtered3 = df_filtered2
            
        if req["n_parameters"] is not None:
            df_filtered4 = df_filtered3[df_filtered3["n_parameters"] <= req["n_parameters"]]
            if df_filtered4.shape[0] == 0:
                return df_filtered3    
        else: 
            bounds = complexity_defaults[req["complexity_estimation"]]
            #print(bounds)
            df_filtered4 = df_filtered3[(df_filtered3["n_parameters"] <= bounds[1])&(df_filtered3["n_parameters"] >= bounds[0]) ]
            if df_filtered4.shape[0] == 0:
                return df_filtered3
        return df_filtered4
    role = 'You are an expert metadata‐extraction and classification agent.'
    task = extraction_prompt + 'Here is the use case description: ' + use_casesi
    paramsi = gpt40_oneshot(role, task , temperature=0.)
    paramsi = json.loads(paramsi)
    print(paramsi['attributes'])
    print(paramsi['tasks'])

    model_metas = mteb.get_model_metas()
    
    df = pd.DataFrame()
    names = []
    n_parameters = []
    memory_usage_mb = []
    max_tokens = []
    embed_dim = []
    release_date = []
    license = []
    open_weights = []
    reference = []
    languages = []
    use_instructions = []
    for i in range(len(model_metas)):
        names.append(model_metas[i].name)
        n_parameters.append(model_metas[i].n_parameters)
        memory_usage_mb.append(model_metas[i].memory_usage_mb)
        max_tokens.append(model_metas[i].max_tokens)
        embed_dim.append(model_metas[i].embed_dim)
        release_date.append(model_metas[i].release_date)
        license.append(model_metas[i].license)
        open_weights.append(model_metas[i].open_weights)
        reference.append(model_metas[i].reference)
        languages.append(model_metas[i].languages)
        use_instructions.append(model_metas[i].use_instructions)
    
    df['names'] = names
    df['n_parameters'] = n_parameters
    df['memory_usage_mb'] = memory_usage_mb
    df['max_tokens'] = max_tokens
    
    df['embed_dim'] = embed_dim
    df['release_date'] = release_date
    df['license'] = license
    df['open_weights'] = open_weights
    
    df['reference'] = reference
    df['languages'] = languages
    df['use_instructions'] = use_instructions

    tasks = mteb.get_tasks(task_types=paramsi['tasks']['types'], languages=paramsi['tasks']['required_languages'], domains=paramsi['tasks']['domains'])


    result = filter_models(df, paramsi['attributes'])


    model_names = result['names'].values

    final_results = mteb.load_results(models=model_names, tasks=tasks)
    final_results = final_results.to_dataframe()

        
    mean_perfs = final_results[final_results.columns[1:]].mean().values
    perfs_dict = {}
    for i in range(len(mean_perfs)):
        perfs_dict[final_results.columns[i+1]] = mean_perfs[i]
    miss_model = list(set(result['names']) - set(final_results.columns) )
    if len(miss_model) > 0:
        for i in range(len(miss_model)):
            perfs_dict[miss_model[i]] = None
    result['performance'] = result['names'].map(perfs_dict)
    pathresult = str(input("\n Enter output path "))
    result[['names', 'performance', 'n_parameters', 'memory_usage_mb', 'max_tokens', 'embed_dim',
            'license', 'open_weights','languages','reference','release_date' ]].sort_values(by=['performance','n_parameters' ], ascending = [False, True]).to_csv(pathresult +'BenchmarkResults' +'.csv')


if __name__ == "__main__":
    main()


