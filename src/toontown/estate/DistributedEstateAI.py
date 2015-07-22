from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.toonbase import ToontownGlobals
from toontown.fishing.DistributedFishingPondAI import DistributedFishingPondAI
from toontown.fishing.DistributedFishingTargetAI import DistributedFishingTargetAI
from toontown.fishing.DistributedPondBingoManagerAI import DistributedPondBingoManagerAI
from toontown.fishing import FishingTargetGlobals
from toontown.safezone.DistributedFishingSpotAI import DistributedFishingSpotAI
from toontown.safezone.SZTreasurePlannerAI import SZTreasurePlannerAI
from toontown.safezone import DistributedTreasureAI
from toontown.safezone import TreasureGlobals
from DistributedCannonAI import *
from DistributedTargetAI import *
import CannonGlobals
import TableGlobals
import HouseGlobals
import GardenGlobals
from DistributedGardenPlotAI import DistributedGardenPlotAI
from DistributedGardenBoxAI import DistributedGardenBoxAI
from DistributedFlowerAI import DistributedFlowerAI
from DistributedGagTreeAI import DistributedGagTreeAI
from DistributedStatuaryAI import DistributedStatuaryAI
from DistributedToonStatuaryAI import DistributedToonStatuaryAI
import time
import random
from toontown.fishing import FishGlobals
from toontown.parties.DistributedPartyJukeboxActivityAI import DistributedPartyJukeboxActivityAI

class Rental:

    def __init__(self, estate):
        self.estate = estate
        self.objects = set()

    def destroy(self):
        del self.estate
        for obj in self.objects:
            if not obj.isDeleted():
                obj.requestDelete()
                taskMgr.remove(obj.uniqueName('delete'))
        self.objects = set()

class CannonRental(Rental):

    def __init__(self, estate):
        Rental.__init__(self, estate)

    def generateObjects(self):
        target = DistributedTargetAI(self.estate.air)
        target.generateWithRequired(self.estate.zoneId)

        for drop in CannonGlobals.cannonDrops:
            cannon = DistributedCannonAI(self.estate.air)
            cannon.setEstateId(self.estate.doId)
            cannon.setTargetId(target.doId)
            cannon.setPosHpr(*drop)
            cannon.generateWithRequired(self.estate.zoneId)
            self.objects.add(cannon)

        self.generateTreasures()
        self.estate.b_setClouds(1)

    def destroy(self):
        self.estate.b_setClouds(0)
        Rental.destroy(self)

    def generateTreasures(self):
        doIds = []
        z = 35

        for i in xrange(20):
            x = random.randint(100, 300) - 200
            y = random.randint(100, 300) - 200
            treasure = DistributedTreasureAI.DistributedTreasureAI(self.estate.air, self, 7, x, y, z)
            treasure.generateWithRequired(self.estate.zoneId)
            self.objects.add(treasure)
            doIds.append(treasure.doId)

        self.estate.sendUpdate("setTreasureIds", [doIds])

    def grabAttempt(self, avId, treasureId):
        av = self.estate.air.doId2do.get(avId)
        if av == None:
            self.estate.air.writeServerEvent('suspicious', avId, 'TreasurePlannerAI.grabAttempt unknown avatar')
            self.estate.notify.warning('avid: %s does not exist' % avId)
            return

        treasure = self.estate.air.doId2do.get(treasureId)
        if self.validAvatar(av):
            treasure.d_setGrab(avId)
            self.deleteTreasureSoon(treasure)
        else:
            treasure.d_setReject()

    def deleteTreasureSoon(self, treasure):
        taskName = treasure.uniqueName('delete')
        taskMgr.doMethodLater(5, self.__deleteTreasureNow, taskName, extraArgs=(treasure, taskName))

    def __deleteTreasureNow(self, treasure, taskName):
        treasure.requestDelete()

    def validAvatar(self, av):
        if av.getMaxHp() == av.getHp():
            return 0

        av.toonUp(3)
        return 1

# Once we make rental game tables.
class TableRental(Rental):

    def __init__(self, estate):
        Rental.__init__(self, estate)

    def generateObjects(self):
        for drop in TableGlobals.tableDrops:
            table = None
            table.setEstateId(self.estate.doId)
            table.setPosHpr(*drop)
            table.generateWithRequired(self.estate.zoneId)
            self.objects.add(table)

    def destroy(self):
        Rental.destroy(self)

class DistributedEstateAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedEstateAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.toons = [0, 0, 0, 0, 0, 0]
        self.items = [[], [], [], [], [], []]
        self.boxes = [[], [], [], [], [], []]
        self.plots = [[], [], [], [], [], []]
        self.decorData = []
        self.cloudType = 0
        self.dawnTime = 0
        self.lastEpochTimestamp = 0
        self.rentalType = 0
        self.rentalHandle = None
        self.rentalTimestamp = 0
        self.houses = [None] * 6
        self.pond = None
        self.spots = []
        self.targets = []
        self.jukebox = None
        self.owner = None

    @property
    def hostId(self):
        return 1000000001

    def generate(self):
        DistributedObjectAI.generate(self)

        self.pond = DistributedFishingPondAI(simbase.air)
        self.pond.setArea(ToontownGlobals.MyEstate)
        self.pond.generateWithRequired(self.zoneId)

        for i in xrange(FishingTargetGlobals.getNumTargets(ToontownGlobals.MyEstate)):
            target = DistributedFishingTargetAI(self.air)
            target.setPondDoId(self.pond.getDoId())
            target.generateWithRequired(self.zoneId)
            self.targets.append(target)

        spot = DistributedFishingSpotAI(self.air)
        spot.setPondDoId(self.pond.getDoId())
        spot.setPosHpr(49.1029, -124.805, 0.344704, 90, 0, 0)
        spot.generateWithRequired(self.zoneId)
        self.spots.append(spot)

        spot = DistributedFishingSpotAI(self.air)
        spot.setPondDoId(self.pond.getDoId())
        spot.setPosHpr(46.5222, -134.739, 0.390713, 75, 0, 0)
        spot.generateWithRequired(self.zoneId)
        self.spots.append(spot)

        spot = DistributedFishingSpotAI(self.air)
        spot.setPondDoId(self.pond.getDoId())
        spot.setPosHpr(41.31, -144.559, 0.375978, 45, 0, 0)
        spot.generateWithRequired(self.zoneId)
        self.spots.append(spot)

        spot = DistributedFishingSpotAI(self.air)
        spot.setPondDoId(self.pond.getDoId())
        spot.setPosHpr(46.8254, -113.682, 0.46015, 135, 0, 0)
        spot.generateWithRequired(self.zoneId)
        self.spots.append(spot)

        self.jukebox = DistributedPartyJukeboxActivityAI(
            self.air,
            self.doId,
            (0, 0, 0, 0)
        )
        self.jukebox.generateWithRequired(self.zoneId)
        self.jukebox.sendUpdate('setX', [-21.8630])
        self.jukebox.sendUpdate('setY', [-154.669])
        self.jukebox.sendUpdate('setH', [148.7050])
        self.jukebox.sendUpdate('unloadSign')

        self.createTreasurePlanner()

    def generateRegisteredObjects(self, slot):
        if len(self.plots[slot]) > 0:
            for item in self.items[slot]:
                plotData = GardenGlobals.estatePlots[slot][item[0]]
                if item[1] == GardenGlobals.FLOWER_TYPE:
                    newItem = DistributedFlowerAI(self.air)
                    newItem.setEstate(self.doId)
                    newItem.setOwnerPlot(self.plots[slot][item[0]].doId)
                    newItem.setPlot(item[0])
                    newItem.setHeading(plotData[2])
                    newItem.setPosition(plotData[0], plotData[1], 1.3)
                    newItem.setOwnerIndex(slot)
                    newItem.setWaterLevel(item[4])
                    newItem.setGrowthLevel(item[5])
                    newItem.setTypeIndex(item[2])
                    newItem.setVariety(item[3])
                elif item[1] == GardenGlobals.GAG_TREE_TYPE:
                    newItem = DistributedGagTreeAI(self.air)
                    newItem.setEstate(self.doId)
                    newItem.setOwnerPlot(self.plots[slot][item[0]].doId)
                    newItem.setPlot(item[0])
                    newItem.setHeading(plotData[2])
                    newItem.setPosition(plotData[0], plotData[1], 1.3)
                    newItem.setOwnerIndex(slot)
                    newItem.setTypeIndex(item[2])
                    newItem.setWaterLevel(item[4])
                    newItem.setGrowthLevel(item[5])
                elif item[1] == GardenGlobals.STATUARY_TYPE:
                    newItem = DistributedStatuaryAI(self.air)
                    newItem.setEstate(self.doId)
                    newItem.setOwnerPlot(self.plots[slot][item[0]].doId)
                    newItem.setPlot(item[0])
                    newItem.setHeading(plotData[2])
                    newItem.setPosition(plotData[0], plotData[1], 1.3)
                    newItem.setOwnerIndex(slot)
                    newItem.setTypeIndex(item[2])
                    newItem.setWaterLevel(item[4])
                    newItem.setGrowthLevel(item[5])
                elif item[1] == GardenGlobals.TOON_STATUARY_TYPE:
                    newItem = DistributedToonStatuaryAI(self.air)
                    newItem.setEstate(self.doId)
                    newItem.setOwnerPlot(self.plots[slot][item[0]].doId)
                    newItem.setPlot(item[0])
                    newItem.setHeading(plotData[2])
                    newItem.setPosition(plotData[0], plotData[1], 1.3)
                    newItem.setOwnerIndex(slot)
                    newItem.setTypeIndex(item[2])
                    newItem.setWaterLevel(item[4])
                    newItem.setGrowthLevel(item[5])
                    newItem.setOptional(item[6])
                else:
                    continue
                newItem.generateWithRequired(self.zoneId)
                self.plots[slot][item[0]].planted = newItem
                self.plots[slot][item[0]].sendUpdate('plantedItem', [newItem.doId])
                self.plots[slot][item[0]].sendUpdate('setMovie', [GardenGlobals.MOVIE_PLANT, 999999999])
                        

    def destroy(self):
        for house in self.houses:
            if house:
                house.requestDelete()
        del self.houses[:]
        
        if self.pond:
            self.pond.requestDelete()
            for spot in self.spots:
                spot.requestDelete()
            for target in self.targets:
                target.requestDelete()

        if self.jukebox:
            self.jukebox.requestDelete()

        if self.treasurePlanner:
            self.treasurePlanner.stop()

        if self.rentalHandle:
            self.rentalHandle.destroy()
            self.rentalHandle = None

        self.requestDelete()

    def setEstateReady(self):
        pass

    def setClientReady(self):
        self.sendUpdate('setEstateReady', [])

    def setClosestHouse(self, todo0):
        pass

    def setTreasureIds(self, todo0):
        pass

    def createTreasurePlanner(self):
        treasureType, healAmount, spawnPoints, spawnRate, maxTreasures = TreasureGlobals.SafeZoneTreasureSpawns[ToontownGlobals.MyEstate]
        self.treasurePlanner = SZTreasurePlannerAI(self.zoneId, treasureType, healAmount, spawnPoints, spawnRate, maxTreasures)
        self.treasurePlanner.start()

    def requestServerTime(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'setServerTime', [time.time() % HouseGlobals.DAY_NIGHT_PERIOD])

    def setServerTime(self, todo0):
        pass

    def setDawnTime(self, dawnTime):
        self.dawnTime = dawnTime

    def d_setDawnTime(self, dawnTime):
        self.sendUpdate('setDawnTime', [dawnTime])

    def b_setDawnTime(self, dawnTime):
        self.setDawnTime(dawnTime)
        self.d_setDawnTime(dawnTime)

    def getDawnTime(self):
        return self.dawnTime

    def placeOnGround(self, todo0):
        pass

    def setDecorData(self, decorData):
        self.decorData = decorData

    def d_setDecorData(self, decorData):
        self.sendUpdate('setDecorData', [decorData])

    def b_setDecorData(self, decorData):
        self.setDecorData(decorData)
        self.d_setDecorData(decorData)

    def getDecorData(self):
        return self.decorData

    def setLastEpochTimeStamp(self, last):
        self.lastEpochTimestamp = last

    def d_setLastEpochTimeStamp(self, last):
        self.sendUpdate('setLastEpochTimeStamp', [last])

    def b_setLastEpochTimeStamp(self, last):
        self.setLastEpochTimeStamp(last)
        self.d_setLastEpochTimeStamp(last)

    def getLastEpochTimeStamp(self):
        return self.lastEpochTimestamp

    def setRentalTimeStamp(self, rental):
        self.rentalTimestamp = rental

    def d_setRentalTimeStamp(self, rental):
        self.sendUpdate('setRentalTimeStamp', [rental])

    def b_setRentalTimeStamp(self, rental):
        self.setRentalTimeStamp(rental)
        self.d_setRentalTimeStamp(rental)

    def getRentalTimeStamp(self):
        return self.rentalTimestamp

    def b_setRentalType(self, type):
        self.d_setRentalType(type)
        self.setRentalType(type)

    def d_setRentalType(self, type):
        self.sendUpdate("setRentalType", [type])

    def setRentalType(self, type):
        expirestamp = self.getRentalTimeStamp()
        if expirestamp == 0:
            expire = 0
        else:
            expire = int(expirestamp - time.time())

        if expire < 0:
            self.rentalType = 0
            self.d_setRentalType(0)
            self.b_setRentalTimeStamp(0)
        else:
            if self.rentalType == type:
                return

            self.rentalType = type
            if self.rentalHandle:
                self.rentalHandle.destroy()
                self.rentalHandle = None

            if self.rentalType == ToontownGlobals.RentalCannon:
                self.rentalHandle = CannonRental(self)
            elif self.rentalType == ToontownGlobals.RentalGameTable:
                self.rentalHandle = TableRental(self)
            else:
                self.notify.warning('Unknown rental %s' % self.rentalType)
                return

            self.rentalHandle.generateObjects()

    def getRentalType(self):
        return self.rentalType

    def rentItem(self, rentType, duration):
        self.rentalType = rentType
        self.b_setRentalTimeStamp(time.time() + duration * 60)
        self.b_setRentalType(rentType)

    def setSlot0ToonId(self, id):
        self.toons[0] = id

    def d_setSlot0ToonId(self, id):
        self.sendUpdate('setSlot0ToonId', [id])

    def b_setSlot0ToonId(self, id):
        self.setSlot0ToonId(id)
        self.d_setSlot0ToonId(id)

    def getSlot0ToonId(self):
        return self.toons[0]

    def setSlot0Items(self, items):
        self.items[0] = items

    def d_setSlot0Items(self, items):
        self.sendUpdate('setSlot0Items', [items])

    def b_setSlot0Items(self, items):
        self.setSlot0Items(items)
        self.d_setSlot0Items(items)

    def getSlot0Items(self):
        return self.items[0]

    def setSlot1ToonId(self, id):
        self.toons[1] = id

    def d_setSlot1ToonId(self, id):
        self.sendUpdate('setSlot1ToonId', [id])

    def b_setSlot1ToonId(self, id):
        self.setSlot1ToonId(id)
        self.d_setSlot1ToonId(id)

    def getSlot1ToonId(self):
        return self.toons[1]

    def setSlot1Items(self, items):
        self.items[1] = items

    def d_setSlot1Items(self, items):
        self.sendUpdate('setSlot1Items', [items])

    def b_setSlot1Items(self, items):
        self.setSlot1Items(items)
        self.d_setSlot1Items(items)

    def getSlot1Items(self):
        return self.items[1]

    def setSlot2ToonId(self, id):
        self.toons[2] = id

    def d_setSlot2ToonId(self, id):
        self.sendUpdate('setSlot2ToonId', [id])

    def b_setSlot2ToonId(self, id):
        self.setSlot2ToonId(id)
        self.d_setSlot2ToonId(id)

    def getSlot2ToonId(self):
        return self.toons[2]

    def setSlot2Items(self, items):
        self.items[2] = items

    def d_setSlot2Items(self, items):
        self.sendUpdate('setSlot2Items', [items])

    def b_setSlot2Items(self, items):
        self.setSlot2Items(items)
        self.d_setSlot2Items(items)

    def getSlot2Items(self):
        return self.items[2]

    def setSlot3ToonId(self, id):
        self.toons[3] = id

    def d_setSlot3ToonId(self, id):
        self.sendUpdate('setSlot3ToonId', [id])

    def b_setSlot3ToonId(self, id):
        self.setSlot3ToonId(id)
        self.d_setSlot3ToonId(id)

    def getSlot3ToonId(self):
        return self.toons[3]

    def setSlot3Items(self, items):
        self.items[3] = items

    def d_setSlot3Items(self, items):
        self.sendUpdate('setSlot3Items', [items])

    def b_setSlot3Items(self, items):
        self.setSlot3Items(items)
        self.d_setSlot3Items(items)

    def getSlot3Items(self):
        return self.items[3]

    def setSlot4ToonId(self, id):
        self.toons[4] = id

    def d_setSlot4ToonId(self, id):
        self.sendUpdate('setSlot4ToonId', [id])

    def b_setSlot5ToonId(self, id):
        self.setSlot4ToonId(id)
        self.d_setSlot4ToonId(id)

    def getSlot4ToonId(self):
        return self.toons[4]

    def setSlot4Items(self, items):
        self.items[4] = items

    def d_setSlot4Items(self, items):
        self.sendUpdate('setSlot4Items', [items])

    def b_setSlot4Items(self, items):
        self.setSlot4Items(items)
        self.d_setSlot4Items(items)

    def getSlot4Items(self):
        return self.items[4]

    def setSlot5ToonId(self, id):
        self.toons[5] = id

    def d_setSlot5ToonId(self, id):
        self.sendUpdate('setSlot5ToonId', [id])

    def b_setSlot5ToonId(self, id):
        self.setSlot5ToonId(id)
        self.d_setSlot5ToonId(id)

    def getSlot5ToonId(self):
        return self.toons[5]

    def setSlot5Items(self, items):
        self.items[5] = items

    def d_setSlot5Items(self, items):
        self.sendUpdate('setSlot5Items', [items])

    def b_setSlot5Items(self, items):
        self.setSlot5Items(items)
        self.d_setSlot5Items(items)

    def getSlot5Items(self):
        return self.items[5]

    def setIdList(self, idList):
        for i in xrange(len(idList)):
            if i >= 6:
                return
            self.toons[i] = idList[i]

    def d_setIdList(self, idList):
        self.sendUpdate('setIdList', [idList])

    def b_setIdList(self, idList):
        self.setIdList(idList)
        self.d_setIdList(idList)

    def completeFlowerSale(self, todo0):
        pass

    def completeFishSale(self, sell):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av:
            if sell:
                trophyResult = self.air.fishManager.creditFishTank(av)
                if trophyResult:
                    self.sendUpdateToAvatarId(avId, 'thankSeller', [ToontownGlobals.FISHSALE_TROPHY, len(av.fishCollection), FishGlobals.getTotalNumFish()])
                else:
                    self.sendUpdateToAvatarId(avId, 'thankSeller', [ToontownGlobals.FISHSALE_COMPLETE, 0, 0])
            else:
                self.sendUpdateToAvatarId(avId, 'thankSeller', [ToontownGlobals.FISHSALE_NONE, 0, 0])

    def awardedTrophy(self, todo0):
        pass

    def setClouds(self, clouds):
        self.cloudType = clouds

    def d_setClouds(self, clouds):
        self.sendUpdate('setClouds', [clouds])

    def b_setClouds(self, clouds):
        self.setClouds(clouds)
        self.d_setClouds(clouds)

    def getClouds(self):
        return self.cloudType

    def cannonsOver(self):
        pass

    def gameTableOver(self):
        pass

    def placeStarterGarden(self, avatar):
        avId = avatar.doId
        slot = self.toons.index(avId)
        plotPos = GardenGlobals.estatePlots[slot]
        boxPos = GardenGlobals.estateBoxes[slot]
        for p, n in enumerate(boxPos):
            x, y, h, i = n
            newBox = DistributedGardenBoxAI(self.air)
            newBox.setEstate(self.doId)
            newBox.setTypeIndex(i)
            newBox.setPlot(p)
            newBox.setOwnerIndex(slot)
            newBox.setPosition(x, y, 0)
            newBox.setHeading(h)
            newBox.generateWithRequired(self.zoneId)
            self.boxes[slot].append(newBox)
        for p, n in enumerate(plotPos):
            i = n[3]
            if i in [GardenGlobals.GAG_TREE_TYPE, GardenGlobals.STATUARY_TYPE]:
                x, y, h = n[:3]
                newPlot = DistributedGardenPlotAI(self.air)
                newPlot.setEstate(self.doId)
                newPlot.setPlot(p)
                newPlot.setOwnerIndex(slot)
                newPlot.setPosition(x, y, 0)
                newPlot.setHeading(h)
                newPlot.generateWithRequired(self.zoneId)
                self.plots[slot].append(newPlot)
            elif i == GardenGlobals.FLOWER_TYPE:
                x, y, h = n[:3]
                newPlot = DistributedGardenPlotAI(self.air)
                newPlot.setEstate(self.doId)
                newPlot.setPlot(p)
                newPlot.setOwnerIndex(slot)
                newPlot.setPosition(x, y, 1.3)
                newPlot.setHeading(h)
                newPlot.generateWithRequired(self.zoneId)
                self.plots[slot].append(newPlot)
        self.generateRegisteredObjects(slot)

    def updateToons(self):
        self.d_setSlot0ToonId(self.toons[0])
        self.d_setSlot1ToonId(self.toons[1])
        self.d_setSlot2ToonId(self.toons[2])
        self.d_setSlot3ToonId(self.toons[3])
        self.d_setSlot4ToonId(self.toons[4])
        self.d_setSlot5ToonId(self.toons[5])
        self.sendUpdate('setIdList', [self.toons])

    def updateItems(self):
        self.d_setSlot0Items(self.items[0])
        self.d_setSlot1Items(self.items[1])
        self.d_setSlot2Items(self.items[2])
        self.d_setSlot3Items(self.items[3])
        self.d_setSlot4Items(self.items[4])
        self.d_setSlot5Items(self.items[5])
