import math
import sys
import copy
import itertools
from threading import Thread
from Queue import Queue

class DataType(type):
    """Generic metaclass."""
    def __new__(meta, classname, bases, classDict):
        return type.__new__(meta, classname, bases, classDict)    

def struct(name, attributes):
    """Construct a class with given attributes (struct-like object).""" 
    def _init(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)        
    def _repr(self):
        items = ", ".join("%s=%s" % (k, getattr(self, k)) for k in attributes)
        return "<%s %s>" % (name, items)
    return DataType(name, (), 
        dict(__slots__=attributes, __init__=_init, __repr__=_repr))

def partition(pred, it):
    """Partition element in iterator in 2 lists (true_predicate, false_predicate)."""
    true_list, false_list = [], []
    for x in it:
        (true_list if pred(x) else false_list).append(x)
    return true_list, false_list

def compact(it, pred=bool):
    """Remove elements in iterator that do not match predicate."""
    return filter(pred, it)

def clone_struct(struct):
    """Return a clone (copy) of struct."""
    return copy.copy(struct)

def update_struct(struct, other_struct):
    """Update struct from other_struct attributes."""
    for key in other_struct.__slots__:
        setattr(struct, key, getattr(other_struct, key))
                         
def get_data_dict(data, accept=None, reject=None):
    """Get dictionary of (attribute, value) of struct."""
    return dict((k, getattr(data, k)) for k in data.__slots__ 
                if (not reject or k not in reject) and (not accept or k in accept))

def error(line):
    """Write line to standard error."""
    sys.stderr.write(str(line) + "\n")

def debug(line):
    """Write debug line."""
    error("--- %s " % line)

def first(it, pred=bool):
    """Return first element in iterator that matches the predicate."""
    return next(itertools.ifilter(pred, it), None) 
    
def remove_from_list(lst, items):
    """Return list with items."""
    return [x for x in lst if x not in items]
   
def threaded_function(function, *args, **kwargs):
    """Run function(*args, **kwargs) in a separate thread and return a reader."""
    def _thread(queue):
        while 1:
            value = function(*args, **kwargs)
            if not value:
                break
            queue.put(value)
    def _get(queue):
        if not queue.empty():
            return queue.get()    
    queue = Queue()
    thread = Thread(target=_thread, args=(queue,))
    thread.setDaemon(True)
    thread.start()
    return lambda: _get(queue)

def takeuntil(stream):
    """Read update structure (ends on empty line)."""
    lines = []
    while 1:
        line = stream.readline()
        if not line:
            return
        if not line.strip():
            break
        lines.append(line)
    return yaml.load("".join(lines))
