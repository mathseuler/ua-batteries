import pytest
from ua_batteries.assumptions import total_price, ROZPODIL, MARZHA, PEREDACHA

def test_total_price_1():
    assert total_price(0) == ROZPODIL + PEREDACHA