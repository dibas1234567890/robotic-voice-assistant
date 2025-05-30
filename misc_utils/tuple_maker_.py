import uuid

async def prepare_upsert_tuples(embeddings, splits) -> list:
    
    texts = [split.page_content for split in splits]



    upsert_items = [
        (str(uuid.uuid4()), vectors['values'], {"text": text})
        for text, vectors in zip(texts, embeddings.data)
    ]

    return upsert_items
