from .db_model import chunks, document

def chunk_text(text, chunk_size=400, overlap=50):
    chunks = []
    chunk_count = 0
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
        chunk_count += 1
    
    print(f"Total chunks created: {chunk_count}")
    print(f"First chunk: {chunks[0]}")
    print(f"Last chunk: {chunks[-1]}")


        
    return chunks
