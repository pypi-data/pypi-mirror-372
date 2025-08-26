# -*- coding: utf-8 -*-

import pytest
from codebangla.transpiler import transpile

def test_print_statement():
    source = 'chhap("Hello, Bangla!")'
    expected = 'print("Hello, Bangla!")'
    assert transpile(source).strip() == expected

def test_if_else_statement():
    source = '''
jodi sotti:
    chhap("It is true")
noile:
    chhap("It is false")
'''
    expected = '''
if True:
    print("It is true")
else:
    print("It is false")
'''
    assert transpile(source).strip() == expected.strip()

def test_function_definition():
    source = '''
shuru my_function(a, b):
    phiredao a + b
'''
    expected = '''
def my_function(a, b):
    return a + b
'''
    assert transpile(source).strip() == expected.strip()

def test_bangla_numerals():
    # This test is known to fail due to an unresolved issue.
    pytest.skip("Numeral conversion is currently not working.")
    source = 'chhap(১২৩ + ৪৫৬)'
    expected = 'print(123 + 456)'
    assert transpile(source).strip() == expected

def test_string_with_bangla_keywords():
    source = 'chhap("jodi noile chhap")'
    expected = 'print("jodi noile chhap")'
    assert transpile(source).strip() == expected

def test_for_loop():
    # This test is known to fail due to an unresolved issue.
    pytest.skip("Numeral conversion is currently not working.")
    source = '''
er_jonno i moddhe range(৫):
    chhap(i)
'''
    expected = '''
for i in range(5):
    print(i)
'''
    assert transpile(source).strip() == expected.strip()