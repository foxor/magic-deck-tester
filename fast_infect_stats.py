#!/usr/bin/env python

import math
import random

GO_FIRST = False

GAMES = 10000

TURNS = 7

FETCH_LANDS = set([
  "Arid Mesa",
  "Misty Rainforest",
  "Scalding Tarn",
  "Verdant Catacombs"
])

MANA_LANDS = set([
  "Stomping Ground"
])

GITAXIAN_PROBE = set([
  "Gitaxian Probe"
])

RANCOR = set([
  "Rancor"
])

CMC_1_CREATURE = set([
  "Glistener Elf"
])

CMC_2_CREATURE = set([
  "Ichorclaw Myr",
  "Blight Mamba"
])

ASSAULT_STROBE = set([
  "Assault Strobe"
])

GROUNDSWELL = set([
  "Groundswell"
])

BUF_4_CMC_1 = set([
  "Might of Old Korosa"
])

BUF_4_CMC_2 = set([
  "Colossal Might"
])

BUF_2_CMC_1 = RANCOR 

BUF_2_CMC_0 = set([
  "Mutagenic Growth"
])

BUF_1_CMC_1 = ASSAULT_STROBE

def load_deck():
  return [
    "Ichorclaw Myr",
    "Blight Mamba",
    "Glistener Elf",
    "Rancor",
    "Stomping Ground",
    "Arid Mesa",
    "Misty Rainforest",
    "Scalding Tarn",
    "Verdant Catacombs",
    "Might of Old Krosa",
    "Colossal Might",
    "Groundswell",
    "Assault Strobe",
    "Gitaxian Probe",
    "Mutagenic Growth"
  ] * 4

