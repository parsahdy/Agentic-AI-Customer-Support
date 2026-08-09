def faq_to_document(row: dict) -> dict:

    question = row.get("question", "")
    answer = row.get("answer", "")  
    document_id = row.get("document_id", "")

    return {
            "content": 
                f"Question: {question}\n"
                f"Answer: {answer}"
            ,
            "metadata": {
                "document_id": document_id,
                "source": "faq_clean.csv",
                "source_type": "csv",
            }
        }


def ticket_to_document(row: dict) -> dict:

    message = row.get("message", "")
    response = row.get("response", "")
    tag = row.get("tag", "")
    category = row.get("category", "")
    language = row.get("language", "")

    return {
        "content": 
            f"Message: {message}\n"
            f"Response: {response}"
        ,
        "metadata": {
            "tag": tag,
            "category": category,
            "language": language,
            "source": "tickets_clean.csv",
            "source_type": "csv",
        }
    }
