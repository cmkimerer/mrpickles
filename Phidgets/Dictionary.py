"""Copyright 2008 Phidgets Inc.
This work is licensed under the Creative Commons Attribution 2.5 Canada License. 
To view a copy of this license, visit http://creativecommons.org/licenses/by/2.5/ca/
"""

__author__ = 'Adam Stelmack'
__version__ = '2.1.4'
__date__ = 'May 02 2008'

from threading import *
from ctypes import *
from PhidgetException import *
from Events.Events import *
from Phidget import *
import sys

class DictionaryKeyChangeReason:
    """This is an enumeration for the key change reasons to make checks and setting more straightforward and readable
    """
    PHIDGET_DICTIONARY_VALUE_CHANGED = 1
    PHIDGET_DICTIONARY_ENTRY_ADDED = 2
    PHIDGET_DICTIONARY_ENTRY_REMOVING = 3
    PHIDGET_DICTIONARY_CURRENT_VALUE = 4

class KeyListener:
    """This class represents a key listener.
    
    This key listener is used, along with the Dictionary object,
    to set up listener for specific keys, or groups of keys.
    Events are available for key add or change, and for key removal.
    """
    def __init__(self, dict, keyPattern):
        """The Constructor Method for the KeyListener Class
        
        Creates a new key listener, for a specific pattern, on a specific dictionary object.
        """
        self.__dict = dict
        self.__keyPattern = keyPattern
        
        self.__listenerHandle = None
        self.__keyRemoval = None
        self.__keyChange = None
        
        self.__onKeyChange = None
        
        self.dll = dict.dll
        
        if sys.platform == 'win32':
            self.__KEYCHANGEHANDLER = WINFUNCTYPE(c_int, c_long, c_void_p, c_char_p, c_char_p, c_int)
        elif sys.platform == 'darwin' or sys.platform == 'linux2':
            self.__KEYCHANGEHANDLER = CFUNCTYPE(c_int, c_long, c_void_p, c_char_p, c_char_p, c_int)

    def __nativeKeyEvent(self, handle, userptr, key, value, reason):
        k = key
        v = value
        if reason == DictionaryKeyChangeReason.PHIDGET_DICTIONARY_ENTRY_REMOVING:
            if self.__keyChange != None:
                self.__keyChange(KeyChangeEventArgs(k, v, reason))
        else:
            if self.__keyRemoval != None:
                self.__keyRemoval(KeyChangeEventArgs(k, v, reason))
        return 0

    def start(self):
        """Start this key listener.
        
        This method should not be called until the coresponding dictionary is connected.
        
        Exceptions:
            PhidgetException: If this Dictionary is not opened.
        """
        self.__onKeyChange = self.__KEYCHANGEHANDLER(self.__nativeKeyEvent)
        listener = c_int()
        result = self.dll.CPhidgetDictionary_set_OnKeyChange_Handler(self.__dict.handle, byref(listener), c_char_p(self.__keyPattern), self.__onKeyChange, None)
        if result > 0:
            raise PhidgetException(result)
        
        self.__listenerHandle = listener

    def stop(self):
        """Stop this key listener.
        
        Exceptions:
            PhidgetException: If this Dictionary is not opened.
        """
        result = self.dll.CPhidgetDictionary_remove_OnKeyChange_Handler(self.__listenerHandle)
        if result > 0:
            raise PhidgetException(result)
        
        self.__listenerHandle = None

    def setKeyChangeHandler(self, keyChangeHandler):
        """Sets the KeyChange event handler.
        
        Parameters:
            keyChangeHandler: hook to the keyChangeHandler callback function.
        """
        self.__keyChange = keyChangeHandler

    def setKeyRemovalListener(self, keyRemovalHandler):
        """Sets the KeyRemoval event handler.
        
        Parameters:
            keyRemovalHandler: hook to the keyRemovalHandler callback function.
        """
        self.__keyRemoval = keyRemovalHandler

    def getDictionary(self):
        """Returns the Dictionary handle that this listener is listening on.
        """
        return self.__dict

