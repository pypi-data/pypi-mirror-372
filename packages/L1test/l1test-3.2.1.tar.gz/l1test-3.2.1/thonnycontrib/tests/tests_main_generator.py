import unittest
from thonnycontrib.frontend.main_generator.main_generator import MainGenerator, MAIN_TO_GENERATE

class TestMainGenerator(unittest.TestCase):
    def setUp(self):
        self.main_generator = MainGenerator(source="")
        
    def tearDown(self):
        self.main_generator = None

    def test_generate_with_no_existing_main(self):
        generated: bool = self.main_generator.generate()
        self.assertTrue(generated) 

    def test_generate_with_existing_main(self):
        self.main_generator.set_source("if __name__ == '__main__': pass")
        generated: bool = self.main_generator.generate()
        self.assertFalse(generated) # ensure nothing is generated
        
    def test_generate_with_existing_commented_main(self):
        self.main_generator.set_source("# if __name__ == '__main__': pass")
        generated: bool = self.main_generator.generate()
        self.assertTrue(generated) # ensure that __main__ is generated

    def test_find_main_lineno(self):
        text = (
                """\
                print('hello, world')
                if __name__ == '__main__':
                    print('this script is being run directly')
                """
            )
        lineno = self.main_generator._MainGenerator__find_main_lineno(text) # this is how we call private methods in python just to test them
        self.assertEqual(lineno, 2)
        
    def test_find_main_lineno_when_commented(self):
        text = (
                """\
                print('hello, world')
                # if __name__ == '__main__':
                #    print('this script is being run directly')
                """
            )
        lineno = self.main_generator._MainGenerator__find_main_lineno(text)
        self.assertEqual(lineno, None)

if __name__ == "__main__":
    unittest.main(verbosity=2)
