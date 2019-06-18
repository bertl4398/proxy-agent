from flask import Flask
from flask import render_template

import netifaces as ni
from netifaces import AF_INET, AF_INET6

from db import get_flow_all


app = Flask(__name__)
app.config.from_pyfile("config.cfg")

iface = app.config["IFACE"]
my_ip4 = ni.ifaddresses(iface)[AF_INET][0]['addr']
my_ip6 = ni.ifaddresses(iface)[AF_INET6][0]['addr']


@app.route("/")
def index():
    flows = get_flow_all()
    # print(flows.to_html(border=0, justify='left', classes="table"),
    #       file=open("templates/flows.html", "w"))
    return render_template("index.html", my_ip4=my_ip4, my_ip6=my_ip6)


if __name__ == "__main__":
    app.run(debug=True)
