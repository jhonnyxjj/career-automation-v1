from career.normalizer import extract_technologies


def test_node_does_not_imply_javascript():
    assert extract_technologies('TypeScript e Node.js') == ['TypeScript', 'Node.js']
    assert 'JavaScript' in extract_technologies('JavaScript e Node.js')
