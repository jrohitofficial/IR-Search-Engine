from preprocessing.text_preprocessing import preprocess, stem_tokens, tokenise


def test_pipeline_lowercases_removes_punctuation_and_stopwords():
    result = preprocess("The Economy is Growing, and Inflation is Falling!")
    tokens = result.split()
    assert result == result.lower()
    assert "the" not in tokens and "is" not in tokens and "and" not in tokens
    assert "," not in result and "!" not in result


def test_stemming_collapses_related_word_forms():
    # Real (and well-documented) classic-Porter-algorithm behaviour, verified
    # here rather than assumed: "economic"/"economics" both stem to "econom",
    # and "economy"/"economies" both stem to "economi" -- but "economy" and
    # "economic" do NOT share a stem, because the "-y -> -i" rule and the
    # "-ic"/"-ics" suffix-stripping rules take different paths. This is a
    # known limitation of the Porter algorithm (it stems by fixed suffix
    # rules, not by a dictionary/morphological model), not a bug in this
    # pipeline -- so the test documents the real grouping rather than
    # asserting a single stem for all four forms.
    assert stem_tokens(["economic"]) == stem_tokens(["economics"]) == ["econom"]
    assert stem_tokens(["economy"]) == stem_tokens(["economies"]) == ["economi"]

    stemmed = stem_tokens(tokenise("economy economic economics economies"))
    assert len(set(stemmed)) == 2


def test_empty_input_returns_empty_string():
    assert preprocess("") == ""
    assert preprocess(None) == ""


def test_long_input_is_processed_without_error():
    long_text = "The government announced new fiscal policy. " * 500
    result = preprocess(long_text)
    assert len(result) > 0
