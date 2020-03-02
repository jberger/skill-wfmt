from adapt.intent import IntentBuilder
from mycroft.skills.core import intent_handler
from mycroft.util.log import LOG
from mycroft.skills.audioservice import AudioService
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
import requests
import html
import re

class WFMTSkill(CommonPlaySkill):

    def CPS_match_query_phrase(self, phrase):
        """ This method responds wether the skill can play the input phrase.

            The method is invoked by the PlayBackControlSkill.

            Returns: tuple (matched phrase(str),
                            match level(CPSMatchLevel),
                            optional data(dict))
                     or None if no match was found.
        """
        if (phrase.lower() == 'wfmt'):
                return (phrase, CPSMatchLevel.EXACT)
        return None

    def CPS_start(self, phrase, data):
        """ Starts playback.

            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        if self.audioservice.is_playing:
            self.log.info('stopping existing stream')
            self.audioservice.stop()
        self.log.info('starting WFMT stream')
        self.audioservice.play(['https://wfmt.streamguys1.com/main-mp3'], 'vlc')

    def stop(self):
        if self.audioservice.is_playing:
            self.log.info('stopping WFMT stream')
            self.audioservice.stop()
            return True
        else:
            return False

    @intent_handler(IntentBuilder("CurrentIntent").require("Current"))
    def handle_current_intent(self, message):
        try:
            playlist = self.fetch_playlist()
            show = self.parse_show(playlist['show'])

            if playlist.get('track'):
                text = 'WFMT is currently playing '
                text += self.parse_track(playlist['track'])
                if show:
                    text += '. On ' + show
                self.__inform(text)
                return

            if show:
                text = 'WFMT is currently airing ' + show
                self.__inform(text)
                return

            raise RuntimeError('No information')

        except Exception as e:
            self.log.info('failed to look up current playing information: ' + str(e))
            self.speak('Sorry, I cannot find that right now')

    @intent_handler(IntentBuilder("PreviousIntent").require("Previous"))
    def handle_previous_intent(self, message):
        try:
            playlist = self.fetch_playlist()
            if playlist['prev_track'][0]:
                text = 'WFMT was previously playing '
                text += self.parse_track(playlist['prev_track'][0])
                self.__inform(text)
            else:
                raise RuntimeError('No track')

        except Exception as e:
            self.log.info('failed to look up previous playing information: ' + str(e))
            self.speak('Sorry, I cannot find that right now')

    def __inform(self, text):
        self.enclosure.deactivate_mouth_events()
        self.enclosure.mouth_text(text)
        self.speak(text)
        mycroft.audio.wait_while_speaking()
        self.enclosure.activate_mouth_events()
        self.enclosure.mouth_reset()

    def fetch_playlist(self):
        r = requests.get('https://clients.webplaylist.org/cgi-bin/wfmt/wonV2.json?_=1532182149220')
        r.raise_for_status()
        return r.json()

    def parse_show(self, show):
        if 'title' not in show:
            return None
        text = show['title']
        if show.get('subtitle'):
            text += '. ' + show['subtitle']
        return text

    def parse_track(self, track):
        text = track['title']
        if track.get('composer'):
            text += ' by ' + self.grok_composer(track['composer'])
        if track.get('soloists'):
            text += '. Featuring '
            text += ' and '.join([self.grok_soloist(x) for x in track['soloists']])
        return text

    def grok_soloist(self, value):
        value = html.unescape(value)

        # split component parts
        # first match is "with", remaining are "and"
        replace = ', with '
        def s(match):
            nonlocal replace
            ret = replace
            replace = ', and '
            return ret
        value = re.sub(r'/|;', s, value)

        # common abbreviations
        value = re.sub(r'\bsym\b.?', 'symphony', value, flags=re.I)
        value = re.sub(r'\borch\b.?', 'orchestra', value, flags=re.I)
        value = re.sub(r'\op\b.?', 'orchestra', value, flags=re.I)

        # instrumentalists
        # this will need more values as they are shown
        value = re.sub(r'\bp\b', 'piano', value)
        value = re.sub(r'\bg\b', 'guitar', value)
        value = re.sub(r'\bf\b', 'flute', value)
        return value

    def grok_composer(self, value):
        value = html.unescape(value)
        # sometimes / means "and", "and the", "with", "conducted by". grrrr
        value = re.sub(r'/', ' and ', value)
        return value

    def grok_title(self, value):
        value = html.unescape(value)
        return value

def create_skill():
    return WFMTSkill()
