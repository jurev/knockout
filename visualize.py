import graphviz as gv

HISTORY = ["__main__"]

graph = gv.Digraph(format='svg')

def monkeypatch(loader):
    load_module_orig = loader.load_module
    def load_module(self, fullname):
                
        if fullname in HISTORY:
            added = False
        else:
            HISTORY.append(fullname)
            graph.edge(HISTORY[-2], HISTORY[-1])
            added = True
        
        print HISTORY
        
        ret = load_module_orig(self, fullname)
        
        if added:
            del HISTORY[-1]       
        
        return ret
    loader.load_module = load_module
    

