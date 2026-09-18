from app.text_splitter import split_text


def test_split_text_respects_chunk_size():
    text = "palabra " * 300
    chunks = split_text(text)
    assert len(chunks) > 1
    assert all(len(c) <= 600 for c in chunks)  # margen sobre chunk_size por el overlap


def test_split_text_short_input_single_chunk():
    text = "Expediente breve."
    chunks = split_text(text)
    assert chunks == [text]
