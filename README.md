# sokoban-and-machine-learning

This project is my undergraduate thesis. I implemented Machine Learning in the analysis of the logfile of the game Sokoban and use it
to predict one's math grades and Raven intelligence.

The codes are divided into three parts: reading the data, cleaning the data, and finally training the model. In addition, I also provide 
an appendix to solve the Sokoban model, which is based on code published on the internet (I'm sorry, I forget the source). 

The order to run the code is: The appendix -> Part I -> Part II -> Part III.

Languages used include Python (3.0+) and R. I recommend you install [anaconda](https://www.continuum.io/downloads), a data science platform including all the tools and packages we need.

To write code in Python, the IDE **Spyder** is highly recommended. It provides a matlab-like interface, and also interactive programming experience, which is very handy in data analysis. Meanwhile, Pycharm, Visual Studio Code and sublime text are also very good IDEs.

For R, **RStudio** is the most renowned IDE. There is no better choice.

This tutorial is written in **Jupyter Notebook**. It allows the combination of documents and interactive programming, which is perfectly suitable for tutorials. If you open this .ipynb file with Jupyter Notebook, you can also edit the code and meanwhile run it to see the result. When you are writing your own code or try to update this code, you may find it more convenient copying the code to a .py file using spyder.

All these tools can be installed via anaconda.

You may want to read tutorials for R and Python [here](https://github.com/FuZhiyu/sokoban-and-machine-learning/tree/master/tutorials). Besides the basics syntax of languages, you are also encouraged (or even required) to read documentations for packages such as scikit-learning in Python and data.table in R. I have collected some of them [here](https://github.com/FuZhiyu/sokoban-and-machine-learning/tree/master/tutorials/documentations). You can also get them easily on the internet or use "help".

In the folder "tutorial", I provide those codes in html and pdf format, which is more friendly to novices.

Besides, in the folder "read_game_log_file", I wrote a script "extract.py" to extract data from logfiles of four games: Gene Labs, Sokoban, London Tower and CTC.

Good luck.

