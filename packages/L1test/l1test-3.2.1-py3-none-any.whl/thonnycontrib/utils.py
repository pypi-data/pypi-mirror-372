from io import StringIO
from types import ModuleType
from thonny import get_workbench
from thonnycontrib.exceptions import CannotImportModuleException, CompilationError
from .properties import BACKEND_COMMAND 
from .environement_vars import *
import os, re, ast, traceback, textwrap, tkinter as tk
import thonny
from thonny.editors import EditorCodeViewText
from .i18n.languages import tr

def wrap(string:str, length=8, break_long_words=False):   
    """Wrap a text using the `wraptext` module.

    Args:
        string (str): the string to wrap.
        length (int, optional): the min length from which the string will be wrapped. Defaults to 8.
        break_long_words (bool, optional): if False the entire words will not be wrapped
                                        if the words lentgh is more that the given length. Defaults to False.
        separator (str, optional): the separator around which to wrap the filenames.
    Returns:
        str: the wrapped string.
    """
    return '\n'.join(textwrap.wrap(string, length, break_on_hyphens=False, break_long_words=break_long_words))


def create_node_representation(node:ast.AST):
    """
    Returns the node representation. Especially, returns the prototype or the signature of the node.
    This function can only construct a string representation of the supported nodes. 
    The supported nodes are reported in ASTParser.py in the global variable SUPPORTED_TYPES.
    
    Even if unsupported node is given so just it's name is returned.
    
    Args: 
        node (ast.AST): The supported node 

    Returns:
        str: Return the string represantation of a node
    """
    arg_to_exclude = lambda arg: arg in ("self", "cls")
    if isinstance(node, ast.ClassDef):
        return "%s(%s)" % (node.name, ", ".join([base.id for base in node.bases]))
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "%s(%s)" % (node.name, ", ".join([a.arg for a in node.args.args if not arg_to_exclude(a.arg)]))
    else:
        return node.name

def remove_url_part(error_msg:str):
    """Removes the hyperlink section from the `error_msg`. The hyperlink
    contains the filename and line number. 
    
    This function is only used by the L1TestErrorView to show the details of
    an error as a normal text.

    Args:
        error_msg (str): the error message from which the hyperlink will
                        be removed.

    Returns:
        str: The new error message without hyperlink part.
    """
    return re.sub(r'(File .*,\s*line\s*\d*)(, .*)?', "", error_msg)

def replace_error_line(error:str, line_number:int):
    """Replace the line of the error to iven `line_number`

    Args:
        error (str): The error that probably contains the error line.
        line_number (int): the new line number of the error.

    Returns:
        str: the same error with a new error line number.
    """
    return re.sub(r'(?P<match>line) (\d+)', '\g<match> %s' % line_number, error)

def replace_filename(filename, error:str):
    """Replace the filename in the given error to the specified `filename`

    Args:
        filename (str): the new filename
        error (str): the error message

    Returns:
        str: the same error but with replaced filename.
    """
    # Anuler les backslash dans les chemins pour éviter les problèmes d'anulation inconnue notamment dans Windows (\U de C:\Users\...)
    filename_escaped = re.sub(r'\\', '\\\\\\\\', filename)
    return re.sub(r'"(<.*>)?"', '"%s"' % filename_escaped, error)


def format_filename_to_hyperlink(error_message:str):
    """
    Finds the filename and line number in the given error message 
    then creates the corresponding hyperlink leading to the right place in the code editor.
    
    If no filename and line number found so an empty string is returned
    
    Args:
        text (str): the error_message supposed containing the hyperlink.

    Returns:
        str: Returns a hyperlink in RST format. 
    """
    def extract_file_and_lineno(error):
        file_line = re.search(r'File\s*(.*),\s*line\s*(\d*)(.*)', error)
        return {
                "filename": file_line.group(1).replace("\"", ""), 
                "lineno": file_line.group(2),
                "complement": file_line.group(3)
            } if file_line else None
    
    extracted = extract_file_and_lineno(error_message)
    if extracted:
        if os.path.exists(extracted["filename"]):
            filename, lineno, comp = extracted["filename"], extracted["lineno"], extracted["complement"]
            url = "thonny-editor://" + escape(filename).replace(" ", "%20")
            if lineno is not None:
                url += "#" + str(lineno)
            # return the hyperlink format following the rst specification
            return "`File \"%s\", line %s%s <%s>`__\n" % (escape(filename), lineno, comp, url)
        else: 
            return ""
    else:
        return ""

