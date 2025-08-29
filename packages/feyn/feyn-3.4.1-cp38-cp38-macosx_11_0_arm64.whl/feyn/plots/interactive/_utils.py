def _get_ranges(model, data):
    inputs = model.inputs
    ranges = {}
    for i in model:
        if i.name in inputs:
            name = i.name
            if "cat" in i.fname:
                ranges[name] = data[name].unique()
            else:
                ranges[name] = (data[name].min(), data[name].max())
    return ranges
