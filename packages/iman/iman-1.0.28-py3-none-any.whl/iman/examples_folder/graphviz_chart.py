

#pip install graphviz

import graphviz

dot = graphviz.Digraph('round-table', comment='The Round Table') 

dot.node('A', 'Speech & Text Processing', color='red')  
dot.node('S', 'Speech Processing', color='blue')

dot.edge('A','S', color='blue' )

dot.render(directory='doctest-output', view=True)