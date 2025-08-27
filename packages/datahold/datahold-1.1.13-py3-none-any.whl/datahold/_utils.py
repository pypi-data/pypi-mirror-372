import abc
import inspect as ins
from types import FunctionType
from typing import *

__all__ = [
    "holdDecorator",
]

INITDOC: str = "This property represents the underlying data."


class holdDecorator:
    _funcnames: tuple[str]

    def __call__(self: Self, holdcls: type) -> type:
        self.setupDataProperty(holdcls=holdcls)
        self.setupInitFunc(holdcls=holdcls)
        name: str
        for name in self._funcnames:
            self.setupHoldFunc(holdcls=holdcls, name=name)
        abc.update_abstractmethods(holdcls)
        return holdcls

    def __init__(self: Self, *funcnames: str) -> None:
        self._funcnames = funcnames

    @classmethod
    def getAnnotationsDict(cls: type, sig: ins.Signature) -> dict:
        ans: dict = dict()
        p: ins.Parameter
        for p in sig.parameters.values():
            ans[p.name] = p.annotation
        ans["return"] = sig.return_annotation
        return ans

    @classmethod
    def getNonEmpty(cls: type, value: Any, backup: Any = Any) -> Any:
        if value is ins.Parameter.empty:
            return backup
        else:
            return value

    @classmethod
    def makeDataProperty(cls: type, *, datacls: type) -> property:
        def fget(self: Self) -> Any:
            return datacls(self._data)

        def fset(self: Self, value: Any) -> None:
            self._data = datacls(value)

        def fdel(self: Self) -> None:
            self._data = datacls()

        ans: property = property(
            fget=fget,
            fset=fset,
            fdel=fdel,
            doc=INITDOC,
        )
        return ans

    @classmethod
    def makeHoldFunc(cls: type, *, old: FunctionType) -> Any:
        def new(self: Self, *args: Any, **kwargs: Any) -> Any:
            data: Any = self.data
            ans: Any = old(data, *args, **kwargs)
            self.data = data
            return ans

        new.__doc__ = old.__doc__

        return new

    @classmethod
    def makeInitFunc(cls: type, *, datacls: type) -> FunctionType:
        def new(self: Self, *args: Any, **kwargs: Any) -> Any:
            self.data = datacls(*args, **kwargs)

        new.__doc__ = datacls.__init__.__doc__

        return new

    @classmethod
    def setupDataProperty(cls: type, holdcls: type) -> None:
        datacls: type = holdcls.__annotations__["data"]
        holdcls.data = cls.makeDataProperty(datacls=datacls)

    @classmethod
    def setupHoldFunc(cls: type, holdcls: type, *, name: str) -> None:
        datacls: type = holdcls.__annotations__["data"]
        old: Callable = getattr(datacls, name)
        new: FunctionType = cls.makeHoldFunc(old=old)
        new.__module__ = holdcls.__module__
        new.__name__ = name
        new.__qualname__ = holdcls.__qualname__ + "." + name
        cls.wrap(old=old, new=new, isinit=False)
        setattr(holdcls, name, new)

    @classmethod
    def setupInitFunc(cls: type, holdcls: type) -> None:
        datacls: type = holdcls.__annotations__["data"]
        new: FunctionType = cls.makeInitFunc(datacls=datacls)
        old: FunctionType = datacls.__init__
        new.__module__ = holdcls.__module__
        new.__name__ = "__init__"
        new.__qualname__ = holdcls.__qualname__ + ".__init__"
        cls.wrap(old=old, new=new, isinit=True)
        holdcls.__init__ = new

    @classmethod
    def wrap(
        cls: type,
        *,
        old: Callable,
        new: FunctionType,
        isinit: bool,
    ) -> ins.Signature:
        try:
            oldsig: ins.Signature = ins.signature(old)
        except ValueError:
            return
        params: list = list()
        a: Any
        n: int
        p: ins.Parameter
        q: ins.Parameter
        for n, p in enumerate(oldsig.parameters.values()):
            if n == 0:
                a = Self
            else:
                a = cls.getNonEmpty(p.annotation)
            q = p.replace(annotation=a)
            params.append(q)
        a = None if isinit else Any
        a = cls.getNonEmpty(oldsig.return_annotation, backup=a)
        new.__signature__ = ins.Signature(params, return_annotation=a)
        new.__annotations__ = cls.getAnnotationsDict(new.__signature__)
