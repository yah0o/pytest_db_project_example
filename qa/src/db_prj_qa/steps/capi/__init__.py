from np_cats_qa.steps.capi.commerce import CommerceCapiSteps

class CapiSteps(object):
    def __init__(self, request, app_id, amqp_url, contracts):
        self.commerce = CommerceCapiSteps(request, app_id, amqp_url, contracts)

