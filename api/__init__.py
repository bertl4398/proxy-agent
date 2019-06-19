import time

from flask import jsonify
from flask_restful import Api, Resource

from net import get_flows
import config

api = Api(prefix=config.API_PREFIX)


class NetFlowAPI(Resource):
    def get(self):
        flows = get_flows()
        return jsonify(flows.to_dict(orient='records'))


# net flow endpoint
api.add_resource(NetFlowAPI, '/flows')
