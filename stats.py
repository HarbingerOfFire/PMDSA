import numpy as np

def sigma_clip(data, sigma=3.0, maxiters=5, axis=None, masked=False, return_mask=False):
    """
    Basic sigma clipping implementation.
    
    Parameters:
        data (array-like): Input array.
        sigma (float): Clipping threshold in standard deviations.
        maxiters (int): Maximum number of clipping iterations.
        axis (int or None): Axis along which to clip (None = flatten).
        masked (bool): Return masked array (if True) or normal array.
        return_mask (bool): If True, return the final clipping mask.

    Returns:
        array or (array, mask): Clipped array, optionally with mask.
    """
    data = np.asanyarray(data)
    mask = np.isnan(data)

    for _ in range(maxiters):
        if axis is None:
            d = data[~mask]
            if d.size == 0:
                break
            med = np.median(d)
            std = np.std(d)
            new_mask = np.abs(data - med) > sigma * std
        else:
            med = np.nanmedian(data, axis=axis)
            std = np.nanstd(data, axis=axis)
            med = np.expand_dims(med, axis)
            std = np.expand_dims(std, axis)
            new_mask = np.abs(data - med) > sigma * std
        
        new_mask |= np.isnan(data)
        if np.all(new_mask == mask):
            break
        mask = new_mask

    if masked:
        result = np.ma.masked_array(data, mask=mask)
    else:
        result = np.where(mask, np.nan, data)

    return (result, mask) if return_mask else result


def sigma_clipped_stats(data, sigma=3.0, maxiters=5, axis=None):
    """
    Mimics astropy.stats.sigma_clipped_stats.
    
    Returns:
        mean, median, std of clipped data.
    """
    clipped = sigma_clip(data, sigma=sigma, maxiters=maxiters, axis=axis, masked=True)
    mean = clipped.mean(axis=axis)
    median = np.ma.median(clipped, axis=axis)
    std = clipped.std(axis=axis)
    return float(mean), float(median), float(std) if np.isscalar(mean) else (mean, median, std)
import numpy as np

def sigma_clip(data, sigma=3.0, maxiters=5, axis=None, masked=False, return_mask=False):
    """
    Basic sigma clipping implementation.
    
    Parameters:
        data (array-like): Input array.
        sigma (float): Clipping threshold in standard deviations.
        maxiters (int): Maximum number of clipping iterations.
        axis (int or None): Axis along which to clip (None = flatten).
        masked (bool): Return masked array (if True) or normal array.
        return_mask (bool): If True, return the final clipping mask.

    Returns:
        array or (array, mask): Clipped array, optionally with mask.
    """
    data = np.asanyarray(data)
    mask = np.isnan(data)

    for _ in range(maxiters):
        if axis is None:
            d = data[~mask]
            if d.size == 0:
                break
            med = np.median(d)
            std = np.std(d)
            new_mask = np.abs(data - med) > sigma * std
        else:
            med = np.nanmedian(data, axis=axis)
            std = np.nanstd(data, axis=axis)
            med = np.expand_dims(med, axis)
            std = np.expand_dims(std, axis)
            new_mask = np.abs(data - med) > sigma * std
        
        new_mask |= np.isnan(data)
        if np.all(new_mask == mask):
            break
        mask = new_mask

    if masked:
        result = np.ma.masked_array(data, mask=mask)
    else:
        result = np.where(mask, np.nan, data)

    return (result, mask) if return_mask else result


def sigma_clipped_stats(data, sigma=3.0, maxiters=5, axis=None):
    """
    Mimics astropy.stats.sigma_clipped_stats.
    
    Returns:
        mean, median, std of clipped data.
    """
    clipped = sigma_clip(data, sigma=sigma, maxiters=maxiters, axis=axis, masked=True)
    mean = clipped.mean(axis=axis)
    median = np.ma.median(clipped, axis=axis)
    std = clipped.std(axis=axis)
    return float(mean), float(median), float(std) if np.isscalar(mean) else (mean, median, std)
import numpy as np

def sigma_clip(data, sigma=3.0, maxiters=5, axis=None, masked=False, return_mask=False):
    """
    Basic sigma clipping implementation.
    
    Parameters:
        data (array-like): Input array.
        sigma (float): Clipping threshold in standard deviations.
        maxiters (int): Maximum number of clipping iterations.
        axis (int or None): Axis along which to clip (None = flatten).
        masked (bool): Return masked array (if True) or normal array.
        return_mask (bool): If True, return the final clipping mask.

    Returns:
        array or (array, mask): Clipped array, optionally with mask.
    """
    data = np.asanyarray(data)
    mask = np.isnan(data)

    for _ in range(maxiters):
        if axis is None:
            d = data[~mask]
            if d.size == 0:
                break
            med = np.median(d)
            std = np.std(d)
            new_mask = np.abs(data - med) > sigma * std
        else:
            med = np.nanmedian(data, axis=axis)
            std = np.nanstd(data, axis=axis)
            med = np.expand_dims(med, axis)
            std = np.expand_dims(std, axis)
            new_mask = np.abs(data - med) > sigma * std
        
        new_mask |= np.isnan(data)
        if np.all(new_mask == mask):
            break
        mask = new_mask

    if masked:
        result = np.ma.masked_array(data, mask=mask)
    else:
        result = np.where(mask, np.nan, data)

    return (result, mask) if return_mask else result


def sigma_clipped_stats(data, sigma=3.0, maxiters=5, axis=None):
    """
    Mimics astropy.stats.sigma_clipped_stats.
    
    Returns:
        mean, median, std of clipped data.
    """
    clipped = sigma_clip(data, sigma=sigma, maxiters=maxiters, axis=axis, masked=True)
    mean = clipped.mean(axis=axis)
    median = np.ma.median(clipped, axis=axis)
    std = clipped.std(axis=axis)
    return float(mean), float(median), float(std) if np.isscalar(mean) else (mean, median, std)
