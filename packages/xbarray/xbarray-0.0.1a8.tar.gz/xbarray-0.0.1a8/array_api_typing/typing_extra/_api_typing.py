from typing import Protocol, TypeVar, Optional, Any, Tuple, Union, Type, TypedDict, Literal, Sequence, overload, Callable
from abc import abstractmethod
from array_api_typing.typing_compat._api_typing import ArrayAPINamespace as ArrayAPICompatNamespace, _NAMESPACE_ARRAY, _NAMESPACE_DEVICE, _NAMESPACE_DTYPE
from array_api_typing.typing_compat._array_typing import SetIndex, GetIndex
from ._at import AtResult

try:
    from array_api_extra._lib._at import Undef
except ImportError:
    from enum import Enum
    class Undef(Enum):
        UNDEF = 0

class ArrayAPINamespace(ArrayAPICompatNamespace[_NAMESPACE_ARRAY, _NAMESPACE_DEVICE, _NAMESPACE_DTYPE], Protocol[_NAMESPACE_ARRAY, _NAMESPACE_DEVICE, _NAMESPACE_DTYPE]):
    """
    From the array_api_extra
    https://github.com/data-apis/array-api-extra/blob/main/src/array_api_extra/_lib/_at.py
    """
    @abstractmethod
    def at(
        self,
        x: _NAMESPACE_ARRAY,
        idx : Union[SetIndex, Undef] = Undef.UNDEF,
        /
    ) -> "AtResult[_NAMESPACE_ARRAY]":
        """
        Returns an object that provides methods for elementwise operations
        on the array `x` using the `at` API.
        """
        pass

    """
    Utility Functions
    https://github.com/data-apis/array-api-extra/blob/main/src/array_api_extra/_lib/_funcs.py
    """
    @overload
    def apply_where(
        self,
        cond: _NAMESPACE_ARRAY,
        args: Union[_NAMESPACE_ARRAY, Tuple[_NAMESPACE_ARRAY, ...]],
        f1: Callable[..., _NAMESPACE_ARRAY],
        f2: Callable[..., _NAMESPACE_ARRAY],
        /,
    ) -> _NAMESPACE_ARRAY: 
        """
        Run one of two elementwise functions depending on a condition.

        Equivalent to ``f1(*args) if cond else fill_value`` performed elementwise
        when `fill_value` is defined, otherwise to ``f1(*args) if cond else f2(*args)``.

        Parameters
        ----------
        cond : array
            The condition, expressed as a boolean array.
        args : Array or tuple of Arrays
            Argument(s) to `f1` (and `f2`). Must be broadcastable with `cond`.
        f1 : callable
            Elementwise function of `args`, returning a single array.
            Where `cond` is True, output will be ``f1(arg0[cond], arg1[cond], ...)``.
        f2 : callable, optional
            Elementwise function of `args`, returning a single array.
            Where `cond` is False, output will be ``f2(arg0[cond], arg1[cond], ...)``.
            Mutually exclusive with `fill_value`.
        fill_value : Array or scalar, optional
            If provided, value with which to fill output array where `cond` is False.
            It does not need to be scalar; it needs however to be broadcastable with
            `cond` and `args`.
            Mutually exclusive with `f2`. You must provide one or the other.

        Returns
        -------
        Array
            An array with elements from the output of `f1` where `cond` is True and either
            the output of `f2` or `fill_value` where `cond` is False. The returned array has
            data type determined by type promotion rules between the output of `f1` and
            either `fill_value` or the output of `f2`.

        Notes
        -----
        ``xp.where(cond, f1(*args), f2(*args))`` requires explicitly evaluating `f1` even
        when `cond` is False, and `f2` when cond is True. This function evaluates each
        function only for their matching condition, if the backend allows for it.

        On Dask, `f1` and `f2` are applied to the individual chunks and should use functions
        from the namespace of the chunks.

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx
        >>> a = xp.asarray([5, 4, 3])
        >>> b = xp.asarray([0, 2, 2])
        >>> def f(a, b):
        ...     return a // b
        >>> xpx.apply_where(b != 0, (a, b), f, fill_value=xp.nan)
        array([ nan,  2., 1.])
        """
    
    @overload
    def apply_where(
        self,
        cond: _NAMESPACE_ARRAY,
        args: Union[_NAMESPACE_ARRAY, Tuple[_NAMESPACE_ARRAY, ...]],
        f1: Callable[..., _NAMESPACE_ARRAY],
        f2: Callable[..., _NAMESPACE_ARRAY],
        /,
        *,
        fill_value: Optional[Union[_NAMESPACE_ARRAY, float, int, complex]] = None,
    ) -> _NAMESPACE_ARRAY: 
        pass

    @abstractmethod
    def atleast_nd(
        self,
        x: _NAMESPACE_ARRAY,
        /,
        *,
        ndim: int,
    ) -> _NAMESPACE_ARRAY:
        """
        Recursively expand the dimension of an array to at least `ndim`.

        Parameters
        ----------
        x : array
            Input array.
        ndim : int
            The minimum number of dimensions for the result.

        Returns
        -------
        array
            An array with ``res.ndim`` >= `ndim`.
            If ``x.ndim`` >= `ndim`, `x` is returned.
            If ``x.ndim`` < `ndim`, `x` is expanded by prepending new axes
            until ``res.ndim`` equals `ndim`.

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx
        >>> x = xp.asarray([1])
        >>> xpx.atleast_nd(x, ndim=3, xp=xp)
        Array([[[1]]], dtype=array_api_strict.int64)

        >>> x = xp.asarray([[[1, 2],
        ...                  [3, 4]]])
        >>> xpx.atleast_nd(x, ndim=1, xp=xp) is x
        True
        """
        pass
    
    @abstractmethod
    def broadcast_shapes(
        self,
        *shapes : Tuple[Optional[float], ...]
    ) -> Tuple[Optional[float], ...]:
         """
        Compute the shape of the broadcasted arrays.

        Duplicates :func:`numpy.broadcast_shapes`, with additional support for
        None and NaN sizes.

        This is equivalent to ``xp.broadcast_arrays(arr1, arr2, ...)[0].shape``
        without needing to worry about the backend potentially deep copying
        the arrays.

        Parameters
        ----------
        *shapes : tuple[int | None, ...]
            Shapes of the arrays to broadcast.

        Returns
        -------
        tuple[int | None, ...]
            The shape of the broadcasted arrays.

        See Also
        --------
        numpy.broadcast_shapes : Equivalent NumPy function.
        array_api.broadcast_arrays : Function to broadcast actual arrays.

        Notes
        -----
        This function accepts the Array API's ``None`` for unknown sizes,
        as well as Dask's non-standard ``math.nan``.
        Regardless of input, the output always contains ``None`` for unknown sizes.

        Examples
        --------
        >>> import array_api_extra as xpx
        >>> xpx.broadcast_shapes((2, 3), (2, 1))
        (2, 3)
        >>> xpx.broadcast_shapes((4, 2, 3), (2, 1), (1, 3))
        (4, 2, 3)
        """
    
    def cov(
        self,
        m: _NAMESPACE_ARRAY,
        /,
    ) -> _NAMESPACE_ARRAY:
        """
        Estimate a covariance matrix.

        Covariance indicates the level to which two variables vary together.
        If we examine N-dimensional samples, :math:`X = [x_1, x_2, ... x_N]^T`,
        then the covariance matrix element :math:`C_{ij}` is the covariance of
        :math:`x_i` and :math:`x_j`. The element :math:`C_{ii}` is the variance
        of :math:`x_i`.

        This provides a subset of the functionality of ``numpy.cov``.

        Parameters
        ----------
        m : array
            A 1-D or 2-D array containing multiple variables and observations.
            Each row of `m` represents a variable, and each column a single
            observation of all those variables.
        xp : array_namespace, optional
            The standard-compatible namespace for `m`. Default: infer.

        Returns
        -------
        array
            The covariance matrix of the variables.

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx

        Consider two variables, :math:`x_0` and :math:`x_1`, which
        correlate perfectly, but in opposite directions:

        >>> x = xp.asarray([[0, 2], [1, 1], [2, 0]]).T
        >>> x
        Array([[0, 1, 2],
            [2, 1, 0]], dtype=array_api_strict.int64)

        Note how :math:`x_0` increases while :math:`x_1` decreases. The covariance
        matrix shows this clearly:

        >>> xpx.cov(x, xp=xp)
        Array([[ 1., -1.],
            [-1.,  1.]], dtype=array_api_strict.float64)

        Note that element :math:`C_{0,1}`, which shows the correlation between
        :math:`x_0` and :math:`x_1`, is negative.

        Further, note how `x` and `y` are combined:

        >>> x = xp.asarray([-2.1, -1,  4.3])
        >>> y = xp.asarray([3,  1.1,  0.12])
        >>> X = xp.stack((x, y), axis=0)
        >>> xpx.cov(X, xp=xp)
        Array([[11.71      , -4.286     ],
            [-4.286     ,  2.14413333]], dtype=array_api_strict.float64)

        >>> xpx.cov(x, xp=xp)
        Array(11.71, dtype=array_api_strict.float64)

        >>> xpx.cov(y, xp=xp)
        Array(2.14413333, dtype=array_api_strict.float64)
        """
    
    def create_diagonal(
        self,
        x: _NAMESPACE_ARRAY,
        /,
        *,
        offset: int = 0,
    ) -> _NAMESPACE_ARRAY:
        """
        Construct a diagonal array.

        Parameters
        ----------
        x : array
            An array having shape ``(*batch_dims, k)``.
        offset : int, optional
            Offset from the leading diagonal (default is ``0``).
            Use positive ints for diagonals above the leading diagonal,
            and negative ints for diagonals below the leading diagonal.
        xp : array_namespace, optional
            The standard-compatible namespace for `x`. Default: infer.

        Returns
        -------
        array
            An array having shape ``(*batch_dims, k+abs(offset), k+abs(offset))`` with `x`
            on the diagonal (offset by `offset`).

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx
        >>> x = xp.asarray([2, 4, 8])

        >>> xpx.create_diagonal(x, xp=xp)
        Array([[2, 0, 0],
            [0, 4, 0],
            [0, 0, 8]], dtype=array_api_strict.int64)

        >>> xpx.create_diagonal(x, offset=-2, xp=xp)
        Array([[0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [0, 4, 0, 0, 0],
            [0, 0, 8, 0, 0]], dtype=array_api_strict.int64)
        """
    
    def kron(
        self,
        a: _NAMESPACE_ARRAY,
        b: _NAMESPACE_ARRAY,
        /,
    ) -> _NAMESPACE_ARRAY:
        """
        Kronecker product of two arrays.

        Computes the Kronecker product, a composite array made of blocks of the
        second array scaled by the first.

        Equivalent to ``numpy.kron`` for NumPy arrays.

        Parameters
        ----------
        a, b : Array | int | float | complex
            Input arrays or scalars. At least one must be an array.
        xp : array_namespace, optional
            The standard-compatible namespace for `a` and `b`. Default: infer.

        Returns
        -------
        array
            The Kronecker product of `a` and `b`.

        Notes
        -----
        The function assumes that the number of dimensions of `a` and `b`
        are the same, if necessary prepending the smallest with ones.
        If ``a.shape = (r0,r1,..,rN)`` and ``b.shape = (s0,s1,...,sN)``,
        the Kronecker product has shape ``(r0*s0, r1*s1, ..., rN*SN)``.
        The elements are products of elements from `a` and `b`, organized
        explicitly by::

            kron(a,b)[k0,k1,...,kN] = a[i0,i1,...,iN] * b[j0,j1,...,jN]

        where::

            kt = it * st + jt,  t = 0,...,N

        In the common 2-D case (N=1), the block structure can be visualized::

            [[ a[0,0]*b,   a[0,1]*b,  ... , a[0,-1]*b  ],
            [  ...                              ...   ],
            [ a[-1,0]*b,  a[-1,1]*b, ... , a[-1,-1]*b ]]

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx
        >>> xpx.kron(xp.asarray([1, 10, 100]), xp.asarray([5, 6, 7]), xp=xp)
        Array([  5,   6,   7,  50,  60,  70, 500,
            600, 700], dtype=array_api_strict.int64)

        >>> xpx.kron(xp.asarray([5, 6, 7]), xp.asarray([1, 10, 100]), xp=xp)
        Array([  5,  50, 500,   6,  60, 600,   7,
                70, 700], dtype=array_api_strict.int64)

        >>> xpx.kron(xp.eye(2), xp.ones((2, 2)), xp=xp)
        Array([[1., 1., 0., 0.],
            [1., 1., 0., 0.],
            [0., 0., 1., 1.],
            [0., 0., 1., 1.]], dtype=array_api_strict.float64)

        >>> a = xp.reshape(xp.arange(100), (2, 5, 2, 5))
        >>> b = xp.reshape(xp.arange(24), (2, 3, 4))
        >>> c = xpx.kron(a, b, xp=xp)
        >>> c.shape
        (2, 10, 6, 20)
        >>> I = (1, 3, 0, 2)
        >>> J = (0, 2, 1)
        >>> J1 = (0,) + J             # extend to ndim=4
        >>> S1 = (1,) + b.shape
        >>> K = tuple(xp.asarray(I) * xp.asarray(S1) + xp.asarray(J1))
        >>> c[K] == a[I]*b[J]
        Array(True, dtype=array_api_strict.bool)
        """

    def nunique(
        self,
        x: _NAMESPACE_ARRAY,
        /,
    ) -> _NAMESPACE_ARRAY:
         """
        Count the number of unique elements in an array.

        Compatible with JAX and Dask, whose laziness would be otherwise
        problematic.

        Parameters
        ----------
        x : Array
            Input array.
        xp : array_namespace, optional
            The standard-compatible namespace for `x`. Default: infer.

        Returns
        -------
        array: 0-dimensional integer array
            The number of unique elements in `x`. It can be lazy.
        """
    
    def setdiff1d(
        self,
        x1: Union[_NAMESPACE_ARRAY, int, float, complex],
        x2: Union[_NAMESPACE_ARRAY, int, float, complex],
        /,
        *,
        assume_unique: bool = False,
    ) -> _NAMESPACE_ARRAY:
        """
        Find the set difference of two arrays.

        Return the unique values in `x1` that are not in `x2`.

        Parameters
        ----------
        x1 : array | int | float | complex | bool
            Input array.
        x2 : array
            Input comparison array.
        assume_unique : bool
            If ``True``, the input arrays are both assumed to be unique, which
            can speed up the calculation. Default is ``False``.
        xp : array_namespace, optional
            The standard-compatible namespace for `x1` and `x2`. Default: infer.

        Returns
        -------
        array
            1D array of values in `x1` that are not in `x2`. The result
            is sorted when `assume_unique` is ``False``, but otherwise only sorted
            if the input is sorted.

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx

        >>> x1 = xp.asarray([1, 2, 3, 2, 4, 1])
        >>> x2 = xp.asarray([3, 4, 5, 6])
        >>> xpx.setdiff1d(x1, x2, xp=xp)
        Array([1, 2], dtype=array_api_strict.int64)
        """

    def sinc(
        self,
        x: _NAMESPACE_ARRAY,
        /,
    ) -> _NAMESPACE_ARRAY:
        r"""
        Return the normalized sinc function.

        The sinc function is equal to :math:`\sin(\pi x)/(\pi x)` for any argument
        :math:`x\ne 0`. ``sinc(0)`` takes the limit value 1, making ``sinc`` not
        only everywhere continuous but also infinitely differentiable.

        .. note::

            Note the normalization factor of ``pi`` used in the definition.
            This is the most commonly used definition in signal processing.
            Use ``sinc(x / xp.pi)`` to obtain the unnormalized sinc function
            :math:`\sin(x)/x` that is more common in mathematics.

        Parameters
        ----------
        x : array
            Array (possibly multi-dimensional) of values for which to calculate
            ``sinc(x)``. Must have a real floating point dtype.
        xp : array_namespace, optional
            The standard-compatible namespace for `x`. Default: infer.

        Returns
        -------
        array
            ``sinc(x)`` calculated elementwise, which has the same shape as the input.

        Notes
        -----
        The name sinc is short for "sine cardinal" or "sinus cardinalis".

        The sinc function is used in various signal processing applications,
        including in anti-aliasing, in the construction of a Lanczos resampling
        filter, and in interpolation.

        For bandlimited interpolation of discrete-time signals, the ideal
        interpolation kernel is proportional to the sinc function.

        References
        ----------
        #. Weisstein, Eric W. "Sinc Function." From MathWorld--A Wolfram Web
        Resource. https://mathworld.wolfram.com/SincFunction.html
        #. Wikipedia, "Sinc function",
        https://en.wikipedia.org/wiki/Sinc_function

        Examples
        --------
        >>> import array_api_strict as xp
        >>> import array_api_extra as xpx
        >>> x = xp.linspace(-4, 4, 41)
        >>> xpx.sinc(x, xp=xp)
        Array([-3.89817183e-17, -4.92362781e-02,
            -8.40918587e-02, -8.90384387e-02,
            -5.84680802e-02,  3.89817183e-17,
                6.68206631e-02,  1.16434881e-01,
                1.26137788e-01,  8.50444803e-02,
            -3.89817183e-17, -1.03943254e-01,
            -1.89206682e-01, -2.16236208e-01,
            -1.55914881e-01,  3.89817183e-17,
                2.33872321e-01,  5.04551152e-01,
                7.56826729e-01,  9.35489284e-01,
                1.00000000e+00,  9.35489284e-01,
                7.56826729e-01,  5.04551152e-01,
                2.33872321e-01,  3.89817183e-17,
            -1.55914881e-01, -2.16236208e-01,
            -1.89206682e-01, -1.03943254e-01,
            -3.89817183e-17,  8.50444803e-02,
                1.26137788e-01,  1.16434881e-01,
                6.68206631e-02,  3.89817183e-17,
            -5.84680802e-02, -8.90384387e-02,
            -8.40918587e-02, -4.92362781e-02,
            -3.89817183e-17], dtype=array_api_strict.float64)
        """

    """
    Delegation functions
    https://github.com/data-apis/array-api-extra/blob/main/src/array_api_extra/_delegation.py
    """
    def isclose(
        a: Union[_NAMESPACE_ARRAY, int, float, complex],
        b: Union[_NAMESPACE_ARRAY, int, float, complex],
        *,
        rtol: float = 1e-05,
        atol: float = 1e-08,
        equal_nan: bool = False,
    ) -> _NAMESPACE_ARRAY:
        """
        Return a boolean array where two arrays are element-wise equal within a tolerance.

        The tolerance values are positive, typically very small numbers. The relative
        difference ``(rtol * abs(b))`` and the absolute difference `atol` are added together
        to compare against the absolute difference between `a` and `b`.

        NaNs are treated as equal if they are in the same place and if ``equal_nan=True``.
        Infs are treated as equal if they are in the same place and of the same sign in both
        arrays.

        Parameters
        ----------
        a, b : Array | int | float | complex | bool
            Input objects to compare. At least one must be an array.
        rtol : array_like, optional
            The relative tolerance parameter (see Notes).
        atol : array_like, optional
            The absolute tolerance parameter (see Notes).
        equal_nan : bool, optional
            Whether to compare NaN's as equal. If True, NaN's in `a` will be considered
            equal to NaN's in `b` in the output array.
        xp : array_namespace, optional
            The standard-compatible namespace for `a` and `b`. Default: infer.

        Returns
        -------
        Array
            A boolean array of shape broadcasted from `a` and `b`, containing ``True`` where
            `a` is close to `b`, and ``False`` otherwise.

        Warnings
        --------
        The default `atol` is not appropriate for comparing numbers with magnitudes much
        smaller than one (see notes).

        See Also
        --------
        math.isclose : Similar function in stdlib for Python scalars.

        Notes
        -----
        For finite values, `isclose` uses the following equation to test whether two
        floating point values are equivalent::

            absolute(a - b) <= (atol + rtol * absolute(b))

        Unlike the built-in `math.isclose`,
        the above equation is not symmetric in `a` and `b`,
        so that ``isclose(a, b)`` might be different from ``isclose(b, a)`` in some rare
        cases.

        The default value of `atol` is not appropriate when the reference value `b` has
        magnitude smaller than one. For example, it is unlikely that ``a = 1e-9`` and
        ``b = 2e-9`` should be considered "close", yet ``isclose(1e-9, 2e-9)`` is ``True``
        with default settings. Be sure to select `atol` for the use case at hand, especially
        for defining the threshold below which a non-zero value in `a` will be considered
        "close" to a very small or zero value in `b`.

        The comparison of `a` and `b` uses standard broadcasting, which means that `a` and
        `b` need not have the same shape in order for ``isclose(a, b)`` to evaluate to
        ``True``.

        `isclose` is not defined for non-numeric data types.
        ``bool`` is considered a numeric data-type for this purpose.
        """
    
    def pad(
        self,
        x: _NAMESPACE_ARRAY,
        pad_width: Union[int, Tuple[int, int], Sequence[Tuple[int, int]]],
        mode: Literal["constant"] = "constant",
        *,
        constant_values: Union[int, float, complex] = 0,
    ) -> _NAMESPACE_ARRAY:
        """
        Pad the input array.

        Parameters
        ----------
        x : array
            Input array.
        pad_width : int or tuple of ints or sequence of pairs of ints
            Pad the input array with this many elements from each side.
            If a sequence of tuples, ``[(before_0, after_0), ... (before_N, after_N)]``,
            each pair applies to the corresponding axis of ``x``.
            A single tuple, ``(before, after)``, is equivalent to a list of ``x.ndim``
            copies of this tuple.
        mode : str, optional
            Only "constant" mode is currently supported, which pads with
            the value passed to `constant_values`.
        constant_values : python scalar, optional
            Use this value to pad the input. Default is zero.
        xp : array_namespace, optional
            The standard-compatible namespace for `x`. Default: infer.

        Returns
        -------
        array
            The input array,
            padded with ``pad_width`` elements equal to ``constant_values``.
        """