class Game(object):
  def __init__(self):
    self.library = load_deck()
    self.life = 20
    self.creatures = []
    self.rancor = []
    self.lands = 0
    self.hand = []
    self.turn = 0
    self.lands_tapped = 0
    self.did_win = False

  def shuffle(self):
    self.library = sorted(self.library, key=lambda x: random.random())

  def deal(self, num=1):
    for i in xrange(num):
      x , self.library = self.library[0], self.library[1:]
      yield x

  def play_card(self, card_num):
    self.hand = self.hand[:card_num] + self.hand[card_num+1:]

  def deal_hand(self):
    self.hand.extend(self.deal(7))

  def get_card_in_hand(self, card_name_set):
    for card in xrange(len(self.hand)):
      if self.hand[card] in card_name_set:
        yield card

  def play_land(self):
    for card in self.get_card_in_hand(FETCH_LANDS):
      for lib_card in xrange(len(self.library)):
        if self.library[lib_card] in MANA_LANDS:
          self.play_card(card)
          self.lands += 1
          self.library = self.library[:lib_card] + self.library[lib_card+1:]
          self.shuffle()
          self.land_this_turn = True
          return
    for card in self.get_card_in_hand(MANA_LANDS):
      self.play_card(card)
      self.lands += 1
      return

  def gitax(self):
    for card in self.get_card_in_hand(["Gitaxian Probe"]):
      self.play_card(card)
      self.life -= 2
      self.hand.extend(self.deal())

  def check_win(self):
    # Do I have a creature?
    # Can I give double strike?
    #  Do any of my creatures have rancor?
    # Does groundswell give 2 or 4?
    # Use +4, 1cmc
    # Use +4, 2cmc
    # Use +2, 1cmc
    # Use +2, 0cmc
    # Use +1, 1cmc
    # Did I win?
    if not self.creatures:
      return

    best_target = 0
    double_strike = [False for x in self.creatures]
    powers = [1 + 2 * self.rancor[x] for x in xrange(len(self.creatures))]

    for creature in xrange(len(self.creatures)):
      if self.rancor[creature]:
        best_target = creature
    for assault_strobe in self.get_card_in_hand(ASSAULT_STROBE):
      double_strike[creature] = True
      self.lands_tapped += 1
      break
    buf_4_1 = BUF_4_CMC_1
    buf_2_1 = BUF_2_CMC_1
    if self.land_this_turn:
      buf_4_1 |= GROUNDSWELL
    else:
      buf_2_1 |= GROUNDSWELL
    for buf in self.get_card_in_hand(buf_4_1):
      if self.lands - self.lands_tapped >= 1:
        powers[best_target] += 4
        self.lands_tapped += 1
    for buf in self.get_card_in_hand(BUF_4_CMC_2):
      if self.lands - self.lands_tapped >= 2:
        powers[best_target] += 4
        self.lands_tapped += 2
    for buf in self.get_card_in_hand(buf_2_1):
      if self.lands - self.lands_tapped >= 1:
        powers[best_target] += 2
        self.lands_tapped += 1
    for buf in self.get_card_in_hand(BUF_2_CMC_0):
      powers[best_target] += 2
    poison = sum(powers[x] * (2 if double_strike[x] else 1) for x in xrange(len(powers)))
    if poison >= 10:
      return True

  def long_term(self):
    # If any are true, play and recur:
    #  Do I have no creatures and 1cmc infext?
    #  Do I have no creatures and 2cmc infect?
    #  Do I have rancor?
    #  Can I cast 1cmc infect?
    #  Can I cast 2cmc infect?
    if not self.creatures or len(list(self.get_card_in_hand(RANCOR))) == 0:
      for creature in self.get_card_in_hand(CMC_1_CREATURE):
        if self.lands - self.lands_tapped >= 1:
          self.lands_tapped += 1
          self.creatures.append(self.hand[creature])
          self.rancor.append(False)
          self.play_card(creature)
          return self.long_term()
      for creature in self.get_card_in_hand(CMC_2_CREATURE):
        if self.lands - self.lands_tapped >= 2:
          self.lands_tapped += 2
          self.creatures.append(self.hand[creature])
          self.rancor.append(False)
          self.play_card(creature)
          return self.long_term()
    else:
      best_target = 0
      for creature in xrange(len(self.creatures)):
        if self.rancor[creature]:
          best_target = creature
      for rancor in self.get_card_in_hand(RANCOR):
        if self.lands - self.lands_tapped >= 1:
          self.lands_tapped += 1
          self.rancor[best_target] += 1
          self.play_card(rancor)
          return self.long_term()

  def play_turn(self, draw = True):
    self.summoning_sickness = False
    self.lands_tapped = 0
    self.land_this_turn = False
    if draw:
      self.hand.extend(self.deal())
    self.play_land()
    self.gitax()
    if not self.check_win():
      self.turn += 1
      self.long_term()
    else:
      self.did_win = True

  def won(self):
    if self.did_win:
      return {"won": self.turn}

def play_game():
  g = Game()
  g.shuffle()
  g.deal_hand()
  g.play_turn(not GO_FIRST)
  for i in xrange(TURNS):
    if g.won():
      return g.won()
    g.play_turn()
  return {'won': False}

_win_buckets = [0 for x in xrange(TURNS)]
_losses = 0
def analyze(result):
  global _win_bucket, _losses
  if result["won"]:
    _win_buckets[result["won"]] += 1
  else:
    _losses += 1

def draw_conclusions():
  print "Win Percentage: %s" % (sum(_win_buckets) * 1.0 / GAMES)
  mean = sum(_win_buckets[x] * x for x in xrange(TURNS)) * 1.0 / GAMES
  s = math.sqrt(sum(((mean - x) ** 2) * _win_buckets[x] for x in xrange(TURNS)) / (GAMES - 1))
  print "Mean: %s, Standard Deviation: %s" % (mean, s)

def run_stats():
  for i in xrange(GAMES):
    result = play_game()
    analyze(result)
  draw_conclusions()

if __name__ == '__main__':
  #import pdb;pdb.set_trace()
  run_stats()
