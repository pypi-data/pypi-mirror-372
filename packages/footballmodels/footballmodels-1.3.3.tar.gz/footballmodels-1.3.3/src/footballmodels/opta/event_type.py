from enum import Enum


class EventType(Enum):
    Pass = 1
    OffsidePass = 2
    TakeOn = 3
    Foul = 4
    CornerAwarded = 6
    Tackle = 7
    Interception = 8
    Turnover = 9
    Save = 10
    Claim = 11
    Clearance = 12
    MissedShots = 13
    ShotOnPost = 14
    SavedShot = 15
    Goal = 16
    Card = 17
    SubstitutionOff = 18
    SubstitutionOn = 19
    FormationChange = 40
    Punch = 41
    GoodSkill = 42
    Aerial = 44
    Challenge = 45
    BallRecovery = 49
    Dispossessed = 50
    Error = 51
    KeeperPickup = 52
    CrossNotClaimed = 53
    Smother = 54
    OffsideProvoked = 55
    ShieldBallOpp = 56
    PenaltyFaced = 58
    KeeperSweeper = 59
    ChanceMissed = 60
    BallTouch = 61
    OtherBallContact = 73
    BlockedPass = 74
    Carry = 1001
    OffsideGiven = 10000

    def __lt__(self, other):
        return self.value < other.value
