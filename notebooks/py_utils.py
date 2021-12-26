from typing import Any, Generic, TypeVar, Callable

TRes = TypeVar("TRes")

def nullPipe(objResult:Generic[TRes], fnToPassTo:Callable[[TRes],Any], *otherFnArgs, returnIfnull=None):
    if objResult is not None:
        return fnToPassTo(objResult, *otherFnArgs)
    else:
        return returnIfnull