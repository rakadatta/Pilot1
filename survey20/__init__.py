import json
import os
import random
from typing import List

import otree
import yaml
from otree.api import *

doc = """
TODO: add description here
this is a survey
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


#  def make_experiment_data(exp_name,result_name,clicked_name):
#  exp_name = models.StringField()
#  result_name = models.CurrencyField(initial=0)


class Player(BasePlayer):
    name = models.StringField(label="Please enter your name")
    age = models.IntegerField(label="What is your age?", min=13, max=125)
    accumulated_sum = models.CurrencyField(initial=0, doc="value accumulated so far")
    prev_reward = models.CurrencyField(initial=0, doc="value accumulated so far")
    num_messages = models.IntegerField(initial=0)
    game_finished = models.BooleanField()

    ##to log the data


class Survey1(ExtraModel):
    player = models.Link(Player)
    experiment_name = models.StringField()
    result_probabilty = models.FloatField()
    option_choosen = models.StringField()


# PAGES
class Introduction(Page):
    pass


class Introduction2(Page):
    pass


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
dat2_filename = os.path.dirname(__file__) + "/data/survey2.yaml"
experiments_data = parse_yaml(dat_filename)
experiments_data2 = parse_yaml(dat2_filename)
max_num_messages = len(experiments_data)
max_num_messages2 = len(experiments_data)
all_experimanent_names = [exp for exp in experiments_data]
all_experimanent_names2 = [exp for exp in experiments_data2]
# to eandomize the Experiments
random.shuffle(all_experimanent_names)
random.shuffle(all_experimanent_names2)


def get_next_experiment(signle_exp_data):
    data_left = []
    data_right = []
    for i in zip(signle_exp_data["left_rewards"], signle_exp_data["left_probs"]):
        data_left.append({"name": "$" + str(i[0]), "y": i[1]})

    for i in zip(signle_exp_data["right_rewards"], signle_exp_data["right_probs"]):
        data_right.append({"name": "$" + str(i[0]), "y": i[1]})

    print([{"name": "name", "data": data_left}])

    return dict(
        pieleft=json.dumps(data_left),
        pieright=json.dumps(data_right),
    )


def get_next_experiment2(signle_exp_data):
    return dict(
        premium=json.dumps(signle_exp_data["premium"]),
        initial_earning=json.dumps(signle_exp_data["initial_earning"]),
        loss=json.dumps(signle_exp_data["loss"]),
        loss_prob=json.dumps(signle_exp_data["loss_prob"]),
        loss_earning=json.dumps(signle_exp_data["final_earning"]),
    )


class Survey(Page):
    @staticmethod
    def live_method(player, data):
        # we send empty at the beginning
        if data == "load":
            curr_experiment_data = get_next_experiment(experiments_data[all_experimanent_names[0]])
            # we send empty at the beginning
            return {
                0: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }

        # the data recieved is either left button or right button
        player.num_messages += 1

        #  result_probabilty = models.FloatField()
        #  option_choosen = models.StringField()
        try:
            player.prev_reward = reward_gained(
                all_experimanent_names[player.num_messages - 1], key=data
            )
            player.accumulated_sum += player.prev_reward
            # data logging
            Survey1.create(
                player=player,
                experiment_name=all_experimanent_names[player.num_messages - 1],
                result_probabilty=player.prev_reward,
                option_choosen=data,
            )

        except:
            pass

        if player.num_messages >= max_num_messages:
            return {
                0: {
                    "is_done": "game_finished",
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }
        else:
            player.game_finished = False
            print(player.num_messages)
            curr_experiment_data = get_next_experiment(
                experiments_data[all_experimanent_names[player.num_messages]]
            )
            return {
                0: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }

class Survey2(Page):
    @staticmethod
    def live_method(player, data):
        # we send empty at the beginning
        if data == "load":
            curr_experiment_data = get_next_experiment(experiments_data[all_experimanent_names[0]])
            # we send empty at the beginning
            return {
                0: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }

        # the data recieved is either left button or right button
        player.num_messages += 1

        #  result_probabilty = models.FloatField()
        #  option_choosen = models.StringField()
        try:
            player.prev_reward = reward_gained(
                all_experimanent_names[player.num_messages - 1], key=data
            )
            player.accumulated_sum += player.prev_reward
            # data logging
            Survey1.create(
                player=player,
                experiment_name=all_experimanent_names[player.num_messages - 1],
                result_probabilty=player.prev_reward,
                option_choosen=data,
            )

        except:
            pass

        if player.num_messages >= max_num_messages:
            return {
                0: {
                    "is_done": "game_finished",
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }
        else:
            player.game_finished = False
            print(player.num_messages)
            curr_experiment_data = get_next_experiment(
                experiments_data[all_experimanent_names[player.num_messages]]
            )
            return {
                0: {
                    "is_done": "not_game_finished",
                    "exp_data": curr_experiment_data,
                    "prev_reward": player.prev_reward,
                    "option_selected": data,
                }
            }


class thanks(Page):
    form_model = "player"
    form_fileds = ["accumulated_sum"]
    pass


#  class Results(Page):
#  @staticmethod
#  def vars_for_template(player: Player):
#  group = player.group

#  return dict(is_greedy=group.item_value - player.bid_amount < 0)


page_sequence = [Introduction, Survey, Introduction2, thanks]
#  page_sequence = [Survey, thanks]
