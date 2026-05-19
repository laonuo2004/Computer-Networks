import unittest

from gbn.pdu import PDU, PDUError, TYPE_DATA, crc_ccitt_false, in_window, seq_mod


class PduTests(unittest.TestCase):
    def test_crc_standard_vector(self):
        self.assertEqual(crc_ccitt_false(b"123456789"), 0x29B1)

    def test_pdu_round_trip_and_crc_failure(self):
        pdu = PDU(TYPE_DATA, 1234, 7, 6, b"hello")
        encoded = bytearray(pdu.encode())
        decoded = PDU.decode(bytes(encoded))
        self.assertEqual(decoded, pdu)
        encoded[-1] ^= 0x55
        with self.assertRaises(PDUError):
            PDU.decode(bytes(encoded))

    def test_sequence_wrap_window(self):
        self.assertEqual(seq_mod(258, 8), 2)
        self.assertTrue(in_window(250, 250, 12, 8))
        self.assertTrue(in_window(5, 250, 12, 8))
        self.assertFalse(in_window(6, 250, 12, 8))


if __name__ == "__main__":
    unittest.main()
