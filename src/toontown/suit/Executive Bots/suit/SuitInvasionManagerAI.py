import time

from toontown.battle import SuitBattleGlobals
from toontown.suit import SuitDNA
from toontown.suit.SuitInvasionGlobals import *
from toontown.toonbase import ToontownGlobals
import random
import shlex

class SuitInvasionManagerAI:
    MIN_TIME_INBETWEEN = 10
    MAX_TIME_INBETWEEN = 30
    MIN_TIME_DURING = 3
    MAX_TIME_DURING = 10
    def __init__(self, air):
        self.air = air

        self.invading = False
        self.start = 0
        self.remaining = 0
        self.total = 0
        self.suitDeptIndex = None
        self.suitTypeIndex = None
        self.flags = 0
        self.currentInvadingSuit = None
        self.currentInvadingDept = None
        self.invasionStatus = False
        self.isSkelecog = 0
        self.isWaiter = 0
        self.isV2 = 0
        # self.startInvading()

        self.air.netMessenger.accept(
            'startInvasion', self, self.handleStartInvasion)
        self.air.netMessenger.accept(
            'stopInvasion', self, self.handleStopInvasion)

        # We want to handle shard status queries so that a ShardStatusReceiver
        # being created after we're created will know where we're at:
        self.air.netMessenger.accept('queryShardStatus', self, self.sendInvasionStatus)

        self.sendInvasionStatus()

    def getInvading(self):
        return self.invasionStatus

    def getInvadingCog(self):
        currentInvadingSuit = self.currentInvadingSuit
        currentInvadingDept = self.currentInvadingDept

        if currentInvadingSuit == 'any':
            if currentInvadingDept in suitDepts:
                currentInvadingSuit = getRandomSuitByDept(currentInvadingDept)
            else:
                currentInvadingSuit = None

        return (currentInvadingSuit, self.isSkelecog,
                self.isV2, self.isWaiter)

    def startInvasion(self, suitDeptIndex=None, suitTypeIndex=None, flags=0,
                      type=INVASION_TYPE_NORMAL):
        if self.invading:
            # An invasion is currently in progress; ignore this request.
            return False

        if (suitDeptIndex is None) and (suitTypeIndex is None) and (not flags):
            # This invasion is no-op.
            return False

        if flags and ((suitDeptIndex is not None) or (suitTypeIndex is not None)):
            # For invasion flags to be present, it must be a generic invasion.
            return False

        if (suitDeptIndex is None) and (suitTypeIndex is not None):
            # It's impossible to determine the invading Cog.
            return False

        if flags not in (0, IFV3, IFV2, IFSkelecog, IFWaiter):
            # The provided flag combination is not possible.
            return False

        if (suitDeptIndex is not None) and (suitDeptIndex >= len(SuitDNA.suitDepts)):
            # Invalid suit department.
            return False

        if (suitTypeIndex is not None) and (suitTypeIndex >= SuitDNA.suitsPerDept):
            # Invalid suit type.
            return False

        if type not in (INVASION_TYPE_NORMAL, INVASION_TYPE_MEGA, INVASION_TYPE_BRUTAL):
            # Invalid invasion type.
            return False

        # Looks like we're all good. Begin the invasion:
        self.invading = True
        self.start = int(time.time())
        self.suitDeptIndex = suitDeptIndex
        self.suitTypeIndex = suitTypeIndex
        self.flags = flags

        # How many suits do we want?
        if type == INVASION_TYPE_NORMAL:
            self.total = 1000
        elif type == INVASION_TYPE_MEGA:
            self.total = 5000
        elif type == INVASION_TYPE_BRUTAL:
            self.total = 10000
        self.remaining = self.total

        self.flySuits()
        self.notifyInvasionStarted()

        # Update the invasion tracker on the districts page in the Shticker Book:
        if self.suitDeptIndex is not None:
            self.air.districtStats.b_setInvasionStatus(self.suitDeptIndex + 1)
        else:
            self.air.districtStats.b_setInvasionStatus(5)

        # If this is a normal invasion, and the players take too long to defeat
        # all of the Cogs, we'll want the invasion to timeout:
        if type == INVASION_TYPE_NORMAL:
            timeout = config.GetInt('invasion-timeout', 1800)
            taskMgr.doMethodLater(timeout, self.stopInvasion, 'invasionTimeout')
            
        # If this is a mega invasion, and the players take to long to defeat
        # all of the cogs, we want the invasion to take a bit longer to timeout:
        if type == INVASION_TYPE_MEGA:
            timeout = config.GetInt('invasion-timeout', 3200)
            
        # If this is a brutal invasion, the players will have a very long time to
        # Defeat the cogs before the invasion times out:
        if type == INVASION_TYPE_BRUTAL:
            timeout = config.GetInt('invasion-timeout', 10000)

        self.sendInvasionStatus()
        return True

    def newInvasion(self, name='any', dept='any', skelecog=0, v2=0, waiter=0):
        print 'NEW_INVASION: suit: %s, dept: %s, skelecog: %s, v2: %s, waiter: %s' % (
                name, dept, skelecog, v2, waiter)
        if name == 'any' and dept == 'any':
            if not skelecog and not v2 and not waiter:
                return False
        self.currentInvadingSuit = name
        self.currentInvadingDept = dept
        self.invasionStatus = True
        self.isSkelecog = skelecog
        self.isWaiter = waiter
        self.isV2 = v2

        self.cleanupCurrentSuits()
        self.alertPlayersOfInvasion()
        self.invasionStarted()

        return True
    def alertPlayersOfInvasion(self):
        currentInvadingSuit = self.currentInvadingSuit
        departmentInvasion = False
        if currentInvadingSuit == 'any':
            if self.currentInvadingDept == 'any':
                currentInvadingSuit = 'f'
            else:
                #Department invasion
                currentInvadingSuit = self.currentInvadingDept
                departmentInvasion = True
        if self.isSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBegin
            self.isWaiter = 0
            self.isV2 = 0
            departmentInvasion = False
        elif self.isV2:
            msgType = ToontownGlobals.V2InvasionBegin
            self.isSkelecog = 0
            self.isWaiter = 0
            departmentInvasion = False
        elif self.isWaiter:
            msgType = ToontownGlobals.WaiterInvasionBegin
            self.isSkelecog = 0
            self.isV2 = 0
            departmentInvasion = False
        elif departmentInvasion:
            msgType = ToontownGlobals.DepartmentInvasionBegin
            self.isSkelecog = 0
            self.isV2 = 0
            self.isWaiter = 0
        else:
            msgType = ToontownGlobals.SuitInvasionBegin
            self.isSkelecog = 0
            self.isV2 = 0
            self.isWaiter = 0
        self.air.newsManager.setInvasionStatus(msgType, currentInvadingSuit,
                                               1000, self.isSkelecog)

    def alertPlayersInvasionEnded(self):
        currentInvadingSuit = self.currentInvadingSuit
        departmentInvasion = False
        if currentInvadingSuit == 'any':
            if self.currentInvadingDept == 'any':
                currentInvadingSuit = 'f'
            else:
                #Department invasion
                currentInvadingSuit = self.currentInvadingDept
                departmentInvasion = True
        if self.isSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionEnd
            departmentInvasion = False
        elif self.isV2:
            msgType = ToontownGlobals.V2InvasionEnd
            departmentInvasion = False
        elif self.isWaiter:
            msgType = ToontownGlobals.WaiterInvasionEnd
            departmentInvasion = False
        elif departmentInvasion:
            msgType = ToontownGlobals.DepartmentInvasionEnd
        else:
            msgType = ToontownGlobals.SuitInvasionEnd
        self.air.newsManager.setInvasionStatus(msgType, currentInvadingSuit,
                                               1000, self.isSkelecog)

    def invasionStarted(self):
        t = self.MIN_TIME_DURING + random.randint(1, self.MAX_TIME_DURING)
        if t > self.MAX_TIME_DURING:
            t = self.MAX_TIME_DURING
        taskMgr.doMethodLater(t*60, self.cleanupInvasion, 'suitInvasionManager-cleanup')

    def startInvading(self):
        #Used for randomly spawning cog invasions. - No longer used.
        t = self.MIN_TIME_INBETWEEN + random.randint(1, self.MAX_TIME_INBETWEEN)
        if t > self.MAX_TIME_INBETWEEN:
            t = self.MAX_TIME_INBETWEEN
        taskMgr.doMethodLater(t*60, self.newInvasion, 'suitInvasionManager-invasion')

    def cleanupInvasion(self, task=None):
        self.invasionStatus = False
        self.alertPlayersInvasionEnded()
        self.currentInvadingSuit = None
        self.currentInvadingDept = None
        self.isSkelecog = 0
        self.isWaiter = 0
        self.isV2 = 0
        self.cleanupCurrentSuits()

        if task:
            return task.done

    def cleanupCurrentSuits(self):
        for suitPlanner in self.air.suitPlanners:
            self.air.suitPlanners.get(suitPlanner).flySuits()

    def cleanupTasks(self):
        taskMgr.remove('suitInvasionManager-cleanup')

    def stopInvasion(self, task=None):
        if not self.invading:
            # We are not currently invading.
            return False

        # Stop the invasion timeout task:
        taskMgr.remove('invasionTimeout')

        # Update the invasion tracker on the districts page in the Shticker Book:
        self.air.districtStats.b_setInvasionStatus(0)

        # Revert what was done when the invasion started:
        self.notifyInvasionEnded()
        self.invading = False
        self.start = 0
        self.suitDeptIndex = None
        self.suitTypeIndex = None
        self.flags = 0
        self.total = 0
        self.remaining = 0
        self.flySuits()

        self.sendInvasionStatus()
        return True

    def getSuitName(self):
        if self.suitDeptIndex is not None:
            if self.suitTypeIndex is not None:
                return SuitDNA.getSuitName(self.suitDeptIndex, self.suitTypeIndex)
            else:
                return SuitDNA.suitDepts[self.suitDeptIndex]
        else:
            return SuitDNA.suitHeadTypes[0]

    def notifyInvasionStarted(self):
        msgType = ToontownGlobals.SuitInvasionBegin
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBegin
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionBegin
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionBegin
        self.air.newsManager.sendUpdate(
            'setInvasionStatus',
            [msgType, self.getSuitName(), self.total, self.flags])

    def notifyInvasionEnded(self):
        msgType = ToontownGlobals.SuitInvasionEnd
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionEnd
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionEnd
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionEnd
        self.air.newsManager.sendUpdate(
            'setInvasionStatus', [msgType, self.getSuitName(), 0, self.flags])

    def notifyInvasionUpdate(self):
        self.air.newsManager.sendUpdate(
            'setInvasionStatus',
            [ToontownGlobals.SuitInvasionUpdate, self.getSuitName(),
             self.remaining, self.flags])

    def notifyInvasionBulletin(self, avId):
        msgType = ToontownGlobals.SuitInvasionBulletin
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBulletin
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionBulletin
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionBulletin
        self.air.newsManager.sendUpdateToAvatarId(
            avId, 'setInvasionStatus',
            [msgType, self.getSuitName(), self.remaining, self.flags])

    def flySuits(self):
        for suitPlanner in self.air.suitPlanners.values():
            suitPlanner.flySuits()

    def handleSuitDefeated(self):
        self.remaining -= 1
        if self.remaining == 0:
            self.stopInvasion()
        elif self.remaining == (self.total/2):
            self.notifyInvasionUpdate()
        self.sendInvasionStatus()

    def handleStartInvasion(self, shardId, *args):
        if shardId == self.air.ourChannel:
            self.startInvasion(*args)

    def handleStopInvasion(self, shardId):
        if shardId == self.air.ourChannel:
            self.stopInvasion()

    def sendInvasionStatus(self):
        if self.invading:
            if self.suitDeptIndex is not None:
                if self.suitTypeIndex is not None:
                    type = SuitBattleGlobals.SuitAttributes[self.getSuitName()]['name']
                else:
                    type = SuitDNA.getDeptFullname(self.getSuitName())
            else:
                type = None
            status = {
                'invasion': {
                    'type': type,
                    'flags': self.flags,
                    'remaining': self.remaining,
                    'total': self.total,
                    'start': self.start
                }
            }
        else:
            status = {'invasion': None}
        self.air.netMessenger.send('shardStatus', [self.air.ourChannel, status])