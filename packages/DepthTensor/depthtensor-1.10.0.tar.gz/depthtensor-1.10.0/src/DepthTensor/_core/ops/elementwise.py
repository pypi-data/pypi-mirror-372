from typing import (
    Optional, 
    Union, 
    Any,
    Callable
)

from ...typing import (
    TensorLike, 
    DTypeLike, 
    Casting,
    Order, 
    ArrayLikeBool,
    ArrayLike,
    OperandLike,
    DeviceLike,
    Op_2in_1out_Protocol,
    Diff_2in_1out_Protocol,
    Func_2in_1out_Protocol,
    Op_1in_1out_Protocol,
    Diff_1in_1out_Protocol,
    Func_1in_1out_Protocol
)

from ..exceptions import (
    DeviceMismatch, DEVICE_MISMATCH_MSG,
    CuPyNotFound, CUPY_NOT_FOUND_MSG
)

from ..utils import (
    to_xp_array
)

import numpy as np
try:
    import cupy as cp
except (ImportError, ModuleNotFoundError):
    cp = None

###
###
###

def create_2in_1out(
    op: Op_2in_1out_Protocol,
    diff: Optional[Diff_2in_1out_Protocol]
) -> Func_2in_1out_Protocol:
    def func(
        x1: OperandLike,
        x2: OperandLike,
        *,
        device: DeviceLike = "cpu",
        in_place: bool = False,
        requires_grad: bool = True,
        **kwds: Any
    ) -> TensorLike:
        from ...tensor import Tensor
        is_tensor_op = False
        if isinstance(x1, Tensor) and isinstance(x2, Tensor):
            if not x1.is_device(x2.device):
                raise DeviceMismatch(DEVICE_MISMATCH_MSG)
            else:
                is_tensor_op = True 

        if is_tensor_op and isinstance(x1, Tensor):
            device_op = x1.device
        else:
            device_op = device

        a1, a2 = to_xp_array(x1, device=device_op), to_xp_array(x2, device=device_op)
        y = op(a1, a2, device=device, **kwds)
        
        if is_tensor_op and in_place and isinstance(x1, Tensor):
            x1.data = y
            return x1
        
        y_requires_grad = False
        prev = ()
        if isinstance(x1, Tensor):
            y_requires_grad = x1.requires_grad
            prev = (x1,)
        if isinstance(x2, Tensor):
            y_requires_grad = y_requires_grad or x2.requires_grad
            if len(prev) == 1:
                prev = (x1, x2)
            else:
                prev = (x2,)

        y = Tensor(y, device=device_op, prev=prev, requires_grad=y_requires_grad and requires_grad)
        if diff is None:
            return y
        else:
            if y.requires_grad:
                dx1, dx2 = diff(y, a1, a2)
                def backward() -> None:
                    if isinstance(x1, Tensor) and x1.requires_grad:
                        x1.grad += y.grad * dx1()
                    if isinstance(x2, Tensor) and x2.requires_grad:
                        x2.grad += y.grad * dx2()
                y.backward = backward
            return y
    return func

def create_1in_1out(
    op: Op_1in_1out_Protocol,
    diff: Optional[Diff_1in_1out_Protocol]
) -> Func_1in_1out_Protocol:
    def func(
        x: OperandLike,
        *,
        device: DeviceLike = "cpu",
        in_place: bool = False,
        requires_grad: bool = True,
        **kwds: Any
    ) -> TensorLike:
        from ...tensor import Tensor
        if isinstance(x, Tensor):
            device_op = x.device
        else:
            device_op = device

        a = to_xp_array(x, device=device_op)
        y = op(a, device=device, **kwds)
        
        y_requires_grad = False
        if isinstance(x, Tensor):
            if in_place:
                x.data = y
                return x
            y_requires_grad = x.requires_grad

        y = Tensor(y, device=device_op, prev=(x,), requires_grad=y_requires_grad and requires_grad)
        if diff is None:
            return y
        else:
            if y.requires_grad:
                dx = diff(y, a)
                def backward() -> None:
                    if isinstance(x, Tensor) and x.requires_grad:
                        x.grad += y.grad * dx()
                y.backward = backward
            return y
    return func