def escape(s:str):
    return (
        s.replace("\\", "\\\\")
         .replace("*", "\\*")
         .replace("`", "\\`")
         .replace("_", "\\_")
         .replace("..", "\\..")
    )

import traceback
import re
from io import StringIO

def get_last_exception(exc_info:tuple):
    """
    Formats exception information provided by ~exc_info~.
    Extracts the last exception located in the last frame.
    
    Args:
        exc_info (tuple): The tuple must contain three elements: 
                        (type, value, traceback) as returned by sys.exc_info().
        with_details (bool): Set as True and some extra informations will be considered
                        while formatting the exception informations. Defaults to True.

    Returns:
        str: Returns a string containing a traceback message for the given ~exc_info~.
    """
    # Get a traceback message.
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    # la variable `content`` va contenir toute la trace liée à l'exception levée
    content = excout.getvalue()
    excout.close()

    # mais on en retire que la dernière frame qui indiquent l'exception renvoyée par l'éditeur thonny
    last_exception = __extract_last_exception(content.rstrip("\n"))
    
    # parfois Python inclut plusieurs lignes vides dans l'exception.
    last_exception = re.sub("\n+", "\n", last_exception)
    # On assure que tout ce qui procède la dernière exception est retiré
    return re.sub(r'.*(?=File.*)', "", last_exception)

def __extract_last_exception(traceback_content:str):
    """Extract the last exception from the traceback frames,

    Args:
        content (str): The returned traceback as string.

    Returns:
        str: The lines representing the compilation error 
    """
    # splitted va contenir toutes les ligne de la traceback
    splitted = traceback_content.split("\n")
    keyword = "File"
    last_frame_index = 0
    
    # On veut pas afficher les frames du backend sur thonny, c'est inutile et illisible.
    frames_to_exclude = ["cpython_backend", os.path.join("thonny", "backend")]
    
    # on filtre par le mot "File" pour récupérer la dernière Frame.
    # C'est la dernière frame qui contient l'erreur survenu du script de thonny 
    # On veut pas, évidement, afficher toute la trace contenant les exceptions levées par l1test backend.
    for i in range(len(splitted)):
        frame = splitted[i]
        if keyword in frame :    
            last_frame_index = i
            
    # last_frame contient le nom du fichier et le détail de l'erreur              
    last_frame = splitted[last_frame_index:] 
    # Le nom du fichier de la dernière frame est à la position 0
    last_frame_file = last_frame[0]
    
    # Dans le cas de l'interuption du programme par un <Control+c>, 
    # la dernière frame contiendra une exception levée par le backend thonny.
    # En l'occurrence, on doit pas afficher toute la frame, mais juste le message renvoyé.
    # En général, on évite d'afficher les frames survenue du backend thonny.
    for frame_to_exclude in frames_to_exclude: 
        if frame_to_exclude in last_frame_file:
            last_frame_index = -1    
            
    # last_frame[-1] -> contient le message de l'exception de la frame          
    return last_frame[-1] if last_frame_index < 0 else "\n".join(last_frame).strip()

def get_module_name(filename:str):
    """
    Gets the module name from the specified filename.
    This function simply gets the basename of the filename, then removes 
    the ".py" extension. 

    Args:
        filename (str): an absolute path

    Returns:
        str: the module name of the given filename.
    """
    return  get_basename(filename, "py")

def get_basename(filename:str, extension:str="*"):
    """
    Gets the module name from the specified filename.
    This function simply gets the basename of the filename, then removes 
    the given extension. 

    Args:
        filename (str): an absolute path
        extension (str): the extension to remove from the filename. 
        Extension can be a regex. Use '*' to remove all extensions.

    Returns:
        str: the basename of the given filename without the given extension.
    """
    return re.sub(r'.'+extension, "", os.path.basename(filename))
   
