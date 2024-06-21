def organize_data_by_region(regions, data):
    organized_data = []
    for region in regions:
        region_data = {
            'label': region,
            'children': []
        }
        for entry in data:
            if entry['region'] == region:
                region_data['children'].append(entry)
        organized_data.append(region_data)
    return organized_data
