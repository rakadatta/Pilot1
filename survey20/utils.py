import random
from typing import List
import yaml
import os


def pick_with_a_probabilty(probabilities: List, rewards: List):
    """
    given a list of probabilities pick the rewards
    @Return: selected reward
    """
    # Ensure probabilities sum up to 1
    assert sum(probabilities) == 1.0, "Probabilities should sum up to 1"
    chosen_value = random.choices(rewards, weights=probabilities, k=1)[0]
    return chosen_value


def parse_yaml(filename: str):
    """
    parse the data yaml file, YAML is choosen because easy to operate for small data samples
    """
    assert os.path.exists(filename)
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
    return data["Experiments"]


def make_pie_charts():
    # not sure if this is needed here
    pass


experiment_name = "exp1"
dat_filename = os.path.dirname(__file__) + "data/survey1.yaml"
experiments_data = parse_yaml(dat_filename)
dd = experiments_data["exp1"]
#  series: [{
#  name: 'Share',
#  data: [
#  { name: 'Petrol', y: 938899 },
#  { name: 'Diesel', y: 1229600 },
#  { name: 'Electricity', y: 325251 },
#  { name: 'Other', y: 238751 }
#  ]
#  }]
#  });
data_left = []
data_right = []
for i in zip(dd["left_rewards"], dd["left_probs"]):
    data_left.append({"name": str(i[0]),"y": i[1]})

for i in zip(dd["right_rewards"], dd["right_probs"]):
    data_right.append({"name": str(i[0]),"y": i[1]})
left_series = [{"name":"name","data": data_left}]
import ipdb; ipdb.set_trace()