def import_module(filename:str) -> ModuleType:
    """
    Import a module from a given filename. 
    The ~filename~ can be also the absolute path of a file.
    
    This function can raise an exception if the imported module 
    contains a compilation error. You should catch it somewhere.
    
    Args:
        filename (str): The filename(or the absolute path) of a file

    Returns:
        ModuleType: Returns the corresponding module of the given file.
        
    Raises: 
        CannotImportModuleException: if the filename cannot be imported by the 
        importlib module.
        CompilationError: any other exception related to a compilation error.
    """
    import importlib.util as iu, os, sys
    
    # import the module specification. 
    # To learn more about ModuleSpec `https://peps.python.org/pep-0451/`    
    module_name = get_module_name(filename)
    spec = iu.spec_from_file_location(module_name, filename)
    if not spec: 
        if not filename.endswith(".py"):
            msg_error = tr("The file \"%s\" cannot be imported.\n\n" + 
                           "Please, be sure that the extension of the file is `.py`") % filename 
        else:
            msg_error = tr("Cannot found the file `%s`") %filename 
        msg_error = tr("Error when importing the module \"%s\":\n") % module_name + msg_error
        raise CannotImportModuleException(msg_error)
    
    imported_source = iu.module_from_spec(spec)
    
    workingdir = os.path.split(imported_source.__file__)
    if (len(workingdir) > 0):
        basedir = workingdir[0]
        dirs = get_all_parent_directories(basedir)
        
        # ajout des packages parents au sys.path
        # on fait ça parce que on veut assurer les imports 
        # des fichiers contenant dans les packages parents
        [sys.path.append(path) for path in dirs]
        
        # ajout des sous packages au sys.path 
        # pour assurer les imports des fichiers contenant dans les sous packages
        sub_packages = get_sub_directories(basedir)
        [sys.path.append(basedir + os.sep + path) for path in sub_packages]
  
    try:
        # This line can raise an exception if the module contains compilation errors,
        # or if the module imports non existed modules
        spec.loader.exec_module(imported_source) 
        return imported_source
    except BaseException as e:
        # the compilation error is catched and raised as a CompilationError
        # and the evaluation is interrupted(because we cannot parse a content
        # with compilation errors).
        error_info = sys.exc_info()
        formatted_error = get_last_exception(error_info)
        raise CompilationError(formatted_error) 

def get_all_parent_directories(dir_path:str):
    """
    For a given path of a directory returns all the parents directory from that path.
    
    Examples:
    >>> get_all_parent_directories('/home/stuff/src')
    ['/home', '/home/stuff', '/home/stuff/src']
    """
    import os
    
    if dir_path is None:
        return []
    
    dirs = dir_path.split(os.sep)
    m = ""
    res = []
    for e in dirs[1:]:
        m += os.sep + e  
        res.append(m)
    return res

def get_sub_directories(package_path:str):
    """
        Get all sub-packages of a given package(param). 
    """
    from setuptools import find_packages
    return [p.replace(".", os.sep) for p in find_packages(package_path)]

def get_focused_writable_text():
    """
    Returns the focused text

    Returns:
        Widget: A widget Object if there's a focused area in the editor
        None : if no focused area exists in the editor
    """
    from thonny.editors import EditorCodeViewText
    widget = get_workbench().focus_get()
    # In Ubuntu when moving from one menu to another, this may give None when text is actually focused
    if isinstance(widget, EditorCodeViewText) and (
        not hasattr(widget, "is_read_only") or not widget.is_read_only()
    ):
        return widget
    else:
        return None
    
def get_selected_line(text_widget: EditorCodeViewText, only_lineno=True) -> int | tuple[int, int]:
    """
    Get the number of the selected line in the text editor. If only_lineno is True, 
    get only the line number.
    
    Note: Before using this method you should check if several lines are selected
    by invoking the method `assert_one_line_is_selected()` located in this file.
    
    Args:
        text_widget (Widget): The text selected in the text editor. 
                    The value of this parameter must be the result 
                    of invoking the get_focused_writable_text() method. 
        only_lineno (bool): If True, only the number of the selected line is returned.
    Returns:
        int | tuple[int, int]: Returns (lineno, column). If `only_lineno` is True, 
        returns only lineno.
    """
    # A text is selected in the editor => can't tell the exact line of the test to run
    lineno, column = map(int, text_widget.index(tk.INSERT).split("."))
    return lineno if only_lineno else (lineno, column)

