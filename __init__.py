from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

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
        self.audioservice.play(['https://wfmt.streamguys1.com/main-mp3'])

    def stop(self):
        if self.audioservice.is_playing:
            self.log.info('stopping WFMT stream')
            self.audioservice.stop()
            return True
        else:
            return False

def create_skill():
    return WFMTSkill()

