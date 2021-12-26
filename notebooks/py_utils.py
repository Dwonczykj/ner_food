from typing import Any, Generic, TypeVar, Callable

TRes = TypeVar("TRes")

def predicatePipe(objResult:TRes, predicate:Callable[[TRes],bool], fnToPassTo:Callable[[TRes,Any],Any], *otherFnArgs, returnIfnull=None):
    if predicate(objResult):
        return fnToPassTo(objResult, *otherFnArgs)
    else:
        return returnIfnull
    
def nullPipe(objResult:TRes, fnToPassTo:Callable[[TRes,Any],Any], *otherFnArgs, returnIfnull=None):
    return predicatePipe(objResult, lambda o: o is not None, fnToPassTo, returnIfnull=returnIfnull, *otherFnArgs)
    