def assert_one_line_is_selected() -> bool:
    """
    Returns True if only one line is selected, otherwise an exception is raised.
    """
    text = get_focused_writable_text()
    if text :
        return len(text.tag_ranges("sel")) == 0
    return False
        
def add_random_suffix(word):
    """Add a random suffix to the given word.
     
    The suffix is added in the following format 'word_suffix'. An underscore separates the two words.
    The suffix is assumed to be long(more than 9 caracters).
    
    Args:
        word (str): A word.

    Returns:
        str: Returns the given word with a random suffix appended after an underscore.
    """
    import string
    from random import shuffle, randint
    divider = "_"
    alphabet = list(string.ascii_lowercase + string.ascii_uppercase)
    
    # Divide by three to avoid the first index being so close to the last index.
    # The first index should be smaller than the last index, so we can have a long suffix.
    first_index = randint(0, len(alphabet)//3) 
    last_index = randint(len(alphabet)//2, len(alphabet)-1)
    
    shuffle(alphabet) 
    suffix = "".join(alphabet[first_index: last_index])
    return word + divider + suffix

def get_font_family_option(option="editor_font_family") -> str:
    """Retrieves the value of the "font family" option from the "options" menu.

    Returns:
        str: The value of the setted font family.
    """
    option = option if option else "editor_font_family"
    return thonny.get_workbench().get_option("view.%s" % option)

def get_font_size_option():
    """Retrieves the value of the "font size" option from the "options" menu.

    Returns:
        int: The value of the setted font size.
    """
    workbench = thonny.get_workbench()
    return workbench._guard_font_size(workbench.get_option("view.editor_font_size"))

def get_image_path(basename:str):
    """Get the absolute path to the image in the /img directory

    Args:
        basename (str): just the name of the file inluding it's extension. 
        For example: "icon.png"

    Returns:
        str: the absolute path to the image located in the /img directory
    """
    parent = os.path.dirname(__file__) # il faut remonter au niveau du package thonnycontrib pour trouver le dossier /img
    return os.path.join(os.path.abspath(parent), "img", basename)

def get_photoImage(image_name:str):
    """Returns a PhotoImage object from the given image path.

    Args:
        image_name (str): The basename of the image with its extension. 
        The image must be located in the "/img" directory.   
    Returns:
        PhotoImage: A PhotoImage object.
    """
    icon_path = get_image_path(image_name)
    return tk.PhotoImage(name=get_basename(icon_path), file=icon_path)

def send_current_state(state:str, command_name=BACKEND_COMMAND, **options):
    """
    Sends the given state with given arg to the front(L1TestRunner).

    Args:
        state (str): The current state to send.
        command_name (str, optional): The name of the command. Default is BACKEND_COMMAND.
        **options: Other options to include in the message.

    Raises:
        AssertionError: If the backend is not initialized.
    """
    from thonny.common import InlineResponse
    import thonnycontrib.backend.l1test_backend
    backend = thonnycontrib.backend.l1test_backend.BACKEND
    assert backend != None
    backend.send_message(InlineResponse(command_name=command_name, state=state, **options))

def clear_env_vars(*vars):
    """
    Clears the environnement variables.
    """
    for var in vars:
        os.environ.pop(var, None)
        
def format_to_string(value_to_format):
    """ 
    Returns a String no matter what.
    
    If valueToFormat was a string, returns it between single quotes.
        (specifically, if valueToFormat is the empty string, the return will be "\'\'", ie a string of length 2 made up of two single quotes)
    Otherwise, returns valueToFormat as a string (without additionnal quotes).
    """
    if isinstance(value_to_format, str):
        return "'%s'" % value_to_format
    else:
        return str(value_to_format)