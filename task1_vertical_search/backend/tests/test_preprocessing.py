from utils.text_preprocessing import preprocess


def test_lowercases_and_removes_punctuation():
    result = preprocess("Digital Health, Mental Well-Being & AI!")
    assert result == result.lower()
    assert "," not in result and "&" not in result and "!" not in result


def test_removes_stopwords():
    result = preprocess("This is a study of the effect of stress")
    tokens = result.split()
    assert "the" not in tokens
    assert "is" not in tokens
    assert "study" in tokens
    assert "stress" in tokens


def test_empty_input_returns_empty_string():
    assert preprocess("") == ""
    assert preprocess(None) == ""


def test_same_pipeline_applies_to_query_and_document_text():
    # The coursework requires identical preprocessing for documents and queries.
    doc_text = "Mental Health interventions for postgraduate students"
    query_text = "mental health"
    assert "mental" in preprocess(doc_text).split()
    assert preprocess(query_text) == preprocess(query_text.lower())
