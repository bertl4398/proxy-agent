import os
import logging
import ipaddress

import netifaces as ni
from netifaces import AF_INET, AF_INET6

import config

from flask import Flask
from flask import render_template, request, redirect, url_for, flash

from api import api
from net import redis_client, get_flows_chart
from tasks.tasks import block_ip

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()])

logger = logging.getLogger()


def create_app():
    logger.info(f'Starting app in {config.APP_ENV} environment')
    app = Flask(__name__)
    app.config.from_object('config')

    api.init_app(app)
    redis_client.init_app(app)

    iface = app.config["IFACE"]
    my_ip4 = ni.ifaddresses(iface)[AF_INET][0]['addr']
    my_ip6 = ni.ifaddresses(iface)[AF_INET6][0]['addr']

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'GET':
            plot = get_flows_chart(my_ip4, my_ip6)
            return render_template('index.html', my_ip4=my_ip4, my_ip6=my_ip6,
                                   plot=plot)

        if request.form['submit'] == 'block':
            ip = request.form['ip']
            port = request.form['port']

            logger.debug("Block %s at port %s", ip, port)
            try:
                ipaddress.ip_address(ip); int(port)
                flash("Block {} at {}".format(ip, port), "warning")
                block_ip.delay(ip, port)
            except ValueError as err:
                flash("{}".format(err), "danger")
                logger.warning(err)

        if request.form['submit'] == 'redirect':
            src_ip = request.form['src_ip']
            src_port = request.form['src_port']
            dst_ip = request.form['dst_ip']
            dst_port = request.form['dst_port']

            logger.debug("Redirect %s:%s to %s:%s", src_ip, src_port,
                         dst_ip, dst_port)
            try:
                ipaddress.ip_address(src_ip); int(src_port)
                ipaddress.ip_address(dst_ip); int(dst_port)
                flash("Redirect {}:{} to {}:{}".format(src_ip, src_port,
                      dst_ip, dst_port), "warning")
            except ValueError as err:
                flash("{}".format(err), "danger")
                logger.warning(err)

        return redirect(url_for('index'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
