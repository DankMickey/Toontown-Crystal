import math
from pandac.PandaModules import Point3
from toontown.toonbase import ToontownGlobals
InputTimeout = 15
TireMovieTimeout = 120
MinWall = (-20.0, -15.0)
MaxWall = (20.0, 15.0)
TireRadius = 1.5
WallMargin = 1 + TireRadius
StartingPositions = (Point3(MinWall[0] + WallMargin, MinWall[1] + WallMargin, TireRadius),
 Point3(MaxWall[0] - WallMargin, MaxWall[1] - WallMargin, TireRadius),
 Point3(MinWall[0] + WallMargin, MaxWall[1] - WallMargin, TireRadius),
 Point3(MaxWall[0] - WallMargin, MinWall[1] + WallMargin, TireRadius))
NumMatches = 3
NumRounds = 2
PointsDeadCenter = {0: 5,
 1: 5,
 2: 5,
 3: 4,
 4: 3}
PointsInCorner = 1
FarthestLength = math.sqrt((MaxWall[0] - TireRadius) * (MaxWall[0] - TireRadius) + (MaxWall[1] - TireRadius) * (MaxWall[1] - TireRadius))
BonusPointsForPlace = (3,
 2,
 1,
 0)
ExpandFeetPerSec = 5
ScoreCountUpRate = 0.15
ShowScoresDuration = 4.0
NumTreasures = {ToontownGlobals.ToontownCentral: 2,
 ToontownGlobals.CrystalDock: 2,
 ToontownGlobals.CrystalGarden: 2,
 ToontownGlobals.Melodyland: 2,
 ToontownGlobals.TheBrrrgh: 1,
 ToontownGlobals.Dreamland: 1}
NumPenalties = {ToontownGlobals.ToontownCentral: 0,
 ToontownGlobals.CrystalDock: 1,
 ToontownGlobals.CrystalGarden: 1,
 ToontownGlobals.Melodyland: 1,
 ToontownGlobals.TheBrrrgh: 2,
 ToontownGlobals.Dreamland: 2}
Obstacles = {ToontownGlobals.ToontownCentral: (),
 ToontownGlobals.CrystalDock: ((0, 0),),
 ToontownGlobals.CrystalGarden: ((MinWall[0] / 2, 0), (MaxWall[0] / 2, 0)),
 ToontownGlobals.Melodyland: ((0, MinWall[1] / 2), (0, MaxWall[1] / 2)),
 ToontownGlobals.TheBrrrgh: ((MinWall[0] / 2, 0),
                             (MaxWall[0] / 2, 0),
                             (0, MinWall[1] / 2),
                             (0, MaxWall[1] / 2)),
 ToontownGlobals.Dreamland: ((MinWall[0] / 2, MinWall[1] / 2),
                                    (MinWall[0] / 2, MaxWall[1] / 2),
                                    (MaxWall[0] / 2, MinWall[1] / 2),
                                    (MaxWall[0] / 2, MaxWall[1] / 2))}
ObstacleShapes = {ToontownGlobals.ToontownCentral: True,
 ToontownGlobals.CrystalDock: True,
 ToontownGlobals.CrystalGarden: True,
 ToontownGlobals.Melodyland: True,
 ToontownGlobals.TheBrrrgh: False,
 ToontownGlobals.Dreamland: False}
