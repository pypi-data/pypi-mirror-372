from pytextrust.text_dist import dist_needleman_wunsch, compute_overlaping_zone


def test_dist_needleman_wunsch_base():
    seq_a = ["The", "quick", "brown", "fox"]
    seq_b = ["The", "quicky", "brown", "foxyyyyy"]
    val = dist_needleman_wunsch(seq_a=seq_a, seq_b=seq_b)
    assert val == -1.2083333333333335


def test_compute_overlaping_zone_base():
    seq_a = ["The", "quick", "brown", "fox"]
    seq_b = ["The", "quicky", "brown", "foxyyyyy"]
    best_seq_a_len, best_seq_b_len, best_needleman_wunsch_dist, _ \
        = compute_overlaping_zone(seq_a=seq_a, seq_b=seq_b,  min_overlap=1,
                                  mismatch_penalty=None,
                                  max_length_diff=2)

    assert best_seq_a_len == 4
    assert best_seq_b_len == 4
    assert best_needleman_wunsch_dist == -1.2083333333333335
