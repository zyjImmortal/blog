from qiniu import put_data, Auth

access_key = "GoHjWCzP49AfTsmsqKe6oMZ15F2zshsvAUlYZ7L1"
secret_key = "ByNtAa-j6-BD-ydYdX6TNvXmP_XZq_8H2ZQKhn3I"
bucket_name = ""


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
    except Exception as e:
        raise e
    return ret.get("key", None)
