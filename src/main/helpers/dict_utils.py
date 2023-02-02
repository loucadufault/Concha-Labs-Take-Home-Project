def filter_dict(dict_like, key_allow_list):
    return {k: dict_like.get(k) for k in key_allow_list if k in dict_like}