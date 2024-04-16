import json
import os
import random
import otree
import yaml
from otree.api import *
from typing import List

doc = """
In a common value auction game, players simultaneously bid on the item being
auctioned.<br/>
Prior to bidding, they are given an estimate of the actual value of the item.
This actual value is revealed after the bidding.<br/>
Bids are private. The player with the highest bid wins the auction, but
payoff depends on the bid amount and the actual value.<br/>
"""


def parse_yaml(filename: str):
    """
    parse the data yaml file, YAML is choosen because easy to operate for small data samples
    """
    assert os.path.exists(filename)
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
    return data["Experiments"]


class C(BaseConstants):
    NAME_IN_URL = "POTATO_SURVEY"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    name = models.StringField(label="Please enter your name")
    age = models.IntegerField(label="What is your age?", min=13, max=125)
    accumulated_sum = models.CurrencyField(initial=0, doc="value accumulated so far")
    prev_reward = models.CurrencyField(initial=0, doc="value accumulated so far")
    num_messages = models.IntegerField(initial=0)
    game_finished = models.BooleanField()


# PAGES
class Introduction(Page):
    form_model = "player"
    form_fields = ["name", "age"]


def pick_with_a_probabilty(probabilities: List, rewards: List):
    """
    given a list of probabilities pick the rewards
    @Return: selected reward
    """
    # Ensure probabilities sum up to 1
    assert sum(probabilities) == 1.0, "Probabilities should sum up to 1"
    chosen_value = random.choices(rewards, weights=probabilities, k=1)[0]
    return chosen_value


def reward_gained(experiment_id, key):
    exp_data = experiments_data[experiment_id]
    if key == "left":
        probs = "left_probs"
        rewards = "left_rewards"
        return pick_with_a_probabilty(exp_data[probs], exp_data[rewards])
    if key == "right":
        probs = "right_probs"
        rewards = "right_rewards"
        return pick_with_a_probabilty(exp_data[probs], exp_data[rewards])


# TODO: maybe move to initial one
dat_filename = os.path.dirname(__file__) + "/data/survey1.yaml"
experiments_data = parse_yaml(dat_filename)
max_num_messages = len(experiments_data)
num_messages = 0
all_experimanent_names = [exp for exp in experiments_data]


def get_next_experiment(signle_exp_data):
    data_left = []
    data_right = []
    for i in zip(signle_exp_data["left_rewards"], signle_exp_data["left_probs"]):
        data_left.append({"name": str(i[0])+"$", "y": i[1]})

    for i in zip(signle_exp_data["right_rewards"], signle_exp_data["right_probs"]):
        data_right.append({"name": str(i[0])+"$", "y": i[1]})

    print([{"name": "name", "data": data_left}])

    return dict(
        pieleft=json.dumps(data_left),
        pieright=json.dumps(data_right),
    )


class Survey(Page):
    @staticmethod
    def live_method(player, data):
        # the data recieved is either left button or right button
        print("the data is", data, type(data))
        player.num_messages += 1

        try:
            player.prev_reward = reward_gained(all_experimanent_names[player.num_messages - 1], key=data)
            player.accumulated_sum += player.prev_reward
        except:
            pass

        if player.num_messages >= max_num_messages:
            return {0: {"is_done": "game_finished", "prev_reward":player.prev_reward}}
        else:
            player.game_finished = False
            print(player.num_messages)
            curr_experiment_data = get_next_experiment(
                experiments_data[all_experimanent_names[player.num_messages]]
            )
            return {0: {"is_done": "not_game_finished", "exp_data":
                        curr_experiment_data, "prev_reward":player.prev_reward}}


class thanks(Page):
    form_model = "player"
    #  player.accumulated_sum = sum(rewards)
    form_fileds = ["accumulated_sum"]

    #  def vars_for_template(player: Player):
        #  player.accumulated_sum = sum(player.rewards)
        #  pass

    #  return dict(is_greedy=group.item_value - player.bid_amount < 0)
    # sum(rewards)
    # TODO: maybe writre the survey results into a text file
    #  @staticmethod
    #  def before_next_page(player: Player, timeout_happened):
    #  group = player.group
    #  player.item_value_estimate = generate_value_estimate(group)
    pass


#  class Results(Page):
#  @staticmethod
#  def vars_for_template(player: Player):
#  group = player.group

#  return dict(is_greedy=group.item_value - player.bid_amount < 0)


#  page_sequence = [Introduction, Survey, thanks]
page_sequence = [Survey, thanks]
