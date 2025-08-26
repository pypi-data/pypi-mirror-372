from decouple import config


def db_params_from_env(test=False):
    test_conf = "_TEST" if test else ""
    host = config(f"CLICKHOUSE_HOST{test_conf}", "localhost")
    database = config(f"CLICKHOUSE_DB{test_conf}", "test" if test else None)
    user = config(f"CLICKHOUSE_USER{test_conf}", None)
    password = config(f"CLICKHOUSE_PASSWORD{test_conf}", None)
    out = {"host": host}
    # we do not want to add the keys if the values are None so that the client can use default
    # values
    if database is not None:
        out["database"] = database
    if user is not None:
        out["user"] = user
    if password is not None:
        out["password"] = password
    return out
