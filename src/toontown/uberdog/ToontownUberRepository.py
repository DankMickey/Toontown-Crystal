from direct.distributed.PyDatagram import *
import urlparse
from otp.distributed.OtpDoGlobals import *
from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
import toontown.minigame.MinigameCreatorAI


if config.GetBool('want-rpc-server', False):
    from toontown.rpc.ToontownRPCServer import ToontownRPCServer
    from toontown.rpc.ToontownRPCHandler import ToontownRPCHandler

class ToontownUberRepository(ToontownInternalRepository):
    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')

        self.notify.setInfo(True)

    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        rootObj = DistributedDirectoryAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        if config.GetBool('want-rpc-server', False):
            endpoint = config.GetString('rpc-server-endpoint', 'http://localhost:8080/')
            self.rpcServer = ToontownRPCServer(endpoint, ToontownRPCHandler(self))
            self.rpcServer.start(useTaskChain=True)

        self.createGlobals()
        self.notify.info('Done.')

    def createGlobals(self):
        """
        Create "global" objects.
        """

        self.csm = simbase.air.generateGlobalObject(OTP_DO_ID_CLIENT_SERVICES_MANAGER, 'ClientServicesManager')
        self.chatAgent = simbase.air.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER, 'ChatAgent')
        self.friendsManager = simbase.air.generateGlobalObject(OTP_DO_ID_ttcy_FRIENDS_MANAGER, 'ttcyFriendsManager')
        self.globalPartyMgr = simbase.air.generateGlobalObject(OTP_DO_ID_GLOBAL_PARTY_MANAGER, 'GlobalPartyManager')
        self.groupManager = simbase.air.generateGlobalObject(OPT_DO_ID_GROUP_MANAGER, 'GroupManager')

