import json
import os
import typing as t
from random import randint

filepath = os.path.dirname(os.path.abspath(__file__))

first_names = []
with open(os.path.join(filepath, "../data/names.json"), "r") as f:
    first_names = json.load(f)

last_names = []
with open(os.path.join(filepath, "../data/surnames.json"), "r") as f:
    last_names = json.load(f)

country_names = ["U.S.", "Canada"]

city_names = []
with open(os.path.join(filepath, "../data/cities.json"), "r") as f:
    city_names = json.load(f)

domain_names = []
with open(os.path.join(filepath, "../data/domains.json"), "r") as f:
    domain_names = json.load(f)

nouns = []
with open(os.path.join(filepath, "../data/nouns.json"), "r") as f:
    nouns = json.load(f)

adjectives = []
with open(os.path.join(filepath, "../data/adjectives.json"), "r") as f:
    adjectives = json.load(f)

verbs = []
with open(os.path.join(filepath, "../data/verbs.json"), "r") as f:
    verbs = json.load(f)

proverbs = []
with open(os.path.join(filepath, "../data/proverbs.json"), "r") as f:
    proverbs = json.load(f)


def data_source(data) -> t.Generator:
    size = len(data)
    while True:
        yield data[randint(0, size - 1)]


def phone_numbers() -> t.Generator:
    min = 1111111111
    max = 9999999999
    num = str(randint(min, max))
    while True:
        yield f"{num[0:3]}-{num[3:6]}-{num[6:11]}"


def increment(i: int) -> int:
    i += 1
    return i
