from decimal import Decimal
import json
from shared_utils.gcs_helper import check_if_file_exists, upload_to_gcs, download_from_gcs

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def get_posted_memos_file(geo_region, file_prefix,  memo_file, gcs_bucket):
    key = f"{file_prefix}/{geo_region}_{memo_file}"
    local_file = memo_file

    if not check_if_file_exists(gcs_bucket, key):
        upload_to_gcs(local_file, gcs_bucket, key)

    download_from_gcs(gcs_bucket, key, local_file)

def update_posted_memos_file(geo_region, file_prefix, memo_file, gcs_bucket):
    key = f"{file_prefix}/{geo_region}_{memo_file}"
    local_file = memo_file
    upload_to_gcs(local_file, gcs_bucket, key)
