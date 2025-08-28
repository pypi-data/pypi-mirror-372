import pytest
import numpy as np


def test_from_texts_basic():
    import copyforward

    # realistic small example: repeated greeting across messages
    messages = [
        "Hello world from Alice",
        "Hello world from Alice — how are you?",
        "Alice says: Hello world from Alice"
    ]
    cf = copyforward.CopyForwardText.from_texts(messages, exact_mode=True)
    assert isinstance(cf.compression_ratio(), float)
    rendered = cf.render()
    assert rendered == messages

    # Test segments return proper objects now
    segments = cf.segments()
    assert isinstance(segments, list)
    assert len(segments) == 3  # Three messages
    for msg_segments in segments:
        assert isinstance(msg_segments, list)
        for seg in msg_segments:
            # Should be either LiteralSegment or ReferenceSegment
            assert hasattr(seg, '__class__')
            if hasattr(seg, 'text'):
                # LiteralSegment
                assert isinstance(seg.text, str)
            else:
                # ReferenceSegment
                assert isinstance(seg.message, int)
                assert isinstance(seg.start, int)
                assert isinstance(seg.len, int)

    # also test approximate mode returns the same render
    cf2 = copyforward.CopyForwardText.from_texts(messages, exact_mode=False)
    assert cf2.render() == messages


def test_from_tokens_list_and_numpy():
    import copyforward

    # tokens representing small message sequences (e.g., token ids)
    msgs_list = [[10, 11, 12, 13], [10, 11, 12, 13, 14]]
    cf1 = copyforward.CopyForwardTokens.from_tokens(msgs_list, exact_mode=True)
    out1 = cf1.render()
    assert out1 == msgs_list

    # Test segments return proper objects now
    segments = cf1.segments()
    assert isinstance(segments, list)
    for msg_segments in segments:
        assert isinstance(msg_segments, list)
        for seg in msg_segments:
            assert hasattr(seg, '__class__')
            if hasattr(seg, 'tokens'):
                # LiteralTokens
                assert isinstance(seg.tokens, list)
                assert all(isinstance(t, int) for t in seg.tokens)
                # Test as_numpy method
                numpy_tokens = seg.as_numpy()
                assert isinstance(numpy_tokens, np.ndarray)
            else:
                # ReferenceTokens
                assert isinstance(seg.message, int)
                assert isinstance(seg.start, int)
                assert isinstance(seg.len, int)

    # approximate mode should also round-trip
    cf1a = copyforward.CopyForwardTokens.from_tokens(msgs_list, exact_mode=False)
    assert cf1a.render() == msgs_list

    # numpy inputs
    # NumPy outputs are supported; inputs should be Python lists for strong typing
    msgs_np = [[10, 11, 12, 13], [10, 11, 12, 13, 14]]
    cf2 = copyforward.CopyForwardTokens.from_tokens(msgs_np, exact_mode=True)
    out2 = cf2.render(as_numpy=True)
    assert isinstance(out2, list)
    assert all(isinstance(x, np.ndarray) for x in out2)
    # values match
    assert [list(x) for x in out2] == [[10,11,12,13],[10,11,12,13,14]]
