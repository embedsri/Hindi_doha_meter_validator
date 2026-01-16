import unittest
from src.meter import MatraCounter
from src.text_utils import normalize_text, clean_for_counting
from src.doha_validator import validate_doha

class TestDohaMeter(unittest.TestCase):
    def setUp(self):
        self.mc = MatraCounter()

    def test_basic_matra_count(self):
        # 'क' = 1
        self.assertEqual(self.mc.count_matras('क')[0], 1)
        # 'का' = 2
        self.assertEqual(self.mc.count_matras('का')[0], 2)
        # 'कि' = 1
        self.assertEqual(self.mc.count_matras('कि')[0], 1)
        # 'की' = 2
        self.assertEqual(self.mc.count_matras('की')[0], 2)
        # 'कं' (Anusvara) = 2
        self.assertEqual(self.mc.count_matras('कं')[0], 2)
        
    def test_conjunct_rule(self):
        # 'सत्य' -> Sa (2 because of tya), tya (1) = 3
        # Tokens: [स], [त्, य] -> 'स' sees 'त्' next? 
        # Actually my logic groups [त्, य] as one token usually?
        # Let's check logic: 't' is halant, so counts 0 but promotes previous.
        # 'ya' is normal.
        count, weights = self.mc.count_matras('सत्य')
        self.assertEqual(count, 3)
        
        # 'कष्ट' -> Ka (2), shta (1) = 3
        count, weights = self.mc.count_matras('कष्ट')
        self.assertEqual(count, 3)
        
    def test_full_doha(self):
        # Kabir Doha
        # बडा भया तो क्या भया, जैसे पेड खजूर
        # Ba(1)da(2) bha(1)ya(2) to(2) kya(2) bha(1)ya(2) = 13?
        # 1+2 + 1+2 + 2 + 2 + 1+2 = 13.
        # jaise(2,2) ped(2,1) khajoor(1,2,1) -> 4 + 3 + 4 = 11.
        
        charan1 = "बड़ा भया तो क्या भया" 
        # Note: kya is conjunct half-k. Ka is half, ya is 2. 
        # 'To' (before kya) is Guru(2). 
        # 'kya' itself: k(0), ya(2). 0+2 = 2.
        # previous 'to' is 2. stays 2.
        
        self.assertEqual(self.mc.count_matras(charan1)[0], 13)
        
        charan2 = "जैसे पेड़ खजूर"
        # jaise: 2,2
        # ped: 2,1 (assuming e is matra, d is short)
        # khajoor: 1, 2, 1
        self.assertEqual(self.mc.count_matras(charan2)[0], 11)

    def test_validator(self):
        doha = """
        बड़ा भया तो क्या भया, जैसे पेड़ खजूर |
        पंथी को छाया नहीं, फल लागे अति दूर ||
        """
        is_valid, report = validate_doha(doha)
        self.assertTrue(is_valid, report)

if __name__ == '__main__':
    unittest.main()
