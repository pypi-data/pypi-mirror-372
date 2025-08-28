#!/usr/bin/env python3
'''
NieMarkov: Niema's Python implementation of Markov chains
'''

# imports
from ast import literal_eval
from gzip import open as gopen
from pickle import dump as pdump, load as pload
from random import randint

# useful constants
NIEMARKOV_VERSION = '1.0.0'
ALLOWED_STATE_TYPES = {int, str}
DEFAULT_BUFSIZE = 1048576 # 1 MB #8192 # 8 KB
MODEL_EXT = {'dict', 'pkl'}

# helper function to check state type and throw an error if not allowed
def check_state_type(state_label):
    if type(state_label) not in ALLOWED_STATE_TYPES:
        raise TypeError("Invalid state type (%s). Must be one of: %s" % (type(state_label), ', '.join(str(t) for t in ALLOWED_STATE_TYPES)))

# open a file for reading/writing (None = stdin/stdout)
def open_file(fn, mode='rt', buffering=DEFAULT_BUFSIZE):
    mode = mode.strip().lower()
    if fn is None:
        if 'r' in mode:
            from sys import stdin as f
        else:
            from sys import stdout as f
    elif fn.strip().lower().endswith('.gz'):
        f = gopen(fn, mode=mode)
    else:
        f = open(fn, mode=mode)
    return f

# helper function to randomly pick from a `dict` of options (keys = options, values = count weighting that option)
def random_choice(options):
    sum_options = sum(options.values())
    random_int = randint(1, sum_options)
    curr_total_count = 0
    for option, count in options.items():
        curr_total_count += count
        if random_int <= curr_total_count:
            return option

# class to represent Markov chains
class MarkovChain:
    # initialize a `MarkovChain` object
    def __init__(self, order=1):
        if not isinstance(order, int) or order < 1:
            raise ValueError("`order` must be a positive integer")
        self.version = NIEMARKOV_VERSION  # NieMarkov version number
        self.order = order                # order of this Markov chain
        self.labels = list()              # labels of the states of this Markov chain
        self.label_to_state = dict()      # `label_to_state[label]` is the state (`int` from 0 to `num_states-1`) labeled by `label`
        self.transitions = dict()         # for an `order`-dimensional `tuple` of states `state_tuple`, `transitions[state_tuple]` is a `dict` where keys = outgoing state tuples, and values = transition counts
        self.initial_state_tuple = dict() # `initial_state_tuple[state_tuple]` is the number of times `state_tuple` is at the start of a path

    # return a string summarizing this `MarkovChain`
    def __str__(self):
        return '<NieMarkov: order=%d; states=%d>' % (self.order, len(self.labels))

    # dump this `MarkovChain` to a file (None = stdout)
    def dump(self, fn, buffering=DEFAULT_BUFSIZE):
        fn_lower = fn.strip().lower()
        model = {'version':self.version, 'order':self.order, 'labels':self.labels, 'transitions':self.transitions, 'initial': self.initial_state_tuple}
        if fn_lower.endswith('.pkl') or fn_lower.endswith('.pkl.gz'):
            with open_file(fn, mode='wb', buffering=buffering) as f:
                pdump(model, f)
        elif fn_lower.endswith('.dict') or fn_lower.endswith('.dict.gz'):
            with open_file(fn, mode='wt', buffering=buffering) as f:
                f.write(str(model))
        else:
            raise ValueError("Invalid output NieMarkov model filename (%s). Valid extensions: %s" % (fn, ', '.join(ext for ext in sorted(MODEL_EXT))))

    # load a `MarkovChain` from a file (None = stdin)
    def load(fn, buffering=DEFAULT_BUFSIZE):
        # load model from file
        fn_lower = fn.strip().lower()
        if fn_lower.endswith('.pkl') or fn_lower.endswith('.pkl.gz'):
            with open_file(fn, mode='rb', buffering=buffering) as f:
                model = pload(f)
        elif fn_lower.endswith('.dict') or fn_lower.endswith('.dict.gz'):
            with open_file(fn, mode='rt', buffering=buffering) as f:
                model = literal_eval(f.read())

        # check model for validity
        for k in ['order', 'labels', 'transitions', 'initial']:
            if k not in model:
                raise ValueError("Invalid model file (missing key '%s'): %s" % (k, fn))

        # create and populate output `MarkovChain`
        mc = MarkovChain(order=model['order'])
        mc.version = model['version']
        mc.labels = model['labels']
        mc.label_to_state = {label:i for i, label in enumerate(mc.labels)}
        mc.transitions = model['transitions']
        mc.initial_state_tuple = model['initial']
        return mc

    # add a path to this `MarkovChain`
    def add_path(self, path):
        # check `path` for validity
        if not isinstance(path, list):
            raise TypeError("`path` must be a list of state labels")
        if len(path) <= self.order:
            raise ValueError("Length of `path` (%d) must be > Markov chain order (%d)" % (len(path), self.order))


        # add new state labels
        for state_label in path:
            if state_label not in self.label_to_state:
                check_state_type(state_label)
                self.label_to_state[state_label] = len(self.labels)
                self.labels.append(state_label)

        # add path
        first_tup = tuple(self.label_to_state[path[j]] for j in range(self.order))
        if first_tup in self.initial_state_tuple:
            self.initial_state_tuple[first_tup] += 1
        else:
            self.initial_state_tuple[first_tup] = 1
        for i in range(len(path) - self.order):
            from_tup = tuple(self.label_to_state[path[j]] for j in range(i, i+self.order))
            to_tup = tuple(self.label_to_state[path[j]] for j in range(i+1, i+1+self.order))
            if from_tup in self.transitions:
                if to_tup in self.transitions[from_tup]:
                    self.transitions[from_tup][to_tup] += 1
                else:
                    self.transitions[from_tup][to_tup] = 1
            else:
                self.transitions[from_tup] = {to_tup: 1}

    # generate a random path in this `MarkovChain`
    def generate_path(self, max_len=float('inf'), start=None):
        if start is None:
            curr_state_tuple = random_choice(self.initial_state_tuple)
        elif len(start) == self.order:
            curr_state_tuple = tuple(self.label_to_state[label] for label in start)
            if curr_state_tuple not in self.transitions:
                raise ValueError("No outgoing edges from start: %s" % start)
        else: # in the future, can do something fancy to handle this scenario, e.g. randomly pick an initial state tuple ending with `start`
            raise ValueError("`start` length (%d) must be same as Markov model order (%d): %s" % (len(start), self.order, start))
        path = [self.labels[state] for state in curr_state_tuple]
        while len(path) < max_len:
            if curr_state_tuple not in self.transitions:
                break
            curr_state_tuple = random_choice(self.transitions[curr_state_tuple])
            path.append(self.labels[curr_state_tuple[-1]])
        return path
