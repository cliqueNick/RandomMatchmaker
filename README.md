usage: Random Matchmaker [-h] [-d DENY_LIST_FILE] [-i MAX_ITERATIONS]
                         [-t THRESHOLD] [-v]
                         registration_file history_file output_file

Provides random dating assignments without repeating past assignments.
Individuals must opt-in every time to be included. An adequate solution is not
guaranteed. Assignments for every individual are not guaranteed.

positional arguments:
  registration_file     Path to the csv file containing the information of the
                        individuals who have opted in to receive random date
                        assignments. Should have these columns: first name,
                        last name, gender. The gender column must contain
                        either: male or female.
  history_file          Path to the csv file where past pairings are stored so
                        they will not be repeated. This will be updated when
                        new assignments are made. Date when assignments are
                        made are recorded in UTC time zone. Will be created if
                        does not exist. Should have these columns: date, male
                        first name, male last name, female first name, female
                        last name.
  output_file           Path to where the new assignments will be stored as a
                        csv. Will be created and overwritten as needed.

optional arguments:
  -h, --help            show this help message and exit
  -d DENY_LIST_FILE, --deny_list_file DENY_LIST_FILE
                        Path to a csv file of names that should never be
                        allowed to use this service. Requires names to match
                        exactly. Should have these columns: first name, last
                        name, gender. The gender column must contain either:
                        male or female.
  -i MAX_ITERATIONS, --max_iterations MAX_ITERATIONS
                        The maximum number of attempts at creating
                        assignments. Increase this before changing the
                        threshold. Must be greater than one. The default is
                        100.
  -t THRESHOLD, --threshold THRESHOLD
                        The maximum fraction of the current registration list
                        that an individual is allowed to have already been
                        paired with. The higher this number the more likely a
                        solution will not be able to be found and the less it
                        is likely that extremely experienced daters are
                        excluded. Decrease this if no solution is found after
                        increasing the number of iterations. Must be a value
                        between 0 and 1. The default value is 1.0.
  -v, --verbose         Whether to print out the resulting assignments as well
                        as save them to a file.

Random Matchmaker 1.0 by Nickolas Lee. Copyright 2023. All rights reserved.
