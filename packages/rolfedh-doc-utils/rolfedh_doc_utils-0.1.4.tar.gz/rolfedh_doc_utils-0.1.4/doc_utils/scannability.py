# doc_utils/scannability.py

import os
import re

def check_scannability(adoc_files, max_sentence_length=22, max_paragraph_sentences=3):
    long_sentences = []
    long_paragraphs = []
    for file_path in adoc_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                paragraphs = content.split('\n\n')
                for i, para in enumerate(paragraphs):
                    sentences = re.split(r'(?<=[.!?]) +', para.strip())
                    for sent in sentences:
                        if len(sent.split()) > max_sentence_length:
                            long_sentences.append((file_path, i+1, sent.strip()))
                    if len(sentences) > max_paragraph_sentences:
                        long_paragraphs.append((file_path, i+1, len(sentences)))
        except Exception as e:
            print(f"Warning: could not read {file_path}: {e}")
    return long_sentences, long_paragraphs
