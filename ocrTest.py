import unittest
import pytesser
import processCards
import os

class TestOCR(unittest.TestCase):

    def setUp(self):
        imgFolder = 'Screenshots'
        self.files = os.listdir(imgFolder)
        self.files = sorted(self.files, key=lambda file: int(file.rstrip('.png')[10:]))
        self.files = map(lambda f : os.path.join(imgFolder, f), self.files)
        
        self.s1 = [('king', 'spade'), ('king', 'club'), ('4','diamond'),('7','diamond'),('9','diamond'),
                   ('6','spade'),('8','club'),('6','club')]
        self.s2 = [('king','diamond'),('king','spade'),('3','club'),('10','spade'),('king','heart'),
                   ('ace','club'),('5','club'),('5','heart')]
        self.s3 = [('queen','diamond'),('jack','diamond'),('5','heart'),('6','spade'),('9','diamond'),
                   ('queen','spade'),('9','club')]
        self.s4 = [('jack','spade'),('3','diamond'),('4','heart'),('5','club'),('5','spade'),
                   ('ace','diamond'),('2','diamond')]
        self.s5 = [('7','spade'),('5','heart'),('ace','diamond'),('10','spade'),('9','heart'),
                   ('7','heart'),('queen','heart')]
        self.s6 = [('queen','spade'),('king','spade'),('2','club'),('2','heart'),('3','spade'),
                   ('10','heart'),('4','heart')]
        self.s7 = [('king','spade'),('2','spade'),('ace','diamond'),('queen','diamond'),
                   ('9','diamond'),('3','heart'),('jack','spade')]
        self.s8 = [('queen','spade'),('10','club'),('jack','heart'),('4','diamond'),('10','spade'),
                   ('2','diamond'),('6','diamond')]
        self.s9 = [('2','club'),('6','heart'),('7','club'),('jack','heart'),('10','spade'),
                   ('4','spade'),('3','heart')]
        self.s10 = [('queen','spade'),('king','club'),('6','club'),('8','spade'),('ace','spade'),
                    ('5','club'),('5','diamond')]
        self.s11 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s12 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s13 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s14 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s15 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s16 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s17 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s18 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s19 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s20 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s21 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.s22 = [('',''),('',''),('',''),('',''),('',''),('',''),('','')]
        self.tests = [self.s1,
                      self.s2,
                      self.s3,
                      self.s4,
                      self.s5,
                      self.s6,
                      self.s7,
                      self.s8,
                      self.s9,
                      self.s10]


    def test_template(self):
        # load all the screenshots and make sure each one is as it should be
        
        #for f in self.files:
        for i in range(len(self.tests)):
            cards = processCards.extractCards(self.files[i])
            meaning = processCards.getMeaningFromCards(cards)
            self.assertEqual(sorted(meaning.values()), sorted(self.tests[i]))
            
            
if __name__ == '__main__':
    unittest.main()
