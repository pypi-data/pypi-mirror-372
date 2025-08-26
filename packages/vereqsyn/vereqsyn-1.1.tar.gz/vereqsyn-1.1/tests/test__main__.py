import vereqsyn.__main__

from .testing import tmp_copy


def test___main____main__1(fixtures, capsys, tmp_path):
    """It runs vereqsyn sync and prints a message."""
    r3 = str(tmp_copy(tmp_path, fixtures / "r3.txt"))
    v3 = str(tmp_copy(tmp_path, fixtures / "v3.cfg"))

    vereqsyn.__main__.main([v3, r3])
    out, err = capsys.readouterr()
    assert out.startswith("Synced ")
    assert err == ""


def test___main____main__2(fixtures, capsys, tmp_path):
    """It runs vereqsyn recreate and prints a message."""
    r1 = str(tmp_copy(tmp_path, fixtures / "r1.txt"))
    v2 = str(tmp_copy(tmp_path, fixtures / "v2.cfg"))

    vereqsyn.__main__.main([v2, r1])
    out, err = capsys.readouterr()
    assert out.startswith("Recreated ")
    assert err == ""
