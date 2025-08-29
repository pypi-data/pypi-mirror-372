from yourpkg.height import parse_height

def test_classic_fslash():
    assert parse_height("5/11/2000") == 180.3  # 71 in → 180.34 cm → 180.3

def test_excel_mangled():
    assert parse_height("11-May") == 180.3     # 5'11"

def test_excel_mangled2():
    assert parse_height("2-Jun") == 188.0      # 6'2" -> 187.96 → 188.0

def test_missing_dash():
    assert parse_height("-") is None

def test_ranges():
    assert parse_height("9/1/2000") is None    # feet too large
    assert parse_height("5/12/2000") is None   # inches too large
