Application that uses a sliding window to extract the top 10 codon frequencies and prompts a local llm to find the foods that contains the least
amount of those codons in order to hinder the development of the bacterial/viral genome.

### Important
This requires an active ollama service.
```python
def query_ollama_api(top_codons, model="hf.co/TrevorJS/gemma-4-E4B-it-uncensored-GGUF:Q8_0", host="http://localhost:11434"):
```
Change the model from this line to point ollama to a model installed locally. (If needed the host as well.)

After this provide the genome file as an argument to the pyhton function like this:
```bash
python codon_food.py GCF_001343785.1_ViralMultiSegProj274766_genomic.fna
```

