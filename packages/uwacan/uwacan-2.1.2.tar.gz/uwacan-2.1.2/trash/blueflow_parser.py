def blueflow(path, unit_brackets='[]'):
    if os.path.splitext(path)[1] == '.xlsx':
        raise NotImplementedError('Extracting blueflow data from xlsx not yet implemented')

    with open(path, 'r') as file:
        header = file.readline().strip().split(',')
        for time_idx, colname in enumerate(header):
            if 'time' in colname.lower():
                break
        else:
            raise ValueError('No timestamps in blueflow data')
        del header[time_idx]

        labels = []
        units = []

        for h in header:
            label, unit = h.split(unit_brackets[0])
            labels.append(label.strip().lower().replace(' ', '_'))
            units.append(unit.strip(' ' + unit_brackets))

        data = [[] for _ in range(len(header))]
        times = []
        for line in file:
            tmp = line.strip().split(',')
            time = pendulum.parse(tmp[time_idx])
            timestamp = time.timestamp()
            times.append(np.datetime64(int(timestamp * 1e9), 'ns'))
            del tmp[time_idx]
            for data_idx, value in enumerate(tmp):
                try:
                    value = float(value)
                except ValueError:
                    value = float('nan')
                data[data_idx].append(value)
    ds = xr.Dataset(
        data_vars={name: ('time', values, {'unit': unit}) for name, unit, values in zip(labels, units, data)},
        coords={'time': times}
    )
    return ds
