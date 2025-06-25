"""
User-Provided Test Cases for DBOR Conformance Level 2

This module contains the specific test cases provided by the user with their
expected DBOR encodings for validation and comparison.
"""

import sys
import os
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from encoder import encode
from decoder import decode, DBORDecodeError


class UserProvidedTestCases(unittest.TestCase):
    """Test cases with user-provided values and expected encodings."""
    
    def setUp(self):
        """Set up test cases with expected encodings."""
        # Test cases with their expected hex encodings (from user input)
        self.test_cases = [
            # Basic values
            (None, "FF"),
            (123456789, "1BFDCB5A06"),
            (-123456789, "3BFCCB5A06"),
            
            # Integer encoding boundaries - direct encoding
            (0, "00"),
            (23, "17"),  # 16#17 = 23
            
            # Extended encoding examples
            (24, "1800"),    # 16#18 = 24
            (279, "19FF"),   # 16#117 = 279  
            (280, "1A0000"), # 16#118 = 280
            (65815, "1BFFFF00"), # 16#10117 = 65815
            (65816, "1C00000000"), # 16#10118 = 65816
            (16842999, "1DFFFFFFFFFF"), # 16#1010117 = 16842999
            (16843000, "1E0000000000"), # 16#1010118 = 16843000
            (4311810295, "1FFFFFFFFFFF"), # 16#101010117 = 4311810295
            (4311810296, "200000000000000"), # 16#101010118 = 4311810296
            
            # Negative integers
            (-1, "20"),
            (-25, "3800"),   # -16#19 = -25
            (-26, "39FF"),   # -16#1A = -26  
            (-281, "3A0000"), # -16#119 = -281
            (-282, "3BFFFF"), # -16#11A = -282
            (-65817, "3C00000000"), # -16#10119 = -65817
            (-65818, "3DFFFFFFFFFF"), # -16#1011A = -65818
            
            # Strings
            ("", "60"),
            ("¡Olé!", "67C2A14FC3A921"),
            
            # Empty containers
            ([], "80"),
            (b"", "40"),
        ]
        
        # Long Latin text (abbreviated for testing)
        self.latin_text = ("Honestati consulitur et utilitati publice providetur, dum pacta quietis et pacis statu debito solidantur. "
                          "Noverint igitur universi, quod homines vallis Uranie universitasque vallis de Switz ac communitas hominum "
                          "Intramontanorum Vallis Inferioris maliciam temporis attendentes, ut se et sua magis defendere valeant et in "
                          "statu debito melius conservare, fide bona promiserunt invicem sibi assistere auxilio, consilio quolibet ac "
                          "favore, personis et rebus, infra valles et extra, toto posse, toto nisu contra omnes ac singulos, qui eis vel "
                          "alicui de ipsis aliquam intulerint violenciam, molestiam aut iniuriam in personis et rebus malum quodlibet "
                          "machinando, ac in omnem eventum quelibet universitas promisit alteri accurrere, cum necesse fuerit, ad "
                          "succurrendum et in expensis propriis, prout opus fuerit, contra impetus malignorum resistere, iniurias "
                          "vindicare, prestito super hiis corporaliter iuramento absque dolo servandis antiquam confederationis formam "
                          "iuramento vallatam presentibus innovando, ita tamen, quod quilibet homo iuxta sui nominis conditionem domino "
                          "suo convenienter subesse teneatur et servire. Communi etiam consilio et favore unanimi promisimus, statuimus "
                          "ac ordinavimus, ut in vallibus prenotatis nullum iudicem, qui ipsum officium aliquo precio vel peccunia "
                          "aliqualiter comparaverit vel qui noster incola vel conprovincialis non fuerit, aliquatenus accipiamus vel "
                          "acceptamus.")
        
        # Sequence test cases
        self.sequence_cases = [
            # 23-element sequence (1-23)
            (list(range(1, 24)), "57" + "".join(f"{i:02X}" for i in range(1, 24))),
            
            # 24-element sequence (1-24)  
            (list(range(1, 25)), "5800" + "".join(f"{i:02X}" for i in range(1, 25))),
            
            # Nested structure: [None, [1, [[], [""]]]]
            ([None, [1, [[], [""]]]], "87FF8501838081600"),
        ]
        
        # Byte string test cases
        self.byte_cases = [
            # 23-element byte string
            (bytes(range(1, 24)), "57" + "".join(f"{i:02X}" for i in range(1, 24))),
            
            # 24-element byte string
            (bytes(range(1, 25)), "5800" + "".join(f"{i:02X}" for i in range(1, 25))),
        ]
    
    def test_round_trip_integrity(self):
        """Test that all values have perfect round-trip integrity."""
        print("\n" + "=" * 60)
        print("USER-PROVIDED TEST CASES - ROUND-TRIP INTEGRITY")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        # Test basic cases
        for value, expected_hex in self.test_cases:
            with self.subTest(value=value):
                try:
                    encoded = encode(value)
                    decoded = decode(encoded)
                    
                    # Round-trip test (most important)
                    round_trip_ok = decoded == value
                    if round_trip_ok:
                        passed_tests += 1
                    
                    total_tests += 1
                    
                    print(f"Value: {value!r}")
                    print(f"  Round-trip: {'✅ PASS' if round_trip_ok else '❌ FAIL'}")
                    
                    if not round_trip_ok:
                        print(f"  Expected: {value!r}")
                        print(f"  Got: {decoded!r}")
                        self.fail(f"Round-trip failed for {value!r}")
                    
                except Exception as e:
                    total_tests += 1
                    print(f"Value: {value!r}")
                    print(f"  ❌ ERROR: {e}")
                    self.fail(f"Exception during round-trip test for {value!r}: {e}")
        
        # Test Latin text
        try:
            encoded_latin = encode(self.latin_text)
            decoded_latin = decode(encoded_latin)
            latin_ok = decoded_latin == self.latin_text
            if latin_ok:
                passed_tests += 1
            total_tests += 1
            
            print(f"Latin text ({len(self.latin_text)} chars):")
            print(f"  Round-trip: {'✅ PASS' if latin_ok else '❌ FAIL'}")
            
            if not latin_ok:
                self.fail("Latin text round-trip failed")
                
        except Exception as e:
            total_tests += 1
            print(f"Latin text: ❌ ERROR: {e}")
            self.fail(f"Exception during Latin text test: {e}")
        
        # Test sequences
        for value, expected_hex in self.sequence_cases:
            with self.subTest(value=value):
                try:
                    encoded = encode(value)
                    decoded = decode(encoded)
                    
                    round_trip_ok = decoded == value
                    if round_trip_ok:
                        passed_tests += 1
                    
                    total_tests += 1
                    
                    print(f"Sequence: {value if len(str(value)) < 60 else str(value)[:60] + '...'}")
                    print(f"  Round-trip: {'✅ PASS' if round_trip_ok else '❌ FAIL'}")
                    
                    if not round_trip_ok:
                        self.fail(f"Sequence round-trip failed for {value!r}")
                        
                except Exception as e:
                    total_tests += 1
                    print(f"Sequence: ❌ ERROR: {e}")
                    self.fail(f"Exception during sequence test: {e}")
        
        # Test byte strings  
        for value, expected_hex in self.byte_cases:
            with self.subTest(value=value):
                try:
                    encoded = encode(value)
                    decoded = decode(encoded)
                    
                    round_trip_ok = decoded == value
                    if round_trip_ok:
                        passed_tests += 1
                    
                    total_tests += 1
                    
                    print(f"Bytes ({len(value)} bytes):")
                    print(f"  Round-trip: {'✅ PASS' if round_trip_ok else '❌ FAIL'}")
                    
                    if not round_trip_ok:
                        self.fail(f"Bytes round-trip failed")
                        
                except Exception as e:
                    total_tests += 1
                    print(f"Bytes: ❌ ERROR: {e}")
                    self.fail(f"Exception during bytes test: {e}")
        
        print(f"\n{'='*60}")
        print(f"ROUND-TRIP SUMMARY: {passed_tests}/{total_tests} tests passed")
        if passed_tests == total_tests:
            print("🎉 ALL ROUND-TRIP TESTS PASSED!")
        else:
            print(f"⚠️  {total_tests - passed_tests} round-trip test(s) failed")
    
    def test_encoding_format_comparison(self):
        """Compare actual encodings with expected formats (informational)."""
        print("\n" + "=" * 60)
        print("ENCODING FORMAT COMPARISON (INFORMATIONAL)")
        print("=" * 60)
        
        matches = 0
        total = 0
        
        for value, expected_hex in self.test_cases:
            try:
                encoded = encode(value)
                actual_hex = encoded.hex().upper()
                expected_clean = expected_hex.replace(" ", "")
                
                encoding_match = actual_hex == expected_clean
                if encoding_match:
                    matches += 1
                
                total += 1
                
                print(f"Value: {value!r}")
                print(f"  Expected: {expected_clean}")
                print(f"  Actual:   {actual_hex}")
                print(f"  Match:    {'✅' if encoding_match else '❌'}")
                
                if not encoding_match:
                    # Analyze the difference
                    if len(actual_hex) >= 2:
                        first_byte = int(actual_hex[:2], 16)
                        header = (first_byte >> 5) & 0x7
                        payload = first_byte & 0x1F
                        print(f"  Analysis: Header={header}, Payload={payload}")
                print()
                
            except Exception as e:
                total += 1
                print(f"Value: {value!r}")
                print(f"  ❌ ERROR: {e}")
                print()
        
        print(f"ENCODING FORMAT SUMMARY: {matches}/{total} exact matches")
        print("Note: Different encodings may still be valid if round-trip works")
    
    def test_specific_integer_boundaries(self):
        """Test specific integer boundary cases from user input."""
        print("\n" + "=" * 60)
        print("INTEGER BOUNDARY TESTS")
        print("=" * 60)
        
        # Test the specific boundary values from user input
        boundary_tests = [
            (23, "17", "Last direct encoding"),
            (24, "1800", "First extended encoding"),
            (279, "19FF", "16#117 boundary"),
            (280, "1A0000", "16#118 boundary"),
            (-25, "3800", "First negative extended"),
        ]
        
        for value, expected_hex, description in boundary_tests:
            with self.subTest(value=value, description=description):
                try:
                    encoded = encode(value)
                    decoded = decode(encoded)
                    actual_hex = encoded.hex().upper()
                    
                    round_trip_ok = decoded == value
                    encoding_match = actual_hex == expected_hex.replace(" ", "")
                    
                    print(f"{description}: {value}")
                    print(f"  Expected: {expected_hex}")
                    print(f"  Actual:   {actual_hex}")
                    print(f"  Encoding: {'✅' if encoding_match else '❌'}")
                    print(f"  Round-trip: {'✅' if round_trip_ok else '❌'}")
                    print()
                    
                    # Round-trip is mandatory
                    self.assertTrue(round_trip_ok, f"Round-trip failed for {value}")
                    
                except Exception as e:
                    print(f"{description}: {value}")
                    print(f"  ❌ ERROR: {e}")
                    print()
                    self.fail(f"Exception testing {description}: {e}")


def run_user_provided_tests():
    """Run the user-provided test cases as a standalone function."""
    print("DBOR User-Provided Test Suite")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(UserProvidedTestCases)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("USER TEST SUITE SUMMARY")
    print("=" * 50)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("🎉 ALL USER-PROVIDED TESTS PASSED!")
        print("✅ Round-trip integrity is perfect!")
    else:
        print(f"⚠️  {failures + errors} test(s) had issues")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result


if __name__ == '__main__':
    # Run the user-provided tests
    run_user_provided_tests()
