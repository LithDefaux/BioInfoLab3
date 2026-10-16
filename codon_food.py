#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter

def read_fasta(file_path):
    """Reads FASTA/FNA files and combines sequence lines into one string."""
    sequence = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith(">"):
                    continue
                sequence.append(line.upper())
        return "".join(sequence)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

def get_top_sliding_codons(sequence, top_n=10):
    """Calculates codon frequencies using a sliding window of step size 1."""
    codon_counts = Counter()
    for i in range(len(sequence) - 2):
        codon = sequence[i:i+3]
        if all(base in "ACGTU" for base in codon):
            codon_counts[codon] += 1
    return codon_counts.most_common(top_n)

def query_ollama_api(top_codons, model="hf.co/TrevorJS/gemma-4-E4B-it-uncensored-GGUF:Q8_0", host="http://localhost:11434"):
    """Queries a local Ollama instance with codon frequencies."""
    url = f"{host}/api/chat"
    
    formatted_codons = "\n".join([
        f"Rank {rank}: {codon} (Frequency: {count})" 
        for rank, (codon, count) in enumerate(top_codons, start=1)
    ])
    
    prompt = (
        "You are a bioinformatics and nutrition assistant.\n"
        "Below are the top 10 most frequent codons extracted from a genome using a sliding window:\n\n"
        f"{formatted_codons}\n\n"
        "Based on the Guanine-Cytosine (GC) vs. Adenine-Thymine (AT) ratio of these codons and overall genomic density, "
        "provide a list of foods and dietary sources that contain the LEAST amount of these specific codons. "
        "Categorize your response into low-GC plant crops, high-water/low-DNA foods, pure refined foods, and low-GC microbes."
    )
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    headers = {"Content-Type": "application/json"}
    data_bytes = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["message"]["content"]
    except urllib.error.URLError as e:
        print(f"Failed to connect to Ollama at {host}. Is Ollama running? Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error querying Ollama API: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Extract top 10 codon frequencies from FASTA genome and query LLM for food analysis."
    )
    parser.add_argument("fasta_file", help="Path to input .fasta or .fna file")
    #parser.add_argument("--api-key", help="Gemini API Key (or set GEMINI_API_KEY environment variable)")
    
    args = parser.parse_args()
    
    #api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    #if not api_key:
    #    print("Error: Missing API key. Pass --api-key or set GEMINI_API_KEY in your environment.", file=sys.stderr)
    #    sys.exit(1)

    sequence = read_fasta(args.fasta_file)
    top_codons = get_top_sliding_codons(sequence, top_n=10)

    print(f"Sequence length: {len(sequence)} bp")
    print("\nTop 10 Codon Frequencies:")
    print("-" * 35)
    for rank, (codon, count) in enumerate(top_codons, start=1):
        print(f"{rank:<4} | {codon:<8} | {count}")
    print("-" * 35)

    print("\nFetching LLM analysis for low-codon foods...\n")
    analysis = query_ollama_api(top_codons)
    
    print("=== ANALYSIS RESULT ===")
    print(analysis)

if __name__ == "__main__":
    main()