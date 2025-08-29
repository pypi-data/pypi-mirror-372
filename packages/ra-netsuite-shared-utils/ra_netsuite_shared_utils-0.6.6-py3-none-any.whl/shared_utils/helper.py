import datetime

def get_start_and_end_date():
    current_date = datetime.datetime.now()
    last_day_prev_month = current_date.replace(day=1) - datetime.timedelta(days=1)
    start_date = last_day_prev_month.replace(day=1).strftime('%Y-%m-%d')
    end_date = last_day_prev_month.strftime('%Y-%m-%d')

    return {"start_date": start_date, "end_date": end_date}

def get_posting_period_val(journal_date):
    date_parts = journal_date.split('-')
    year = date_parts[0]
    month = date_parts[1]
    date_key = f"{month}-{year}"
    date_object = datetime.datetime.strptime(date_key, "%m-%Y")
    return date_object.strftime("%b %Y")

def capitalize_first_letter(sentence):
    if not sentence:
        return ""
    return sentence[0].upper() + sentence[1:]

def get_missing_mappings(final_df, class_to_id_mapping, location_to_id_mapping):
    missing_mappings = {
        'CLASS': [],
        'LOCATION': []
    }
    seen_gl_class = set()
    seen_geo_region_name = set()

    for row in final_df:
        class_id = class_to_id_mapping.get(row['gl_class'], None)
        location_id = location_to_id_mapping.get(capitalize_first_letter(row['geo_region_name']), None)

        if class_id is None and row['gl_class'] not in seen_gl_class:
            missing_mappings['CLASS'].append(row['gl_class'])
            seen_gl_class.add(row['gl_class'])
        if location_id is None and row['geo_region_name'] not in seen_geo_region_name:
            missing_mappings['LOCATION'].append(row['geo_region_name'])
            seen_geo_region_name.add(row['geo_region_name'])

    return missing_mappings
