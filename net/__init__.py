import json
import logging
import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np

from dateutil import parser

from flask_redis import FlaskRedis


redis_client = FlaskRedis()
logger = logging.getLogger()


def get_flows():
    flow = list()
    for key in redis_client.scan_iter():
        k = key.decode("utf-8")
        if k.startswith("flow/"):
            try:
                d = redis_client.hgetall(key)
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
                logger.warning(ex)
                logger.warning(k)

    df = pd.DataFrame(flow)
    if flow:
        df["time"] = df["time"].apply(lambda t: parser.parse(t, fuzzy=True))
        # table = pd.pivot_table(df, index=["src", "dst"], values=["frames", "bytes"],
        #                        aggfunc=np.sum)
        # return table.sort_values("bytes", ascending=False)
    return df


def get_flows_chart(my_ip4, my_ip6):
    df = get_flows()
    df["source"] = df.src.map(str) + ":" + df.src_port.map(str)
    df["destination"] = df.dst.map(str) + ":" + df.dst_port.map(str)

    my_ip6 = my_ip6.rsplit("%")[0]
    df = df[(df["dst"] == my_ip4) | (df["dst"] == my_ip6)]
    fig = {'data': [{'x': df.source, 'y': df.bytes,
                     'text': df.destination,
                     'mode': 'markers', 'name': "current flows" }],
           'layout': {'xaxis': {'title': ''},
                      'yaxis': {'title': 'Bytes per last 5 seconds',
                                'type': 'log'}}}
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
