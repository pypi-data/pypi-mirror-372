def diff(x, t):
    """
    Compute the discrete derivative

    Input
    ----------
    x : list
    t : list
    Returns
    -------
    v : list
    """
    # Check input validity
    if not isinstance(x, list) or not isinstance(t, list):
        raise TypeError("Both inputs must be Python lists")
    if len(x) != len(t):
        raise ValueError("Both arrays must be of equal length")
    if len(x) < 2:
        raise ValueError("At least two values are needed")

    v = [None]  # derivative undefined for first point
    for k in range(1,len(x)):
        dx = x[k] - x[k-1]
        dt = t[k] - t[k-1]
        if dt == 0:
            raise ZeroDivisionError(f"Zero time difference at index {k}")
        v.append(dx / dt)
    return v
