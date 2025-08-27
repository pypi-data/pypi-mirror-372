from __future__ import annotations

from typing import Optional, Dict

# Zeep is synchronous; we keep calls short and optional.
try:
    from zeep import Client
    from zeep.transports import Transport
    from zeep.wsse.username import UsernameToken
except Exception:  # zeep not installed
    Client = None  # type: ignore
    Transport = None  # type: ignore
    UsernameToken = None  # type: ignore

import requests
import certifi

# Official ONVIF Device WSDL
DEVICE_WSDL = "http://www.onvif.org/ver10/device/wsdl/devicemgmt.wsdl"


def get_device_information(xaddr: str, username: Optional[str] = None, password: Optional[str] = None, timeout: float = 2.0) -> Optional[Dict]:
    """Attempt to fetch ONVIF DeviceInformation from given XAddr.
    Returns a dict with manufacturer/model/firmware/serial/hw if successful, else None.
    This is best-effort and unauthenticated by default.
    """
    if Client is None:
        return None
    try:
        session = requests.Session()
        session.verify = certifi.where()
        session.trust_env = True
        session.timeout = timeout  # type: ignore[attr-defined]
    except Exception:
        session = None
    try:
        transport = Transport(session=session, timeout=timeout) if session else Transport(timeout=timeout)
        client = Client(DEVICE_WSDL, transport=transport)
        # binding name for Device service as per WSDL
        binding = "{http://www.onvif.org/ver10/device/wsdl}DeviceBinding"
        service = client.create_service(binding, xaddr)
        if username and password and UsernameToken is not None:
            # Recreate client with WSSE for authenticated calls
            client = Client(DEVICE_WSDL, transport=transport, wsse=UsernameToken(username, password))
            service = client.create_service(binding, xaddr)
        info = service.GetDeviceInformation()
        # Expected keys: Manufacturer, Model, FirmwareVersion, SerialNumber, HardwareId
        return {
            "Manufacturer": getattr(info, "Manufacturer", None),
            "Model": getattr(info, "Model", None),
            "FirmwareVersion": getattr(info, "FirmwareVersion", None),
            "SerialNumber": getattr(info, "SerialNumber", None),
            "HardwareId": getattr(info, "HardwareId", None),
        }
    except Exception:
        return None


def change_onvif_password(xaddr: str, admin_username: str, admin_password: str, target_username: str, new_password: str, timeout: float = 3.0) -> bool:
    """Attempt to change an ONVIF user's password via Device.SetUser.

    Notes:
    - Requires admin privileges on the device.
    - Best-effort. Many vendors restrict or vary behavior.
    - Returns True on apparent success, False otherwise.
    """
    if Client is None or UsernameToken is None:
        return False
    try:
        session = requests.Session()
        session.verify = certifi.where()
        session.trust_env = True
        session.timeout = timeout  # type: ignore[attr-defined]
    except Exception:
        session = None
    try:
        transport = Transport(session=session, timeout=timeout) if session else Transport(timeout=timeout)
        binding = "{http://www.onvif.org/ver10/device/wsdl}DeviceBinding"
        client = Client(DEVICE_WSDL, transport=transport, wsse=UsernameToken(admin_username, admin_password))
        service = client.create_service(binding, xaddr)
        # Fetch current users
        try:
            users = service.GetUsers()
        except Exception:
            users = []
        # Build user list for SetUser: update the matching target user
        factory = client.type_factory('ns0')  # ns0: onvif Device types
        new_users = []
        found = False
        for u in users or []:
            name = getattr(u, 'Username', None)
            level = getattr(u, 'UserLevel', 'Administrator')
            if name == target_username:
                found = True
                new_users.append(factory.User(Username=name, Password=new_password, UserLevel=level))
            else:
                # Keep existing user unchanged (some devices require full list)
                # Redact password if not provided by device by passing None
                pw = getattr(u, 'Password', None)
                if pw is None:
                    new_users.append(factory.User(Username=name, UserLevel=level))
                else:
                    new_users.append(factory.User(Username=name, Password=pw, UserLevel=level))
        if not found:
            # Try to create the user instead
            try:
                service.CreateUsers([factory.User(Username=target_username, Password=new_password, UserLevel='Administrator')])
                return True
            except Exception:
                return False
        # Apply SetUser with updated password
        service.SetUser(new_users)
        return True
    except Exception:
        return False
