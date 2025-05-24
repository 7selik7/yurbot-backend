import fitz

class DocumentReader:
    @staticmethod
    def read_document_content(doc_path: str, mime_type: str) -> str:
        try:
            if mime_type == "application/pdf":
                text = ""
                with fitz.open(doc_path) as pdf:
                    for page in pdf:
                        text += page.get_text()
                return text
            elif mime_type == "text/plain":
                with open(doc_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"⚠️ Формат {mime_type} поки не підтримується."
        except Exception as e:
            return f"⚠️ Не вдалося прочитати документ: {str(e)}"

document_reader = DocumentReader()