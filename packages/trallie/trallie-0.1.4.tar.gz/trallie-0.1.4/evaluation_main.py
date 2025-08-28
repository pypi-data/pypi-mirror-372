import os
import glob

from trallie.wrappers import openie, closedie

from pathlib import Path

# os.environ["GROQ_API_KEY"] = None
# os.environ["OPENAI_API_KEY"] = None 

os.environ["GROQ_API_KEY"] = "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"

base_path = Path("data/evaluation/data")
datasets = get_evaluation_params(base_path)

model_names = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b"]
model_providers = ["groq", "groq", "groq"]
reasoning_modes = [False, False, False, True]
    
for dataset_name, dataset_info in list(datasets.items()):
    print(dataset_name, dataset_info)
    for provider, model_name, reasoning_mode in zip(model_providers, model_names, reasoning_modes):
        dataset_info["schema"] = get_dataset_schema(dataset_info["ground_truth"])
        records = glob.glob(str(dataset_info["files"]))

        # Use the first 100 records for evaluation 
        sampled_records = records[:100]

        if not os.path.exists(f"results/{model_name}_{dataset_name}_openie_predicted_table.json"):
            extracted_jsons = openie(
                dataset_info['description'],
                sampled_records,
                provider=provider,
                model_name=model_name,
                reasoning_mode=reasoning_mode,
                dataset_name=dataset_name
            )
            print(extracted_jsons)

        result = evaluate_openie(
            dataset_info['ground_truth'],
            f"results/{model_name}_{dataset_name}_openie_predicted_table.json",
            use_exact_match=True
        )
        print(f"Results for OpenIE {model_name} : {result}")

        if not os.path.exists(f"results/{model_name}_{dataset_name}_closedie_predicted_table.json"):
            schema = get_dataset_schema(dataset_info['ground_truth'])
            extracted_jsons = closedie(
                sampled_records,
                schema,
                provider=provider,
                model_name=model_name,
                reasoning_mode=reasoning_mode,
                dataset_name=dataset_name
            )

        result = evaluate_closedie(
            dataset_info["ground_truth"],
            f"results/{model_name}_{dataset_name}_closedie_predicted_table.json",
            use_exact_match=True
        )
        print(f"Results for ClosedIE {model_name} : {result}")