def wrapper_2in_1out(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    func_name: str,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    is_tensor_op = False
    if isinstance(x1, Tensor) and isinstance(x2, Tensor):
        if not x1.is_device(x2.device):
            raise DeviceMismatch(DEVICE_MISMATCH_MSG)
        else:
            is_tensor_op = True 
    #* Either tensor-tensor op or array-array op.

    #* If its tensor-tensor op, device is decided by x1.device, else, its by the device argument.
    if is_tensor_op and isinstance(x1, Tensor):
        device_op = x1.device
    else:
        device_op = device

    a1, a2 = to_xp_array(x1, device=device_op), to_xp_array(x2, device=device_op)
    if device_op == "cpu":
        if func_name == "matmul":
            y = getattr(np, func_name)(a1, a2, out=out, dtype=dtype, casting=casting, order=order, subok=subok)
        else:
            y = getattr(np, func_name)(a1, a2, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = getattr(cp, func_name)(a1, a2, out=out, dtype=dtype, casting=casting)

    if is_tensor_op and in_place and isinstance(x1, Tensor):
        x1.data = y
        return x1
    
    requires_grad = False
    prev = ()
    if isinstance(x1, Tensor):
        requires_grad = x1.requires_grad
        prev = (x1,)
    if isinstance(x2, Tensor):
        requires_grad = requires_grad or x2.requires_grad
        if len(prev) == 1:
            prev = (x1, x2)
        else:
            prev = (x2,)

    return Tensor(y, device=device_op, prev=prev, requires_grad=requires_grad)

def wrapper_1in_1out(
    x: OperandLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    func_name: str,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    if isinstance(x, Tensor):
        device_op = x.device
    else:
        device_op = device

    a = to_xp_array(x, device=device_op)
    if device_op:
        y = getattr(np, func_name)(a, out=out, dtype=dtype, where=where, casting=casting, order=order, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = getattr(cp, func_name)(a, out=out, dtype=dtype, casting=casting)

    requires_grad = False
    if isinstance(x, Tensor):
        if in_place:
            x.data = y
            return x
        requires_grad = x.requires_grad
    return Tensor(y, device=device_op, prev=(x,), requires_grad=requires_grad)

###
### Arithmetics
###

def add(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_2in_1out(x1, x2, out=out, func_name="add", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def subtract(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_2in_1out(x1, x2, out=out, func_name="subtract", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def multiply(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_2in_1out(x1, x2, out=out, func_name="multiply", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def matmul(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_2in_1out(x1, x2, out=out, func_name="matmul", device=device, in_place=in_place, casting=casting, order=order, dtype=dtype, subok=subok)

def divide(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_2in_1out(x1, x2, out=out, func_name="divide", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def power(
    x1: OperandLike, 
    x2: OperandLike, 
    /,
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_2in_1out(x1, x2, out=out, func_name="power", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)


def negative(
    x: OperandLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="negative", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def sign(
    x: OperandLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="sign", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def abs(
    x: OperandLike,
    /,
    out: Optional[Union[np.ndarray, Any]] = None, 
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[ArrayLikeBool, bool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="abs", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def clip(
    a: OperandLike,
    a_min: OperandLike,
    a_max: OperandLike,
    /,
    out: Optional[ArrayLike] = None,
    *,
    requires_grad: bool = False,
    device: DeviceLike = "cpu",
    where: Union[bool, ArrayLikeBool] = True,
    casting: Casting = 'same_kind',
    order: Order = 'K',
    dtype: Optional[DTypeLike] = None,
    subok: bool = True
) -> TensorLike:
    from ...tensor import Tensor
    is_tensor_op = False
    if isinstance(a, Tensor) and isinstance(a_min, Tensor) and isinstance(a_max, Tensor):
        if not (a.device == a_min.device == a_max.device): raise DeviceMismatch(DEVICE_MISMATCH_MSG)
        is_tensor_op = True

    if is_tensor_op and isinstance(a, Tensor):
        device_op = a.device
    else:
        device_op = device

    arr_a, arr_min, arr_max = to_xp_array(a, device=device_op), to_xp_array(a_min, device=device_op), to_xp_array(a_max, device=device_op)
    if device_op == "cpu":
        if out is None:
            y = np.clip(arr_a, arr_min, arr_max, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
        else:
            y = np.clip(arr_a, arr_min, arr_max, out=out, where=where, casting=casting, order=order, dtype=dtype, subok=subok)
    else:
        if cp is None: raise CuPyNotFound(CUPY_NOT_FOUND_MSG)
        y = cp.clip(arr_a, arr_min, arr_max, out=out)
    return Tensor(y, requires_grad=requires_grad)

###
### Exponents/Logarithms
###

def exp(
    x: OperandLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="exp", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def sqrt(
    x: OperandLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="sqrt", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def log(
    x: OperandLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="log", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

def square(
    x: OperandLike, 
    /, 
    out: Optional[Union[np.ndarray, Any]] = None,
    *,
    device: DeviceLike = "cpu",
    in_place: bool = False,
    where: Union[bool, ArrayLikeBool] = True, 
    casting: Casting = 'same_kind',
    order: Order = 'K', 
    dtype: Optional[DTypeLike] = None, 
    subok: bool = True
) -> TensorLike:
    return wrapper_1in_1out(x, out=out, func_name="square", device=device, in_place=in_place, where=where, casting=casting, order=order, dtype=dtype, subok=subok)

###
###
###

__all__ = [
    'add', 
    'subtract', 
    'multiply', 
    'matmul', 
    'divide',
    'power',
    'negative', 
    'sign', 
    'abs',
    'exp', 
    'sqrt', 
    'log', 
    'square',
    'clip',
    'create_2in_1out',
    'create_1in_1out'
]