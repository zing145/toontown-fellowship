from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from panda3d.core import Filename, Vec4

from otp.ai.MagicWordGlobal import *
from toontown.event import ExperimentChallenges
from toontown.event.DistributedEvent import DistributedEvent
from toontown.event.ExperimentBlimp import ExperimentBlimp
from toontown.event.ExperimentChallengeGUI import ExperimentChallengeGUI


class DistributedExperimentEvent(DistributedEvent):
    notify = directNotify.newCategory('DistributedExperimentEvent')

    def __init__(self, cr):
        DistributedEvent.__init__(self, cr)

        self.introMusic = base.loadMusic('phase_4/audio/bgm/TE_battle_intro.ogg')
        self.music = base.loadMusic('phase_4/audio/bgm/TE_battle.ogg')
        self.musicSequence = None

        self.blimp = None

        self.challengeGui = None
        self.phase = 0

    def start(self):
        taskMgr.remove('TT-birds')

        base.musicManager.stopAllSounds()
        base.lockMusic()

        self.musicSequence = Sequence(
            Func(base.playMusic, self.introMusic, looping=0, volume=1, playLocked=True),
            Wait(self.introMusic.length()),
            Func(base.playMusic, self.music, looping=1, volume=1, playLocked=True))
        self.musicSequence.start()

        if __debug__:
            skyblue2Filename = Filename('../resources/phase_3.5/maps/skyblue2_invasion.jpg')
            middayskyBFilename = Filename('../resources/phase_3.5/maps/middayskyB_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename('../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename('../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a_invasion.rgb')
        else:
            skyblue2Filename = Filename('/phase_3.5/maps/skyblue2_invasion.jpg')
            middayskyBFilename = Filename('/phase_3.5/maps/middayskyB_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename('/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_invasion.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename('/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a_invasion.rgb')
        self.cr.playGame.hood.sky.findTexture('skyblue2').read(skyblue2Filename)
        self.cr.playGame.hood.sky.findTexture('middayskyB').read(middayskyBFilename)
        self.cr.playGame.hood.sky.findTexture('toontown_central_tutorial_palette_4amla_1').read(toontown_central_tutorial_palette_4amla_1Filename, toontown_central_tutorial_palette_4amla_1_aFilename, 0, 0)

        render.setColorScale(Vec4(0.85, 0.65, 0.65, 1))
        aspect2d.setColorScale(Vec4(0.85, 0.65, 0.65, 1))

    def delete(self):
        self.musicSequence.finish()
        self.musicSequence = None

        if self.blimp is not None:
            self.blimp.cleanup()
            self.blimp = None

        if self.challengeGui:
            self.challengeGui.destroy()

        base.musicManager.stopAllSounds()
        base.unlockMusic()

        if __debug__:
            skyblue2Filename = Filename('../resources/phase_3.5/maps/skyblue2.jpg')
            middayskyBFilename = Filename('../resources/phase_3.5/maps/middayskyB.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename('../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename('../resources/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a.rgb')
        else:
            skyblue2Filename = Filename('/phase_3.5/maps/skyblue2.jpg')
            middayskyBFilename = Filename('/phase_3.5/maps/middayskyB.jpg')
            toontown_central_tutorial_palette_4amla_1Filename = Filename('/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1.jpg')
            toontown_central_tutorial_palette_4amla_1_aFilename = Filename('/phase_3.5/maps/toontown_central_tutorial_palette_4amla_1_a.rgb')
        self.cr.playGame.hood.sky.findTexture('skyblue2').read(skyblue2Filename)
        self.cr.playGame.hood.sky.findTexture('middayskyB').read(middayskyBFilename)
        self.cr.playGame.hood.sky.findTexture('toontown_central_tutorial_palette_4amla_1').read(toontown_central_tutorial_palette_4amla_1Filename, toontown_central_tutorial_palette_4amla_1_aFilename, 0, 0)

        render.setColorScale(Vec4(1, 1, 1, 1))
        aspect2d.setColorScale(Vec4(1, 1, 1, 1))

        DistributedEvent.delete(self)

    def setVisGroups(self, visGroups):
        self.cr.sendSetZoneMsg(self.zoneId, visGroups)

    def createBlimp(self, timestamp):
        self.blimp = ExperimentBlimp()
        self.blimp.reparentTo(render)
        self.blimp.setPosHpr(144, -188, 55, 140, 0, 5)
        self.blimp.startFlying(timestamp)
        self.blimp.request('Phase0', timestamp)

    def setChallenge(self, challengeId):
        if challengeId == 0:
            self.completeObjective()
            return

        challengeInfo = ExperimentChallenges.getChallengeInfo(challengeId)
        self.challengeGui = ExperimentChallengeGUI(*challengeInfo)
        self.challengeGui.setPos(0, 0, 0.8)
        self.challengeGui.fadeIn()

    def setChallengeCount(self, count):
        if self.challengeGui:
            self.challengeGui.updateProgress(count)

    def challengeComplete(self):
        if self.challengeGui:
            self.challengeGui.fadeOutDestroy()
            self.challengeGui = None

    def setPhase(self, phase, timestamp):
        self.phase = phase
        self.blimp.request('Phase%s' % phase, timestamp)

@magicWord(category=CATEGORY_PROGRAMMER, types=[int])
def blimp(phase):
    if not (0 <= phase <= 3):
        return 'Invalid phase.'
    for event in base.cr.doFindAllInstances(DistributedExperimentEvent):
        event.blimp.request('Phase%d' % phase, globalClockDelta.getRealNetworkTime(bits=32))
        break
    else:
        return "Couldn't find a blimp."