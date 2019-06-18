import redis

import pandas as pd
import numpy as np
import netifaces as ni

from dateutil import parser
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE

from flask import Flask
from flask import render_template

app = Flask(__name__)

my_ip4 = ni.ifaddresses('eno2')[AF_INET][0]['addr']
my_ip6 = ni.ifaddresses('eno2')[AF_INET6][0]['addr']

def get_flow_all():
    r = redis.Redis(host='localhost', port=6379, db=0)

    flow = list()

    for key in r.scan_iter():
        k = key.decode("utf-8")
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
    df["time"] = df["time"].apply(lambda t: parser.parse(t, fuzzy=True))

    table = pd.pivot_table(df, index=["src", "dst"], values=["frames", "bytes"],
                           aggfunc=np.sum)
    return table.sort_values("bytes", ascending=False)

@app.route("/")
def index():
    flows = get_flow_all()
    print(flows.to_html(border=0, justify='left', classes="table"),
          file=open("templates/flows.html", "w"))
    return render_template("index.html", my_ip4=my_ip4, my_ip6=my_ip6)
