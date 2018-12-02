#!/usr/bin/env python2
from datetime import datetime
from datetime import timedelta
import unittest

import voter as vtr


class TestVoter(unittest.TestCase):

    def setUp(self):
        self.voter = vtr.LunchVoter()

    def test_vote(self):
        vote = 'fleety Allee 11:30'
        expected_topic = 'allee @ 11:30 (fleety)'
        self._assert_vote(expected_topic, vote)

    def test_vote_invalid_chars(self):
        vote = 'fleety some:place 11:38'
        expected_topic = 'some @ 11:38 (fleety)'
        self._assert_vote(expected_topic, vote)

    def test_vote_two_on_same_place(self):
        self._pre_vote('foody allee 11:30')
        vote = 'fleety allee 11:30'
        expected_topic = 'allee @ 11:30 (fleety, foody)'
        self._assert_vote(expected_topic, vote)

    def test_vote_more_on_same_place(self):
        self._pre_vote('foody allee 11:30')
        self._pre_vote('noemi allee 11:30')
        vote = 'fleety allee 11:30'
        expected_topic = 'allee @ 11:30 (fleety, foody, noemi)'
        self._assert_vote(expected_topic, vote)

    def test_vote_different(self):
        self._pre_vote('foody allee 11:30')
        vote = 'fleety foodcourt 11:13'
        expected_topic = 'allee @ 11:30 (foody) | foodcourt @ 11:13 (fleety)'
        self._assert_vote(expected_topic, vote)

        vote = 'noemi foodcourt 11:13'
        expected_topic = 'allee @ 11:30 (foody) | foodcourt @ 11:13 (fleety, noemi)'
        self._assert_vote(expected_topic, vote)

        vote = 'sam foodcourt 11:13'
        expected_topic = ('allee @ 11:30 (foody) | '
                          'foodcourt @ 11:13 (fleety, noemi, sam)')
        self._assert_vote(expected_topic, vote)

        vote = 'ben burgery 11:13'
        expected_topic = ('allee @ 11:30 (foody) | '
                          'foodcourt @ 11:13 (fleety, noemi, sam) | '
                          'burgery @ 11:13 (ben)')
        self._assert_vote(expected_topic, vote)

        vote = 'gavin burgery 11:13'
        expected_topic = ('allee @ 11:30 (foody) | '
                          'foodcourt @ 11:13 (fleety, noemi, sam) | '
                          'burgery @ 11:13 (ben, gavin)')
        self._assert_vote(expected_topic, vote)

        vote = 'alex burgery 11:30'
        expected_topic = ('allee @ 11:30 (foody) | '
                          'foodcourt @ 11:13 (fleety, noemi, sam) | '
                          'burgery @ 11:13 (ben, gavin) | burgery @ 11:30 (alex)')
        self._assert_vote(expected_topic, vote)

    def test_revote(self):
        self._pre_vote('fleety allee 11:30')
        vote = 'fleety foodcourt 11:13'
        expected_topic = 'foodcourt @ 11:13 (fleety)'
        self._assert_vote(expected_topic, vote)

    def test_revote_multiple_places(self):
        self._pre_vote('fleety allee 11:30')
        self._pre_vote('foody foodcourt 11:30')
        vote = 'fleety foodcourt 11:30'
        expected_topic = 'foodcourt @ 11:30 (fleety, foody)'
        self._assert_vote(expected_topic, vote)

        vote = 'foody allee 11:13'
        expected_topic = 'foodcourt @ 11:30 (fleety) | allee @ 11:13 (foody)'
        self._assert_vote(expected_topic, vote)

        self._pre_vote('sam allee 11:13')
        vote = 'sam burgery 11:13'
        expected_topic = ('foodcourt @ 11:30 (fleety) | '
                          'allee @ 11:13 (foody) | '
                          'burgery @ 11:13 (sam)')
        self._assert_vote(expected_topic, vote)

        vote = 'sam foodcourt 11:30'
        expected_topic = 'foodcourt @ 11:30 (fleety, sam) | allee @ 11:13 (foody)'
        self._assert_vote(expected_topic, vote)

        vote = 'sam allee 11:13'
        expected_topic = 'foodcourt @ 11:30 (fleety) | allee @ 11:13 (foody, sam)'
        self._assert_vote(expected_topic, vote)

    def test_parse_topic(self):
        topic_to_parse = 'foodcourt @ 11:13 (fleety)'
        expected_topic = [{'who': ['fleety'],
                           'where': 'foodcourt',
                           'when': '11:13'}]
        self._assert_parse_topic(expected_topic, topic_to_parse)

        topic_to_parse = 'foodcourt @ 11:13 (fleety, noemi)'
        expected_topic = [{'who': ['fleety', 'noemi'],
                           'where': 'foodcourt',
                           'when': '11:13'}]
        self._assert_parse_topic(expected_topic, topic_to_parse)

        topic_to_parse = ('foodcourt @ 11:13 (fleety, noemi) | '
                          'allee @ 11:30 (foody, ben, gavin)')
        expected_topic = [{'who': ['fleety', 'noemi'],
                           'where': 'foodcourt',
                           'when': '11:13'},
                          {'who': ['ben', 'foody', 'gavin'],
                           'where': 'allee',
                           'when': '11:30'}]
        self._assert_parse_topic(expected_topic, topic_to_parse)

    def test_parse_fancy_topic(self):
        topic_to_parse = 'butcher\'s @ 11:13 (fleety)'
        expected_topic = [{'who': ['fleety'],
                           'where': 'butcher\'s',
                           'when': '11:13'}]
        self._assert_parse_topic(expected_topic, topic_to_parse)

        topic_to_parse = 'a./b_3-8 @ 11:13 (fleety)'
        expected_topic = [{'who': ['fleety'],
                           'where': 'a./b_3-8',
                           'when': '11:13'}]
        self._assert_parse_topic(expected_topic, topic_to_parse)

    def test_reinit_class(self):
        self.voter = vtr.LunchVoter(self._time_stamp('foodcourt @ 11:13 (fleety)'))
        vote = 'foody foodcourt 11:13'
        expected_topic = 'foodcourt @ 11:13 (fleety, foody)'
        self._assert_vote(expected_topic, vote)

    def test_yesterdays_topic_replaced(self):
        yesterday = datetime.today() - timedelta(days=1)
        old_topic = ('{} | foodcourt @ 11:13 (fleety)'
                     .format(yesterday.strftime(vtr.DATE_PATTERN)))
        self.voter = vtr.LunchVoter(old_topic)
        vote = 'foody foodcourt 11:13'
        expected_topic = 'foodcourt @ 11:13 (foody)'
        self._assert_vote(expected_topic, vote)

    def test_invalid_topic(self):
        self.voter.parse_topic('invalid topic')
        vote = 'foody foodcourt 12:00'
        expected_topic = 'foodcourt @ 12:00 (foody)'
        self._assert_vote(expected_topic, vote)

    def test_easter_egg(self):
        vote = 'fleety ??? 11:30'
        expected_topic = '{} @ 11:30 (fleety)'.format(vtr.EASTER_EGG)
        self._assert_vote(expected_topic, vote)

    def _pre_vote(self, vote):
        self.voter.vote(vote)

    @staticmethod
    def _time_stamp(text):
        return '{} | {}'.format(datetime.now().strftime(vtr.DATE_PATTERN), text)

    def _assert_vote(self, expected_topic, vote):
        topic = self.voter.vote(vote)
        self.assertEquals(self._time_stamp(expected_topic), topic)

    def _assert_parse_topic(self, expected_topic, topic_to_parse):
        expected_topic_string = '{}'.format(expected_topic)
        parsed_topic = self.voter.parse_topic(self._time_stamp(topic_to_parse))
        parsed_topic_string = '{}'.format(parsed_topic)
        self.assertEquals(expected_topic_string, parsed_topic_string)


if __name__ == '__main__':
    unittest.main()
