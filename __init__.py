from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from mycroft.skills.audioservice import AudioService

class WFMTSkill(MycroftSkill):

    def __init__(self, name=None):
        super(WFMTSkill, self).__init__(name="WFMTSkill")

    def initialize(self):
        self.log.info('initializing Audio Service')
        self.audio_service = AudioService(self.emitter)

    @intent_handler(IntentBuilder("PlayIntent").require("Play"))
    def handle_play_intent(self, message):
        self.log.info('starting WFMT stream')
        self.audio_service.stop()
        self.audio_service.play('http://stream.wfmt.com/main-mp3')

    def stop(self):
        self.log.info('stopping WFMT stream')
        self.audio_service.stop()
        return True

def create_skill():
    return WFMTSkill()
