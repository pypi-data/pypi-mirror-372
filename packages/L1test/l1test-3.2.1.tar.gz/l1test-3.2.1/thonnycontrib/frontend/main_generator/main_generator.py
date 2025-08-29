from thonny.editors import EditorCodeViewText
import re
from thonny import get_workbench

# The regex to check if the __main__ already exists
# The regex checks if a string already contains the __main__ and not commented.
_REGEX = re.compile(r"(?m)^\s*if\s+__name__\s*==\s*['\"]__main__['\"]\s*:\s*")

# The generated `__main__` function. 
# Leave a blank line before the `if __name__ == '__main__':` line, 
# so that the generated main function is separated from the rest of the code.
MAIN_TO_GENERATE:str = (
"""

if __name__ == '__main__':
    # éxécuté qd ce module n'est pas initialisé par un import.
    pass\
"""
)

class MainGenerator(): 
    """
    This class is responsible for generating the __main__ function.
    It takes a source code as input and generates the __main__ function 
    at the bottom of the source code.
    
    Args:
        source (str, optional): The source code in which 
        the __main__ will be generated. Defaults to "".
    """         
    def __init__(self, source=""):
        self._source = source
    
    def generate(self, text_widget:EditorCodeViewText=None) -> bool: 
        """
        Generate the __main__ and insert it at the bottom of the given `text_widget`.

        Args:
            text_widget (EditorCodeViewText, optional): The text widget to insert 
            the generated __main__ into. Set to `None` to not insert the generated 
            main function, this is useful for testing.
            
        Returns:
            bool: Returns True if the __main__ is generated, False otherwise.
        """      
        is_generated = False  

        main_line = self.__find_main_lineno(self._source) # Check if a __main__ already exists
        main_content = self.__get_main_content()
        
        if not main_line: # if not found
            is_generated = True
            if text_widget :  
                text_widget.insert("end", main_content)
                main_line = int(text_widget.index('end').split('.')[0]) - (main_content.count("\n") -1)
        if text_widget:
            text_widget.see(f"{main_line}.0")
            end_line = main_line + main_content.count("\n") - 1
            text_widget.select_lines(main_line, end_line if is_generated else main_line) # highlight the generated lines
            get_workbench().after(800, lambda: text_widget.select_lines(0,0)) # remove highlighting the lines after 800ms
        return is_generated
    
    def __find_main_lineno(self, text: str) -> int:
        """
        Returns the line numbers where the __main__ (and not commented) exists. Returns None if not found.
        """
        lines = text.splitlines()
        # use next() to get the first line number where the regex is found. Gets None if not found
        return next((i for i, line in enumerate(lines, 1) if re.search(_REGEX, line)), None)
    
    def __get_main_content(self) -> str:
        """ Returns the content of the __main__ to generate """
        return MAIN_TO_GENERATE

    def get_source(self) -> str:
        """ Returns the source code """
        return self._source
    
    def set_source(self, source: str):
        """ Sets the source code """
        self._source = source