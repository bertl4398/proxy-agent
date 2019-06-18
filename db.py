import redis

import pandas as pd
import numpy as np

from dateutil import parser

from flask import current_app as app


def get_flow_all():
    host = app.config["REDIS_HOST"]
    port = app.config["REDIS_PORT"]
    db = app.config["REDIS_DB"]

    r = redis.Redis(host=host, port=port, db=db)

    flow = list()

    for key in r.scan_iter():
        k = key.decode("utf-8")
        #  print(k)
        if k.startswith("flow/"):
            try:
                d = r.hgetall(key)
                d = {rk.decode("utf-8"): rv.decode("utf-8")
                     for rk, rv in d.items()}
                d["proto"] = k.split("/")[1]
                d["bytes"] = int(d["bytes"])
                d["frames"] = int(d["frames"])
                if "6" in d["proto"]:
                    d["src"] = k.split("/")[2].split(",")[0]
                    d["src_port"] = k.split("/")[2].split(",")[1]
                    d["dst_port"] = d["dst"].split(",")[1]
                    d["dst"] = d["dst"].split(",")[0]
                else:
                    d["src"] = k.split("/")[2].split(":")[0]
                    d["src_port"] = k.split("/")[2].split(":")[1]
                    d["dst_port"] = d["dst"].split(":")[1]
                    d["dst"] = d["dst"].split(":")[0]

                flow.append(d)
            except Exception as ex:
                print(ex)

    df = pd.DataFrame(flow)
    if flow:

        df["time"] = df["time"].apply(lambda t: parser.parse(t, fuzzy=True))

        table = pd.pivot_table(df, index=["src", "dst"], values=["frames", "bytes"],
                               aggfunc=np.sum)
        return table.sort_values("bytes", ascending=False)
    else:
        return df
