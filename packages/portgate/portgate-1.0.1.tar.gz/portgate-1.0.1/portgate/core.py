import socket
from typing import List, Dict, Any, Optional
import miniupnpc

from .exceptions import PortGateError


class PortGate:
    
    def __init__(self):
        self.upnp = miniupnpc.UPnP()
        self._discover()
        
    def _discover(self):
        try:
            self.upnp.discoverdelay = 100
            ndevices = self.upnp.discover()
            if ndevices > 0:
                self.upnp.selectigd()
            else:
                raise PortGateError("Failed to discover UPnP devices: Your modem may not be supporting UPnP/NAT-PMP. Try enabling it in your modem settings.")
        except Exception as e:
            raise PortGateError("Failed to discover UPnP devices: Your modem may not be supporting UPnP/NAT-PMP. Try enabling it in your modem settings.")
            
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return self.upnp.lanaddr
    
    def add_mapping(self, internal_port: int, external_port: int, protocol: str = "TCP", 
                   description: str = "PortGate", ttl: int = 3600):
        local_ip = self._get_local_ip()
        
        protocols = ["TCP", "UDP"] if protocol == "BOTH" else [protocol]
        
        for proto in protocols:
            try:
                self.upnp.addportmapping(
                    external_port,
                    proto,
                    local_ip,
                    internal_port,
                    description,
                    str(ttl)
                )
            except Exception as e:
                raise PortGateError(f"Failed to add {proto} port mapping {external_port}: {str(e)}")
    
    def remove_mapping(self, internal_port: int, protocol: str = "TCP"):
        mappings = self.list_mappings()
        local_ip = self._get_local_ip()
        
        protocols = ["TCP", "UDP"] if protocol == "BOTH" else [protocol]
        
        removed = False
        for mapping in mappings:
            if (mapping['internal_port'] == internal_port and 
                mapping['internal_client'] == local_ip and 
                mapping['protocol'] in protocols):
                
                try:
                    result = self.upnp.deleteportmapping(
                        mapping['external_port'],
                        mapping['protocol']
                    )
                    if result:
                        removed = True
                except Exception as e:
                    raise PortGateError(f"Failed to remove {mapping['protocol']} port mapping {mapping['external_port']}: {str(e)}")
        
        if not removed:
            raise PortGateError(f"No matching port mapping found for {protocol} port {internal_port}")
    
    def list_mappings(self) -> List[Dict[str, Any]]:
        mappings = []
        try:
            i = 0
            while True:
                try:
                    mapping = self.upnp.getgenericportmapping(i)
                    if mapping is None:
                        break
                    
                    external_port, protocol, internal_client_port, description, enabled, remote_host, lease_duration = mapping
                    internal_client, internal_port = internal_client_port
                    
                    mappings.append({
                        'external_port': external_port,
                        'protocol': protocol,
                        'internal_client': internal_client,
                        'internal_port': internal_port,
                        'description': description,
                        'enabled': enabled,
                        'remote_host': remote_host,
                        'lease_duration': lease_duration
                    })
                    i += 1
                except Exception:
                    break
                    
            return mappings
        except Exception as e:
            raise PortGateError(f"Failed to list port mappings: {str(e)}")
    
    def refresh_mapping(self, internal_port: int, protocol: str = "TCP", ttl: int = 3600):
        mappings = self.list_mappings()
        local_ip = self._get_local_ip()
        
        found_mapping = None
        for mapping in mappings:
            if (mapping['internal_port'] == internal_port and 
                mapping['internal_client'] == local_ip and 
                mapping['protocol'] == protocol):
                found_mapping = mapping
                break
        
        if not found_mapping:
            raise PortGateError(f"No matching port mapping found for {protocol} port {internal_port}")
        
        try:
            self.upnp.deleteportmapping(
                found_mapping['external_port'],
                found_mapping['protocol']
            )
        except Exception as e:
            raise PortGateError(f"Failed to remove existing mapping: {str(e)}")
        
        try:
            self.add_mapping(
                internal_port=internal_port,
                external_port=found_mapping['external_port'],
                protocol=protocol,
                description=found_mapping.get('description', 'PortGate'),
                ttl=str(ttl)
            )
        except Exception as e:
            raise PortGateError(f"Failed to add new mapping: {str(e)}")
    
    def clear_mappings(self) -> int:
        mappings = self.list_mappings()
        local_ip = self._get_local_ip()
        count = 0
        
        for mapping in mappings:
            if mapping['internal_client'] == local_ip:
                try:
                    self.upnp.deleteportmapping(
                        mapping['external_port'],
                        mapping['protocol']
                    )
                    count += 1
                except Exception:
                    pass
                    
        return count
    
    def get_router_info(self) -> Dict[str, str]:
        try:
            return {
                'wan_ip': self.upnp.externalipaddress(),
                'lan_addr': self.upnp.lanaddr,
                'wan_addr': self.upnp.wanaddr
            }
        except Exception as e:
            raise PortGateError(f"Failed to get router information: {str(e)}")