class Dictionary:
    """This class represents the Phidget Dictionary.
    
    The Phidget Dictionary is a service provided by the Phidget Webservice.
    The Webservice maintains a centralized dictionary of key-value pairs that can be accessed and changed from any number of clients.
    
    Note that the Webservice uses this dictionary to control access to Phidgets through the openRemote and openRemoteIP interfaces,
    and as such, you should never add or modify a key that starts with /PSK/ or /PCK/, unless you want to explicitly modify Phidget
    specific data -- and this is highly discouraged, as it's very easy to break things. Listening to these keys is fine if so desired.
    
    The intended use for the dictionary is as a central repository for communication and persistent storage of data between several
    client applications. As an example - a higher level interface exposed by one application -- which controls the Phidgets,
    for others to access -- rather then every client talking directly to the Phidgets themselves.
    
    The dictionary makes use of extended regular expressions for key matching.
    """
    def __init__(self):
        """The Constructor Method for the Dictionary Class
        """
        self.handle = c_void_p()
        
        self.__error = None
        self.__serverConnect = None
        self.__serverDisconnect = None
        
        self.__onError = None
        self.__onServerConnect = None
        self.__onServerDisconnect = None
        
        if sys.platform == 'win32':
            self.__ERRORHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_char_p)
            self.__SERVERATTACHHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__SERVERDETACHHANDLER = WINFUNCTYPE(c_int, c_void_p, c_void_p)
        elif sys.platform == 'darwin' or sys.platform == 'linux2':
            self.__ERRORHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_char_p)
            self.__SERVERATTACHHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p)
            self.__SERVERDETACHHANDLER = CFUNCTYPE(c_int, c_void_p, c_void_p)
        
        if sys.platform == 'win32':
            self.dll = windll.LoadLibrary("C:\WINDOWS\system32\phidget21.dll")
        elif sys.platform == 'darwin':
            self.dll = cdll.LoadLibrary("/Library/Frameworks/Phidget21.framework/Versions/Current/Phidget21")
        elif sys.platform == 'linux2':
            self.dll = cdll.LoadLibrary("/usr/lib/libphidget21.so")
        else:
            print "Platform not supported"
        
        result = self.dll.CPhidgetDictionary_create(byref(self.handle))
        if result > 0:
            raise PhidgetException(result)

    def __nativeErrorEvent(self, handle, userptr, errorCode, errorMessage):
        if self.__error != None:
            code = errorCode.value
            message = errorMessage.value
            self.__error(ErrorEventArgs(message, code))
            
        return 0

    def setErrorHandler(self, errorhandler):
        """Sets the Error Event Handler.
        
        Parameters:
            errorhandler: hook to the errorhandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__error = errorhandler
        self.__onError = self.__ERRORHANDLER(self.__nativeErrorEvent)
        result = self.dll.CPhidgetDictionary_set_OnError_Handler(self.handle, self.__onError, None)
        if result > 0:
            raise PhidgetException(result)

    def __nativeServerConnectEvent(self, handle, userptr):
        if self.__serverConnect != None:
            self.__serverConnect(ServerConnectArgs(self))
            
        return 0

    def setServerConnectHandler(self, serverConnectHandler):
        """Sets the Server Connect event handler.
        
        The serverConnect handler is a method that will be called when a connection to a server is made.
        
        Parameters:
            serverConnectHandler: hook to the serverConnectHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__serverConnect = serverConnectHandler
        self.__onServerConnect = self.__SERVERATTACHHANDLER(self.__nativeServerConnectEvent)
        result = self.dll.CPhidgetDictionary_set_OnServerConnect_Handler(self.handle, self.__onServerConnect, None)
        if result > 0:
            raise PhidgetException(result)

    def __nativeServerDisconnectEvent(self, handle, usrptr):
        if self.__serverDisconnect != None:
            self.__serverDisconnect(ServerConnectArgs(self))
            
        return 0

    def setServerDisconnectHandler(self, serverDisconnectHandler):
        """Sets the Server Disconnect Event Handler.
        
        The serverDisconnect handler is a method that will be called when a connection to a server is terminated.
        
        Parameters:
            serverDisconnectHandler: hook to the serverDisconnectHandler callback function.
        
        Exceptions:
            PhidgetException
        """
        self.__serverDisconnect = serverDisconnectHandler
        self.__onServerDisconnect = self.__SERVERDETACHHANDLER(self.__nativeServerDisconnectEvent)
        result = self.dll.CPhidgetDictionary_set_OnServerDisconnect_Handler(self.handle, self.__onServerDisconnect, None)
        if result > 0:
            raise PhidgetException(result)

    def closeDictionary(self):
        """Closes this Dictionary.
        
        This will shut down all threads dealing with this Dictionary and you won't recieve any more events.
        
        Exceptions:
            PhidgetException: If this Dictionary is not opened.
        """
        result = self.dll.CPhidgetDictionary_close(self.handle)
        if result > 0:
            description = Phidget.getErrorDescription(result)
            raise PhidgetException(result, description)
        else:
            result = self.dll.CPhidgetDictionary_delete(self.handle)
            if result > 0:
                raise PhidgetException(result)

    def openRemote(self, serverID, password=""):
        """Open this Dictionary remotely using a Server ID, and securely using a password.
        
        This password can be set as a parameter when starting the Phidget Webservice.
        The use of a password is optional and calling the function without providing a password will
        connect normally.
        
        Parameters:
            serverID<string>: ServerID of the Phidget Webservice.
            password<string>: The secure password for the Phidget Webservice.
        
        Exceptions:
            PhidgetException: if the Phidget Webservice cannot be contacted
        """
        result = self.dll.CPhidgetDictionary_openRemote(self.handle, c_char_p(serverID), c_char_p(password))
        if result > 0:
            raise PhidgetException(result)

    def openRemoteIP(self, IPAddress, port, password=""):
        """Open this Dictionary remotely using an IP Address and port, and securely using a password.
        
        This password can be set as a parameter when starting the Phidget Webservice.
        The use of a password is optional and calling the function without providing a password will
        connect normally.
        
        Parameters:
            IPAddress<string>: IP Address or hostname of the Phidget Webservice
            port<int>: Port of the Phidget Webservice
            password<string>: The secure password for the Phidget Webservice
        
        Exceptions:
            PhidgetException: if the Phidget Webservice cannot be contacted
        """
        result = self.dll.CPhidgetDictionary_openRemoteIP(self.handle, c_char_p(IPAddress), c_int(port), c_char_p(password))
        if result > 0:
            raise PhidgetException(result)

    def addKey(self, key, value, persist=True):
        """Adds a new key to the Dictionary, or modifies the value of an existing key.
        
        The key can only contain numbers, letters, "/", ".", "-", "_", and must begin with a letter, "_" or "/".
        The value can contain any value.
        
        The persistent value controls whether a key will stay in the dictionary after the client that created it disconnects.
        If persist == False, the key is removed when the connection closes. Otherwise the key remains in the dictionary until it is explicitly removed.
        
        Specifying the persist parameter is optional and will default to True if not provided when calling this method.
        
        Parameters:
            key<string>: The key to add to the Dictionary.
            value<string>: The value to be associated with the key in the Dictionary.
            persist<boolean>: Flag to specify whether to make this Dictionary entry persistent or not.
        
        Exceptions:
            PhidgetException: if the Phidget Webservice cannot be contacted
        """
        if persist == True:
            persistVal = 1
        else:
            persistVal = 0
        result = self.dll.CPhidgetDictionary_addKey(self.handle, c_char_p(key), c_char_p(value), c_int(persistVal))
        if result > 0:
            raise PhidgetException(result)

    def removeKey(self, pattern):
        """Removes a key, or set of keys, from the Dictionary.
        
        The key name is a regular expressions pattern, and so care must be taken to only have it match the specific keys you want to remove.
        
        Parameters:
            pattern<string>: The regular expression pattern to match to the keys you want to remove from the Dictionary.
        
        Exceptions:
            PhidgetException: if the Phidget Webservice cannot be contacted
        """
        result = self.dll.CPhidgetDictionary_removeKey(self.handle, c_char_p(pattern))
        if result > 0:
            raise PhidgetException(result)

    """
    This function is not yet implemented.
    def getKey(self, key):
        value = c_char_p()
        result = self.dll.CPhidgetDictionary_getKey(self.handle, c_char_p(key), byref(value))
        if result > 0:
            raise PhidgetException(result)
        else:
            return value.value
    """

    def getServerID(self):
        """Returns the Server ID of a Phidget Webservice when this Dictionary was opened as remote.
        
        This is an arbitrary server identifier, independant of IP address and Port.
        
        Returns:
            The ServerID for the webservice <string>.
        
        Exceptions:
            PhidgetException: if this Dictionary was not opened.
        """
        serverID = c_char_p()
        result = self.dll.CPhidgetDictionary_getServerID(self.handle, byref(serverID))
        if result > 0:
            raise PhidgetException(result)
        else:
            return serverID.value

    def getServerAddress(self):
        """Returns the Address of a Phidget Webservice when this Dictionary was opened as remote.
        
        This may be an IP Address or a hostname.
        
        Returns:
            The server address for the webservice <string>.
        
        Exceptions:
            PhidgetException: if this Dictionary was not opened.
        """
        serverAddr = c_char_p()
        port = c_int()
        result = self.dll.CPhidgetDictionary_getServerAddress(self.handle, byref(serverAddr), byref(port))
        if result > 0:
            raise PhidgetException(result)
        else:
            return serverAddr.value

    def getServerPort(self):
        """Returns the Port of a Phidget Webservice when this Dictionary was opened as remote.
        
        Returns:
            The server port for the webservice.
        
        Exceptions:
            PhidgetException: if this Dictionary was not opened.
        """
        serverAddr = c_char_p()
        port = c_int()
        result = self.dll.CPhidgetDictionary_getServerAddress(self.handle, byref(serverAddr), byref(port))
        if result > 0:
            raise PhidgetException(result)
        else:
            return port.value

    def isAttachedToServer(self):
        """Gets the attached status of this Dictionary.
        
        Returns:
            The attached status of this Dictionary <boolean>.
        
        Exceptions:
            PhidgetException: if this Dictionary was not opened.
        """
        serverStatus = c_int()
        result = self.dll.CPhidgetDictionary_getServerStatus(self.handle, byref(serverStatus))
        if result > 0:
            raise PhidgetException(result)
        else:
            if serverStatus.value == 1:
                return True
            else:
                return False
