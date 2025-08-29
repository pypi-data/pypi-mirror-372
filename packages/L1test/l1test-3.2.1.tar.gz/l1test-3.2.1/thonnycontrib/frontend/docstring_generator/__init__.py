from .doc_generator import *

# Ceci est une implémentation de création d'un singleton pour L1TestRunner
_doc_generator: DocGenerator = None

def get_doc_generator(auto:bool) -> DocGenerator:
    """
    If there's no `DocGenerator` instance creates one and returns it,
    otherwise returns the current `DocGenerator` instance.
    """
    strategy = AutoGenerationStrategy() if auto else ManualGenerationStrategy()
    if not _doc_generator:
        return DocGenerator(strategy) 
    else:
        _doc_generator.set_strategy(strategy)
        return _doc_generator               