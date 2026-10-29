# traceback_demo.py: read a traceback from the bottom up
def get_model(config):
    return config["model"]


def start_agent(config):
    model = get_model(config)
    print("starting with", model)


start_agent({"temperature": 0.2})
