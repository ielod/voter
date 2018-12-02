from datetime import datetime
import re

ALLOWED_PLACE_PATTERN = '([-\'./\w]+)'
TOPIC_PATTERN = '{} @ (\S+) \(([^()]+)\)'.format(ALLOWED_PLACE_PATTERN)
DATE_PATTERN = '%Y-%m-%d'

EASTER_EGG = 'eurest'

WHO = 'who'
WHERE = 'where'
WHEN = 'when'


class LunchVoter(object):

    def __init__(self, topic=''):
        self.topic = self.parse_topic(topic)

    @staticmethod
    def _strip_vote(place):
        pattern = re.compile(ALLOWED_PLACE_PATTERN)
        decoded_place = pattern.findall(place)
        if len(decoded_place) == 0:
            decoded_place.append(EASTER_EGG)
        return decoded_place[0].lower()

    @staticmethod
    def _is_topic_for_today(topic):
        today_pattern = datetime.now().strftime('{} |'.format(DATE_PATTERN))
        return topic.find(today_pattern) == 0

    def _register_vote(self, who, where, when):
        self._remove_from_topic_if_exists(who)
        if len(self.topic) == 0:
            self.topic.append(dict(who=[who], where=where, when=when))
        else:
            found = False
            for place in self.topic:
                if WHERE in place and WHEN in place and WHO in place:
                    if place[WHERE] == where and place[WHEN] == when:
                        place[WHO].append(who)
                        place[WHO].sort()
                        found = True
            if not found:
                self.topic.append(dict(who=[who], where=where, when=when))

    def _remove_from_topic_if_exists(self, who):
        if who in [person for place in self.topic for person in place[WHO]]:
            for place in self.topic:
                if who in place[WHO]:
                    if len(place[WHO]) > 1:
                        place[WHO].remove(who)
                    else:
                        self.topic.remove(place)

    def build_topic(self):
        topic = datetime.now().strftime(DATE_PATTERN)
        for place in self.topic:
            if len(topic) > 0:
                topic += ' | '
            topic += '{} @ {} ({})'.format(place[WHERE],
                                           place[WHEN],
                                           ', '.join(place[WHO]))
        return topic

    def parse_topic(self, topic):
        self.topic = []
        if self._is_topic_for_today(topic):
            pattern = re.compile(TOPIC_PATTERN)
            places = pattern.findall(topic)
            for place in places:
                people = place[2].split(', ')
                people.sort()
                self.topic.append(dict(where=place[0],
                                       when=place[1],
                                       who=people))
        return self.topic

    def vote(self, vote_details):
        who, where, when = vote_details.split()
        self._register_vote(who, self._strip_vote(where), when)
        return self.build_topic()
