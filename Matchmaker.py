import pandas
import random
import argparse
import datetime
import os

__author__ = "Nickolas Lee"
__version__ = "1.0"


argparser = argparse.ArgumentParser(prog="Random Matchmaker", description="Provides random dating assignments without repeating past assignments. "
                                                                          "Individuals must opt-in every time to be included. "
                                                                          "An adequate solution is not guaranteed. "
                                                                          "Assignments for every individual are not guaranteed. ",
                                    epilog="Random Matchmaker " + __version__ + " by Nickolas Lee. Copyright 2023. All rights reserved.")
argparser.add_argument("registration_file", help="Path to the csv file containing the information of the individuals who have opted in to receive random date assignments. "
                                                 "Should have these columns: first name, last name, gender. The gender column must contain either: male or female.")
argparser.add_argument("history_file", help="Path to the csv file where past pairings are stored so they will not be repeated. This will be updated when new assignments are made. "
                                            "Date when assignments are made are recorded in UTC time zone. Will be created if does not exist. "
                                            "Should have these columns: date, male first name, male last name, female first name, female last name.")
argparser.add_argument("output_file", help="Path to where the new assignments will be stored as a csv. Will be created and overwritten as needed. ")
argparser.add_argument("-d", "--deny_list_file", default=None, help="Path to a csv file of names that should never be allowed to use this service. "
                                                                    "Requires names to match exactly. "
                                                                    "Should have these columns: first name, last name, gender. The gender column must contain either: male or female.")
argparser.add_argument("-i", "--max_iterations", type=int, default=100, help="The maximum number of attempts at creating assignments. "
                                                                             "Increase this before changing the threshold. "
                                                                             "Must be greater than one. "
                                                                             "The default is 100.")
argparser.add_argument("-t", "--threshold", type=float, default=1.0, help="The maximum fraction of the current registration list that an individual is allowed to have already been "
                                                                          "paired with. "
                                                                          "The higher this number the more likely a solution will not be able to be found "
                                                                          "and the less it is likely that extremely experienced daters are excluded. "
                                                                          "Decrease this if no solution is found after increasing the number of iterations. "
                                                                          "Must be a value between 0 and 1. "
                                                                          "The default value is 1.0.")
argparser.add_argument("-v", "--verbose", action="store_true", help="Whether to print out the resulting assignments as well as save them to a file.")


def make_matches(registrations, history, deny_list=None, max_iterations: int = 100, threshold: float = 1.0):
    if 1 >= max_iterations:
        raise ValueError("Too few iterations.")
    if 0 >= threshold or threshold > 1.0:
        raise ValueError("Threshold must be between zero and one.")

    # remove those on black list
    registrations_set = set(map(tuple, registrations.values))
    if deny_list is not None:
        black_list_set = set(map(tuple, deny_list.values))
        white = registrations_set.difference(black_list_set)
        clean_list = pandas.DataFrame(white, columns=registrations.columns)
    else:
        clean_list = registrations
    history_set = set(map(tuple, history.drop(columns="date").values))

    males = clean_list[clean_list["gender"] == "male"]
    males = pandas.DataFrame(males)
    males.drop(columns="gender", inplace=True)
    males_set = set(map(lambda x: x[0] + x[1], males.values))
    females = clean_list[clean_list["gender"] == "female"]
    females = pandas.DataFrame(females)
    females.drop(columns="gender", inplace=True)
    females_set = set(map(lambda x: x[0] + x[1], females.values))

    # make history into a dictionary
    history_dict = dict()
    for rowid, row in history.iterrows():
        male_name = row["male first name"] + row["male last name"]
        female_name = row["female first name"] + row["female last name"]

        if male_name not in history_dict:
            history_dict[male_name] = set()
        history_dict[male_name].add(female_name)

        if female_name not in history_dict:
            history_dict[female_name] = set()
        history_dict[female_name].add(male_name)

    # remove those who have already dated everyone on the list
    cannot_help = set()
    for rowid, row in males.iterrows():
        male_name = row["first name"] + row["last name"]
        try:
            dated = history_dict[male_name].intersection(females_set)
            if len(dated) == len(females_set):
                print(male_name + " has already dated everyone on the list and will be excluded.")
                cannot_help.add(male_name)
            elif len(dated) > len(females_set) * threshold:
                print(male_name + " has already dated enough people on the list and will be excluded.")
                cannot_help.add(male_name)
        except KeyError:
            pass                        # those in history but not currently registered
    males["name"] = males["first name"] + males["last name"]
    males = males[~males["name"].isin(cannot_help)]
    males.drop(columns="name", inplace=True)

    cannot_help = set()
    for rowid, row in females.iterrows():
        female_name = row["first name"] + row["last name"]
        try:
            dated = history_dict[female_name].intersection(males_set)
            if len(dated) == len(males_set):
                print(female_name + " has already dated everyone on the list and will be excluded.")
                cannot_help.add(female_name)
            elif len(dated) > len(males_set) * threshold:
                print(female_name + " has already dated enough people on the list and will be excluded.")
                cannot_help.add(female_name)
        except KeyError:
            pass
    females["name"] = females["first name"] + females["last name"]
    females = females[~females["name"].isin(cannot_help)]
    females.drop(columns="name", inplace=True)

    pair_results = list()
    for i in range(max_iterations):
        # randomly sort
        index = [i for i in range(len(males))]
        random.shuffle(index)
        males["random"] = index
        males.sort_values(by="random", inplace=True)
        males.reset_index()
        males.drop(columns="random", inplace=True)

        index = [i for i in range(len(females))]
        random.shuffle(index)
        females["random"] = index
        females.sort_values(by="random", inplace=True)
        females.reset_index()
        females.drop(columns="random", inplace=True)

        # find the smaller of two lists
        if len(males) <= 0:
            raise ValueError("Not enough eligible male participants.")
        if len(females) <= 0:
            raise ValueError("Not enough eligible female participants.")
        iterations = 0
        if len(males) <= len(females):
            iterations = len(males)
        elif len(males) > len(females):
            iterations = len(females)

        # align
        pair_results = list()
        for i in range(iterations):
            pair_results.append(males.iloc[i].tolist() + females.iloc[i].tolist())

        # if any pair is seen in the history then try again
        pair_results_set = set(map(tuple, pair_results))
        intersection = pair_results_set.intersection(history_set)
        if len(intersection) == 0:
            break
    else:
        print("maximum iterations reached without finding a solution")

    pair_results = pandas.DataFrame(pair_results, columns=["male first name", "male last name"] + ["female first name", "female last name"])
    return pair_results


args = argparser.parse_args()
registrations = pandas.read_csv(args.registration_file, usecols=["first name", "last name", "gender"])
if not os.path.exists(args.history_file):
    h = pandas.DataFrame(columns=["date"] + ["male first name", "male last name"] + ["female first name", "female last name"])
    h.to_csv(args.history_file, index=False)
history = pandas.read_csv(args.history_file, usecols=["date"] + ["male first name", "male last name"] + ["female first name", "female last name"])
deny_list = None
if args.deny_list_file is not None:
    deny_list = pandas.read_csv(args.deny_list_file, usecols=["first name", "last name", "gender"])
output = make_matches(registrations, history, deny_list, max_iterations=args.max_iterations, threshold=args.threshold)
output.to_csv(args.output_file, index=False)
if args.verbose:
    print(output)
output["date"] = [datetime.datetime.utcnow() for i in range(len(output))]
history = pandas.concat([history, output])
history.to_csv(args.history_file, index=False)
