import re
from typing import Optional, Tuple
import faiss
import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# find out the act and scene number
def extract_act_scene(text: str) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    act_number: Optional[int] = None
    scene_number: Optional[int] = None

    act_match = re.search(r"Act\s*(\d+)", text, re.IGNORECASE)
    if act_match:
        act_number = int(act_match.group(1))

    scene_match = re.search(r"Scene\s*(\d+)", text, re.IGNORECASE)
    if scene_match:
        scene_number = int(scene_match.group(1))

    return act_number, scene_number

# load data
EMBEDDING_PATH = os.path.join(HERE, "data", "shakespeare_chunked_embeddings.npy")
embeddings = np.load(EMBEDDING_PATH)
INDEX_PATH = os.path.join(HERE, "data", "shakespeare_chunked_index.bin")
index = faiss.read_index(INDEX_PATH)
DOCUMENTS_PATH = os.path.join(HERE, "data", "shakespeare_chunked_emb.json")
with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)
    
embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

model_id = "Qwen/Qwen2.5-7B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

print("Model loaded with 4-bit quantization. Device:", model.device)

# get the embedding of user query
def embed_query(query: str):
    vec = embedder.encode([query], convert_to_numpy=True)
    return vec.astype("float32")

# get top 5 matches based on query
def retrieve_top_k(query: str, k: int = 5, act: str = None, scene: str = None, play: str = None,  documents: list = documents):
    q_vec = embed_query(query)  # shape (1, D)

    # Filter documents by Act and Scene if specified
    if act or scene:
        filtered_docs = []
        filtered_embeddings = []
        for i, doc in enumerate(documents):
            metadata = doc.get("metadata", {})
            # if play and metadata.get("play") != str(play):
            #     continue
            if act and metadata.get("act") != str(act):
                continue
            if scene and metadata.get("scene") != str(scene):
                continue
            filtered_docs.append((i, doc))
            filtered_embeddings.append(embeddings[i])
        
        if not filtered_docs:
            return [{"error": "No documents match the Act and Scene filter"}]
        
        # Convert to np array for FAISS-like search
        filtered_embeddings_np = np.vstack(filtered_embeddings)
        
        # Search using cosine similarity
        sims = cosine_similarity(q_vec, filtered_embeddings_np)[0]
        top_k_indices = np.argsort(sims)[-k:][::-1]

        results = []
        for i in top_k_indices:
            idx, doc = filtered_docs[i]
            results.append({
                "id": doc.get("id", idx),
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": float(sims[i])
            })
        return results

    # Fallback: No filtering, use entire index
    distances, indices = index.search(q_vec, k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        doc = documents[idx]
        results.append({
            "id": doc.get("id", idx),
            "text": doc["text"],
            "metadata": doc["metadata"],
            "score": float(dist)
        })
    return results

# prompt building for the model with RAG
def build_prompt(retrieved_chunks, user_question, style="shake"):
    if style == "shake":
        tone_instruction = "Respond in Shakespearean English, quoting from these passages."
    else:
        tone_instruction = "Respond clearly as a Shakespeare expert, quoting from these passages."

    header = f"You are a Shakespeare expert. {tone_instruction}\n\n"
    passages = ""
    for i, chunk in enumerate(retrieved_chunks, start=1):
        passages += f"[Passage {i}]\n{chunk['text']}\n\n"
    question_block = f"### Question:\n{user_question}\n\n### Answer:\n"
    return header + passages + question_block

# finetuning the model for generate answers
def generate_answer(prompt: str, max_new_tokens: int = 300, temperature: float = 0.8):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True).to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    generated = output_ids[0][ inputs["input_ids"].shape[1]: ]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()

# handeling user query
def user_query(user_question: str):
  (act, scene) = extract_act_scene(user_question)
  top_chunks = retrieve_top_k(user_question, k=5, act=act, scene=scene)
  print("Retrieved passages (top 5):")
  for i, c in enumerate(top_chunks, start=1):
    print(i)
    print(c)

  prompt = build_prompt(top_chunks, user_question, style="no-shake")

  print("\nGenerating answer...\n")
  answer = generate_answer(prompt, max_new_tokens=200, temperature=0.8)
  print("=== ShakespeareBot Answer ===")
  print(answer)
  print("#"*50)
  
  return answer
  
user_query("Why does Hamlet not kill Claudius. Please use only sourced form Play Hamlet, Act 3, Scene 3?")