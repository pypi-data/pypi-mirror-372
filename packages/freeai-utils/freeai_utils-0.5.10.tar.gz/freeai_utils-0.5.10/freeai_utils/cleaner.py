import os
from typing import List, Tuple, Union

class Cleaner: #this class first created is due to the gttS doesnt delete the .mp3 100% each time when interrupt in a multiprocessing 
    def __init__(self, directory : Union[str, None] = None):
        if directory is None:
            self._dir = os.path.dirname(os.path.abspath(__file__))
        else: self._dir = directory
        
        if type(self._dir) is not str:
            raise TypeError(f"the directory must be str type in order to proceed")
        
        if not os.path.exists(self._dir):
            raise FileNotFoundError(f"Your path doesn't exist")
        
    
    def remove_all_files_end_with(self, ends_with : str = None) -> Tuple[List[str], int]:
        """
        Removes all files in a directory that end with a specified string.\n
        Returns a tuple containing a list of the paths of the removed files and an integer count of how many files were deleted.
        """
        counter : int = 0
        paths : List[str] = []
        
        if type(ends_with) is not str or (isinstance(ends_with, str) and not ends_with.startswith('.')) or len(ends_with) < 2:
            raise TypeError(f"The 'ends_with' argument must be a string representing a file extension (e.g., '.txt'). You provided: {ends_with!r}")
        
        for root, _, files in os.walk(self._dir):
            for file in files:
                file_path = os.path.join(root, file).replace('\\', '/')  # normalize path
                if file.lower().endswith(ends_with):
                    counter += 1
                    paths.append(file_path)
                    os.remove(file_path)
        
        return paths, counter
        
if __name__ == "__main__":
    cleaner = Cleaner()
    print(cleaner.remove_all_files_end_with('.png'))