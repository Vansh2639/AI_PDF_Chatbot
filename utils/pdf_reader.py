import fitz
from langchain_core.documents import Document


def extract_text_from_pdf(uploaded_files):

    documents = []
    total_pages = 0

    for uploaded_file in uploaded_files:

        pdf = fitz.open(
            stream=uploaded_file.read(),
            filetype="pdf",
        )

        total_pages += len(pdf)

        for page_number, page in enumerate(pdf):

            # Preserve original reading order
            text = page.get_text("text", sort=False)

            if text.strip():

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "page": page_number + 1,
                            "source": uploaded_file.name,
                        },
                    )
                )

        pdf.close()

    return documents, total_pages
