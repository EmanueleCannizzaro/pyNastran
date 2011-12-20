import sys
from struct import pack
from pyNastran.op2.resultObjects.op2_Objects import scalarObject,array

class displacementObject(scalarObject): # approachCode=1, sortCode=0, thermal=0
    def __init__(self,dataCode,iSubcase,dt=None):
        scalarObject.__init__(self,dataCode,iSubcase)
        self.dt = dt
        #print "displacementObject - self.dt=|%s|" %(self.dt)
        ## this could get very bad very quick, but it could be great!
        ## basically it's a way to handle transients without making
        ## a whole new class
        self.gridTypes     = {}
        self.displacements = {}
        self.rotations     = {}
        if dt is not None:
            #assert dt>=0.
            self.addNewTransient()
            self.add = self.addTransient
            #self.addBinary = self.addBinaryTransient
            #self.__repr__ = self.__reprTransient__  # why cant i do this...
            #self.writeOp2 = self.writeOp2Transient
        ###

    def updateDt(self,dataCode,dt):
        self.dataCode = dataCode
        self.applyDataCode()
        if dt is not None:
            self.log.debug("updating %s...%s=%s  iSubcase=%s" %(self.dataCode['name'],self.dataCode['name'],dt,self.iSubcase))
            self.dt = dt
            self.addNewTransient()
        ###

    #def setLoadID(self,loadID):
    #    self.loadID = loadID

    def addNewTransient(self):
        """
        initializes the transient variables
        """
        if self.dt not in self.displacements:
            self.displacements[self.dt] = {}
            self.rotations[self.dt]     = {}

    def addBinary(self,deviceCode,data):
        (nodeID,v1,v2,v3,v4,v5,v6) = unpack('iffffff',data)
        msg = "nodeID=%s v1=%s v2=%s v3=%s" %(nodeID,v1,v2,v3)
        assert 0<nodeID<1000000000, msg
        assert nodeID not in self.displacements

        self.displacements[nodeID] = array([v1,v2,v3]) # dx,dy,dz
        self.rotations[nodeID]     = array([v4,v5,v6]) # rx,ry,rz
    ###

    def add(self,nodeID,gridType,v1,v2,v3,v4,v5,v6):
        msg = "nodeID=%s gridType=%s v1=%s v2=%s v3=%s" %(nodeID,gridType,v1,v2,v3)
        assert 0<nodeID<1000000000, msg
        #assert nodeID not in self.displacements,'displacementObject - static failure'
        
        if gridType==1:
            gridType = 'G'
        elif gridType==2:
            gridType = 'S'
        elif gridType==7:
            gridType = 'L'
        else:
            raise Exception('gridType=%s' %(gridType))
        ###
        self.gridTypes[nodeID] = gridType
        self.displacements[nodeID] = array([v1,v2,v3]) # dx,dy,dz
        self.rotations[nodeID]     = array([v4,v5,v6]) # rx,ry,rz
    ###

    def addTransient(self,nodeID,gridType,v1,v2,v3,v4,v5,v6):
        msg  = "nodeID=%s v1=%s v2=%s v3=%s\n" %(nodeID,v1,v2,v3)
        msg += "          v4=%s v5=%s v6=%s"   %(       v4,v5,v6)
        assert 0<nodeID<1000000000, msg
        #assert nodeID not in self.displacements[self.dt],'displacementObject - transient failure'

        if gridType==1:
            gridType = 'G'
        elif gridType==2:
            gridType = 'S'
        elif gridType==7:
            gridType = 'L'
        else:
            raise Exception('gridType=%s' %(gridType))
        ###

        self.gridTypes[nodeID] = gridType
        self.displacements[self.dt][nodeID] = array([v1,v2,v3]) # dx,dy,dz
        self.rotations[self.dt][nodeID]     = array([v4,v5,v6]) # rx,ry,rz
    ###

    def __reprTransient__(self):
        self.log.debug("Transient...")
        raise Exception('this could be cool...')
        return self.__repr__()

    def writeOp2(self,block3,deviceCode=1):
        """
        creates the binary data for writing the table
        @warning hasnt been tested...
        """
        msg = block3
        for nodeID,displacement in sorted(self.displacements.items()):
            rotation = self.rotations[nodeID]
            (dx,dy,dz) = displacement
            (rx,ry,rz) = rotation
            grid = nodeID*10+deviceCode
            msg += pack('iffffff',grid,dx,dy,dz,rx,ry,rz)
        ###
        return msg

    #def writeOp2Transient(self,block3,deviceCode=1):
    #    """
    #    creates the binary data for writing the table
    #    @warning hasnt been tested...
    #    @warning dt slot needs to be fixed...
    #    """
    #    msg = ''
    #    for dt,displacements in sorted(self.displacements.items()):
    #        XXX = 50 ## this isnt correct... @todo update dt
    #        msg += block3[0:XXX] + pack('i',dt) + block3[XXX+4:]
    #        #msg += '%s = %g\n' %(self.dataCode['name'],dt)
    #
    #        for nodeID,displacement in sorted(displacements.items()):
    #            rotation = self.rotations[nodeID]
    #            (dx,dy,dz) = displacement
    #            (rx,ry,rz) = rotation
    #
    #            grid = nodeID*10+deviceCode
    #            msg += pack('iffffff',grid,dx,dy,dz,rx,ry,rz)
    #        ###
    #    ###
    #    return msg

    def __reprTransient__(self):
        msg = '---TRANSIENT DISPLACEMENTS---\n'
        #msg += '%s = %g\n' %(self.dataCode['name'],self.dt)
        headers = ['Dx','Dy','Dz','Rx','Ry','Rz']
        msg += '%-10s %-8s ' %('NodeID','GridType')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,displacements in sorted(self.displacements.items()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for nodeID,displacement in sorted(displacements.items()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]
                (dx,dy,dz) = displacement
                (rx,ry,rz) = rotation

                msg += '%-10i %-8s ' %(nodeID,gridType)
                vals = [dx,dy,dz,rx,ry,rz]
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %(0)
                    else:
                        msg += '%10.3e ' %(val)
                    ###
                msg += '\n'
            ###
        return msg

    def __repr__(self):
        if self.dt is not None:
            return self.__reprTransient__()

        msg = '---DISPLACEMENTS---\n'
        headers = ['Dx','Dy','Dz','Rx','Ry','Rz']
        msg += '%-10s %-8s ' %('NodeID','GridType')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for nodeID,displacement in sorted(self.displacements.items()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx,dy,dz) = displacement
            (rx,ry,rz) = rotation

            msg += '%-10i %-8s ' %(nodeID,gridType)
            vals = [dx,dy,dz,rx,ry,rz]
            for val in vals:
                if abs(val)<1e-6:
                    msg += '%10s ' %(0)
                else:
                    msg += '%10.3e ' %(val)
                ###
            msg += '\n'
        return msg

class complexDisplacementObject(scalarObject): # approachCode=1, sortCode=0, thermal=0
    def __init__(self,dataCode,iSubcase,freq=None):
        scalarObject.__init__(self,dataCode,iSubcase)
        self.freq = freq
        #print "complexDisplacementObject - self.freq=|%s|" %(self.freq)
        self.gridType      = {}
        self.displacements = {}
        self.rotations     = {}
        self.addNewTransient()

    def updateDt(self,dataCode,freq):
        self.dataCode = dataCode
        self.applyDataCode()
        if freq is not None:
            self.log.debug("updating %s...%s=%s  iSubcase=%s" %(self.dataCode['name'],self.dataCode['name'],dt,self.iSubcase))
            self.freq = freq
            self.addNewTransient()
        ###

    def addNewTransient(self):
        """initializes the transient variables"""
        if self.dt not in self.displacements:
            self.displacements[self.freq] = {}
            self.rotations[self.freq]     = {}

    def add(self,nodeID,gridType,v1r,v1i,v2r,v2i,v3r,v3i,v4r,v4i,v5r,v5i,v6r,v6i):
        #msg = "nodeID=%s v1=%s v2=%s v3=%s" %(nodeID,v1,v2,v3)
        msg = ''
        assert 0<nodeID<1000000000, msg
        #assert nodeID not in self.displacements,'displacementObject - static failure'

        self.displacements[self.freq][nodeID] = [[v1r,v1i],[v2r,v2i],[v3r,v3i]] # dx,dy,dz
        self.rotations[self.freq][nodeID]     = [[v4r,v4i],[v5r,v5i],[v6r,v6i]] # rx,ry,rz
    ###

    def __repr__(self):
        msg = '---COMPLEX DISPLACEMENTS---\n'
        #if self.dt is not None:
        #    msg += '%s = %g\n' %(self.dataCode['name'],self.dt)
        headers = ['DxReal','DxImag','DyReal','DyImag','DzReal','DyImag','RxReal','RxImag','RyReal','RyImag','RzReal','RzImag']
        msg += '%-10s ' %('nodeID')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for freq,displacements in sorted(self.displacements.items()):
            msg += 'freq = %g\n' %(freq)
            #print "freq = ",freq
            #print displacements
            for nodeID,displacement in sorted(displacements.items()):
                rotation = self.rotations[freq][nodeID]
                (dx,dy,dz) = displacement
                (rx,ry,rz) = rotation

                msg += '%-10i ' %(nodeID)
                vals = dx+dy+dz+rx+ry+rz
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %(0)
                    else:
                        msg += '%10.3e ' %(val)
                    ###
                msg += '\n'
            ###
        return msg

class temperatureObject(scalarObject): # approachCode=1, sortCode=0, thermal=1
    def __init__(self,dataCode,iSubcase,dt=None):
        scalarObject.__init__(self,dataCode,iSubcase)
        self.dt = dt
        self.temperatures = {}
        self.gridTypes    = {}
        
        #print "dt = ",self.dt
        if dt is not None:
            #assert dt>=0.
            self.addNewTransient()
            self.isTransient = True
            self.addNewTransient()
            #self.temperatures = {self.dt:{}}
            self.add = self.addTransient
            #self.addBinary = self.addBinaryTransient
            #self.__repr__ = self.__reprTransient__  # why cant i do this...            
        ###

    def updateDt(self,dataCode,dt):
        self.dataCode = dataCode
        self.applyDataCode()
        if dt is not None:
            self.log.debug("updating %s...%s=%s  iSubcase=%s" %(self.name,self.name,dt,self.iSubcase))
            self.dt = dt
            self.addNewTransient()
        ###

    def addNewTransient(self):
        """initializes the transient variables"""
        if self.dt not in self.temperatures:
            self.temperatures[self.dt] = {}

    def add(self,nodeID,gridType,v1,v2=None,v3=None,v4=None,v5=None,v6=None):
        assert 0<nodeID<1000000000, 'nodeID=%s' %(nodeID)
        #assert nodeID not in self.temperatures

        if gridType==1:
            gridType = 'G'
        elif gridType==2:
            gridType = 'S'
        elif gridType==7:
            gridType = 'L'
        else:
            raise Exception('gridType=%s' %(gridType))
        ###

        self.gridTypes[nodeID] = gridType
        self.temperatures[nodeID] = v1

    def addTransient(self,nodeID,gridType,v1,v2=None,v3=None,v4=None,v5=None,v6=None):
        assert 0<nodeID<1000000000, 'nodeID=%s' %(nodeID)
        #assert nodeID not in self.temperatures[self.dt]

        if gridType==1:
            gridType = 'G'
        elif gridType==2:
            gridType = 'S'
        elif gridType==7:
            gridType = 'L'
        else:
            raise Exception('gridType=%s' %(gridType))
        ###

        self.gridTypes[nodeID] = gridType
        self.temperatures[self.dt][nodeID] = v1

    def __reprTransient__(self):
        msg = '---TRANSIENT TEMPERATURE---\n'
        msg += '%-10s %8s %-8s\n' %('NodeID','GridType','Temperature')

        for dt,temperatures in sorted(self.temperatures.items()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for nodeID,T in sorted(temperatures.items()):
                gridType = self.gridTypes[nodeID]
                msg += '%10s %8s ' %(nodeID,gridType)

                if abs(T)<1e-6:
                    msg += '%10s\n' %(0)
                else:
                    msg += '%10g\n' %(T)
                ###
            ###
        return msg

    def writeOp2(self,block3,deviceCode=1):
        """
        creates the binary data for writing the table
        @warning hasnt been tested...
        """
        msg = block3
        for nodeID,T in sorted(self.temperatures.items()):
            grid = nodeID*10+deviceCode
            msg += pack('iffffff',grid,T,0,0,0,0,0)
        ###
        return msg

    def writeOp2Transient(self,block3,deviceCode=1):
        """
        creates the binary data for writing the table
        @warning hasnt been tested...
        @warning dt slot needs to be fixed...
        """
        msg = ''
        for dt,temperatures in sorted(self.temperatures.items()):
            XXX = 50 ## this isnt correct... @todo update dt
            msg += block3[0:XXX] + pack('i',dt) + block3[XXX+4:]
            #msg += '%s = %g\n' %(self.dataCode['name'],dt)
    
            for nodeID,T in sorted(temperatures.items()):
                grid = nodeID*10+deviceCode
                msg += pack('iffffff',grid,T,0,0,0,0,0)
            ###
        ###
        return msg

    def __repr__(self):
        if self.isTransient:
            return self.__reprTransient__()

        msg = '---TEMPERATURE---\n'
        msg += '%-10s %8s %-8s\n' %('NodeID','GridType','Temperature')
        #print "self.dataCode=",self.dataCode
        #print "self.temperatures=",self.temperatures
        for nodeID,T in sorted(self.temperatures.items()):
            gridType = self.gridTypes[nodeID]
            msg += '%10s %8s ' %(nodeID,gridType)

            if abs(T)<1e-6:
                msg += '%10s\n' %(0)
            else:
                msg += '%10g\n' %(T)
            ###
        return msg

#---------------------------------------------------------------------------------
#class staticFluxObj(scalarObject): # approachCode=1, tableCode=3 - whatever the static version of this is...

class fluxObject(scalarObject): # approachCode=1, tableCode=3, thermal=1
    def __init__(self,dataCode,iSubcase,dt=None):
        scalarObject.__init__(self,dataCode,iSubcase)

        self.dt = dt
        self.fluxes = {}
        if dt is not None:
            self.fluxes = {}
            self.isTransient = True
            raise Exception('transient is supported yet...')

    def add(self,nodeID,gridType,v1,v2,v3,v4=None,v5=None,v6=None):
        assert 0<nodeID<1000000000, 'nodeID=%s' %(nodeID)
        assert nodeID not in self.fluxes
        self.fluxes[nodeID] = array([v1,v2,v3])

    def writeOp2(self,block3,deviceCode=1):
        """
        creates the binary data for writing the table
        @warning hasnt been tested...
        """
        msg = block3
        for nodeID,flux in sorted(self.fluxes.items()):
            grid = nodeID*10+deviceCode
            msg += pack('iffffff',grid,flux[0],flux[1],flux[2],0,0,0)
        ###
        return msg

    def __repr__(self):
        if self.isTransient:
            return self.__reprTransient__()

        msg = '---HEAT FLUX---\n'
        msg += '%-10s %-8s %-8s %-8s\n' %('NodeID','xFlux','yFlux','zFlux')
        for nodeID,flux in sorted(self.fluxes.items()):
            msg += '%10i ' %(nodeID)

            for val in flux:
                if abs(val)<1e-6:
                    msg += '%10s' %(0)
                else:
                    msg += '%10.3e ' %(val)
                ###
            msg += '\n'
        return msg

#---------------------------------------------------------------------------------

class nonlinearDisplacementObject(scalarObject): # approachCode=10, sortCode=0, thermal=0
    def __init__(self,dataCode,iSubcase,loadStep):
        scalarObject.__init__(self,dataCode,iSubcase)
        self.dataCode = dataCode
        self.applyDataCode()
        self.loadStep = loadStep
        
        assert loadStep>=0.
        self.displacements = {loadStep: {}}
        raise Exception('not implemented')

class nonlinearTemperatureObject(scalarObject): # approachCode=10, sortCode=0, thermal=1
    def __init__(self,dataCode,iSubcase,loadStep):
        raise Exception('disabled...')
        scalarObject.__init__(self,dataCode,iSubcase)
        self.dataCode = dataCode
        self.applyDataCode()
        self.loadStep = loadStep
        
        assert loadStep>=0.
        self.temperatures = {loadStep: {}}

    def updateDt(self,dataCode,loadStep):
        self.dataCode = dataCode
        self.applyDataCode()
        assert loadStep>=0.
        self.loadStep = loadStep
        self.temperatures[loadStep] = {}

    def add(self,nodeID,gridType,v1,v2,v3,v4,v5,v6): # addTransient
        #msg = "nodeID=%s v1=%s v2=%s v3=%s v4=%s v5=%s v6=%s" %(nodeID,v1,v2,v3,v4,v5,v6)
        msg = "nodeID=%s v1=%s" %(nodeID,v1)
        #print msg
        assert 0<nodeID<1000000000, msg
        assert nodeID not in self.temperatures[self.loadStep]
        
        self.temperatures[self.loadStep][nodeID] = v1 # T
    ###

    def __repr__(self):
        msg = '---NONLINEAR TEMPERATURE VECTOR---\n'
        if self.loadStep is not None:
            msg += '%s = %g\n' %(self.dataCode['name'],self.loadStep)
        headers = ['Temperature']
        msg += '%10s ' %('GRID')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,temps in sorted(self.temperatures.items()):
            for nodeID,T in sorted(temps.items()):
                msg += '%10i ' %(nodeID)
                if abs(T)<1e-6:
                    msg += '%10s ' %(0)
                else:
                    msg += '%10.3f ' %(T)
                ###
                msg += '\n'
            ###
        return msg
