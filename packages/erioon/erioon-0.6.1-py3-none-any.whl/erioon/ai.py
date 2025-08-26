# import json
# from erioon.read import handle_get_all
# import openai
# import anthropic

# # Import Vertex AI client libraries for Gemini
# from google.cloud import aiplatform
# from google.api_core.client_options import ClientOptions

# # Map model names to providers for dispatching
# MODEL_PROVIDER_MAP = {
#     # OpenAI models
#     "gpt-4o": "openai",
#     "gpt-4o-mini": "openai",
#     "gpt-3.5-turbo": "openai",
#     # Anthropic models
#     "claude-v1": "anthropic",
#     "claude-v1.3": "anthropic",
#     "claude-instant-v1": "anthropic",
#     # Gemini models
#     "gemini-1": "gemini",
#     "gemini-1.5": "gemini",
#     "gemini-pro": "gemini",
# }

# def openai_handler(messages, model, api_key):
#     openai.api_key = api_key
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0.3,
#         stream=True,
#     )
#     collected_text = ""
#     for chunk in response:
#         if 'choices' in chunk:
#             delta = chunk['choices'][0]['delta']
#             if 'content' in delta:
#                 token = delta['content']
#                 print(token, end='', flush=True)
#                 collected_text += token
#     print()
#     return collected_text

# def anthropic_handler(prompt, model, api_key):
#     client = anthropic.Client(api_key)
#     stream_response = client.completions.create(
#         model=model,
#         prompt=prompt,
#         max_tokens=1000,
#         temperature=0.3,
#         stop_sequences=["\n\n"],
#         stream=True,
#     )
#     collected_text = ""
#     for chunk in stream_response:
#         if 'completion' in chunk:
#             token = chunk['completion']
#             print(token, end='', flush=True)
#             collected_text += token
#     print()
#     return collected_text

# def gemini_handler(prompt, model, project_id, location="us-central1"):
#     """
#     Stream response from Gemini models on Google Vertex AI.

#     Requires environment variable GOOGLE_APPLICATION_CREDENTIALS set to your service account JSON key.

#     Args:
#         prompt (str): The prompt to send.
#         model (str): Gemini model ID (e.g. "gemini-1").
#         project_id (str): Your Google Cloud project ID.
#         location (str): Vertex AI location, defaults to "us-central1".

#     Returns:
#         str: Full response text.
#     """

#     client_options = ClientOptions(api_endpoint=f"{location}-aiplatform.googleapis.com")
#     client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

#     # The resource name of the model you want to use
#     model_name = f"projects/{project_id}/locations/{location}/publishers/google/models/{model}"

#     # Build the request payload for chat completion
#     request = {
#         "endpoint": model_name,
#         "instances": [{
#             "content": prompt,
#             "mime_type": "text/plain"
#         }],
#         "parameters": {
#             "temperature": 0.3,
#             "maxOutputTokens": 1000,
#             "candidateCount": 1,
#             "topP": 0.95,
#             "topK": 40,
#             "stopSequences": ["```"]
#         }
#     }

#     # NOTE: Actual Google Vertex AI streaming chat completions
#     # might use a different client method or gRPC streaming;
#     # this example is simplified and might need adjustment.

#     # Here, simulate streaming by fetching the full response at once:
#     response = client.predict(endpoint=model_name, instances=request["instances"], parameters=request["parameters"])

#     # Extract text from response predictions
#     full_response = ""
#     for prediction in response.predictions:
#         text = prediction.get("content", "")
#         print(text, end="", flush=True)
#         full_response += text
#     print()
#     return full_response


# def handle_deep_search(user_id, db_id, coll_id, question, model, api_key, limit, container_url, gemini_project_id=None):
#     # Step 1: fetch data
#     raw_data, status = handle_get_all(user_id, db_id, coll_id, limit, container_url)
#     if status != 200 or raw_data.get("status") != "OK":
#         return {"answer": "Failed to load data.", "filtered": []}

#     records = raw_data.get("results", [])

#     # Optional local filter for simple queries
#     def local_filter(records, question):
#         if "AAPL" in question and "above 200" in question:
#             return [r for r in records if r.get("symbol") == "AAPL" and r.get("price", 0) > 200]
#         return records

#     filtered_records = local_filter(records, question)

#     # Build prompt for the AI model
#     prompt = f"""
# You are a data assistant.

# Given this JSON data:
# {json.dumps(filtered_records, indent=2)}

# Answer this question:
# {question}

# Please respond with a brief summary of the filtered dataset, followed by the JSON data enclosed in triple backticks.

# End your response describing how you got to your answer.
# """

#     provider = MODEL_PROVIDER_MAP.get(model.lower())
#     if provider is None:
#         return {"answer": f"Model '{model}' not recognized.", "filtered": []}

#     try:
#         if provider == "openai":
#             messages = [
#                 {"role": "system", "content": "You provide data summaries and JSON outputs based on user queries."},
#                 {"role": "user", "content": prompt}
#             ]
#             content = openai_handler(messages, model, api_key)

#         elif provider == "anthropic":
#             content = anthropic_handler(prompt, model, api_key)

#         elif provider == "gemini":
#             if gemini_project_id is None:
#                 return {"answer": "Google Cloud project ID required for Gemini provider.", "filtered": []}
#             content = gemini_handler(prompt, model, gemini_project_id)

#         else:
#             return {"answer": f"Provider '{provider}' not supported.", "filtered": []}

#         # Extract JSON inside triple backticks
#         json_start = content.find("```")
#         json_end = content.rfind("```")
#         if json_start != -1 and json_end != -1 and json_end > json_start:
#             json_str = content[json_start + 3:json_end].strip()
#             try:
#                 filtered = json.loads(json_str)
#             except Exception:
#                 filtered = filtered_records
#         else:
#             filtered = filtered_records

#         return {"answer": content, "filtered": filtered}

#     except Exception as e:
#         return {"answer": f"Error occurred: {str(e)}", "filtered": []}
