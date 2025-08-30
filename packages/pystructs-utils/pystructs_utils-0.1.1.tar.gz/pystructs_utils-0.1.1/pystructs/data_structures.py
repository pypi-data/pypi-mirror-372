def deep_map(func, data):
    """Apply a function to all values in nested dicts/lists."""
    if isinstance(data, list):
        return [deep_map(func, x) for x in data]
    elif isinstance(data, dict):
        return {k: deep_map(func, v) for k, v in data.items()}
    else:
        return func(data)

def merge_deep(a, b):
    """Merge two dictionaries deeply."""
    result = dict(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_deep(result[k], v)
        else:
            result[k] = v
    return result

def pluck_path(data, path):
    """Extract nested value safely by path list."""
    for key in path:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data

def filter_deep(func, data):
    """Extract nested value safely by path list."""
    if isinstance(data, list):
        filtered_list = [filter_deep(func, x) for x in data]
        return [x for x in filtered_list if x is not None]
    elif isinstance(data, dict):
        filtered_dict = {k: filter_deep(func, v) for k, v in data.items()}
        return {k: v for k, v in filtered_dict.items() if v is not None and v != {} and v != []}
    else:
        return data if func(data) else None