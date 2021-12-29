# pylisting
Tools for working with Python source code listings.

This package was created to facilitate the following workflow:
1. Write some code in a Jupyter notebook.
2. Export that code to a Python file. (This can be accomplished with `jupyter nbconvert --to python your_jupyter_notebook.ipynb`)
3. Run the Python file and annotate every line with what gets written to stdout and stderr. (This is accomplished using the pylisting-annotate command.)
4. Split the annotated file into individual files, one for each cell in the original Jupyter notebook. (This is accomplished using the pylisting-split command.)
5. Embed the annotated code from various cells in a LaTeX document using the listings package.
