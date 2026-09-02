from retrieval.ranking import rank_evidence_items, calculate_source_factor, calculate_keyword_density


def test_calculate_source_factor():
    assert calculate_source_factor("src/processor.py") == 1.0
    assert calculate_source_factor("tests/test_processor.py") == 0.2
    assert calculate_source_factor("src/deep/test_utils.py") == 0.2


def test_calculate_keyword_density():
    text = "The Processor class validates incoming request data"
    keywords = ["Processor", "validates", "data"]
    assert calculate_keyword_density(text, keywords) == 1.0

    keywords = ["Processor", "nonexistent"]
    assert calculate_keyword_density(text, keywords) == 0.5


def test_rank_evidence_items():
    items = [
        {
            "file": "tests/test_processor.py",
            "symbol": "test_run",
            "content": "def test_run(): pass",
            "semantic_score": 0.9,
            "source_type": "semantic"
        },
        {
            "file": "src/processor.py",
            "symbol": "Processor",
            "content": "class Processor: def run(self): pass",
            "semantic_score": 0.85,
            "source_type": "symbol"
        }
    ]

    ranked = rank_evidence_items(
        items,
        query="Where is Processor class implemented?",
        symbol_name="Processor",
        keywords=["Processor", "class"]
    )

    assert len(ranked) == 2
    # The source code item (src/processor.py) should be ranked higher due to symbol match & source boost
    assert ranked[0]["file"] == "src/processor.py"
    assert ranked[0]["rank_score"] > ranked[1]["rank_score"]
    assert "score_breakdown" in ranked[0]
