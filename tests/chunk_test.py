import pytest
from src.chunk import truncate_on_h2

def test_truncate_on_h2():
    # Exemple d'entrée
    texts = [
        "Title1\nSome text##More text",
        "Title2\nAnother text##Even more text"
    ]

    # Résultat attendu
    expected_output = [
        {'title': 'Title1', 'chunk': 'Title1|||: Title1\nSome text', 'index': 0},
        {'title': 'Title1', 'chunk': 'Title1|||: More text', 'index': 1},
        {'title': 'Title2', 'chunk': 'Title2|||: Title2\nAnother text', 'index': 2},
        {'title': 'Title2', 'chunk': 'Title2|||: Even more text', 'index': 3}
    ]

    # Appel de la fonction

    result = truncate_on_h2(texts)
    print(result)

    # Vérification du résultat
    assert result == expected_output

# Pour exécuter le test
if __name__ == "__main__":
    pytest.main([__file__])