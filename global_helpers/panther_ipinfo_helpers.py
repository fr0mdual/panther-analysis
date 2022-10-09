import datetime

from panther_base_helpers import deep_get


class IPInfoLocation:
    def __init__(self, event):
        self.ipinfo_location = deep_get(event, "p_enrichment", "ip-info-location-cidr")
    
    def city(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "city")
    
    def country(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "country")
    
    def latitude(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "lat")
    
    def longitude(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "lng")

    def postal_code(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "postal_code")
    
    def region(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "region")
    
    def region_code(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "region_code")
    
    def timezone(self, match_field) -> str:
        return deep_get(self.ipinfo_location, match_field, "timezone")


class IPInfoASN:
    def __init__(self, event):
        self.ipinfo_asn = deep_get(event, "p_enrichment", "ip-info-asn-cidr")
    
    def asn(self, match_field) -> str:
        return deep_get(self.ipinfo_asn, match_field, "asn")
    
    def domain(self, match_field) -> str:
        return deep_get(self.ipinfo_asn, match_field, "domain")
    
    def name(self, match_field) -> str:
        return deep_get(self.ipinfo_asn, match_field, "name")
    
    def route(self, match_field) -> str:
        return deep_get(self.ipinfo_asn, match_field, "route")

    def _type(self, match_field) -> str:
        return deep_get(self.ipinfo_asn, match_field, "type")
    
    
def GetIpInfoLocationObject(event):
    if deep_get(event, "p_enrichment", "ip-info-location-cidr"):
        return IPInfoLocation(event)

def GetIpInfoASNObject(event):
    if deep_get(event, "p_enrichment", "ip-info-asn-cidr"):
        return IPInfoASN(event)

def geoinfo_from_ip(event, match_field):
    ipinfo_location = GetIpInfoLocationObject(event)
    ipinfo_asn = GetIpInfoASNObject(event)
    if ipinfo_location and ipinfo_asn:
        return {
            "ip": event.get(match_field),
            #"hostname": "", TODO: Couldn't find this field in Location or ASN
            #"anycast": true, TODO: This field was listed in the example output, but not present in any requests
            "city": ipinfo_location.city(match_field),
            "region": ipinfo_location.region(match_field),
            "country": ipinfo_location.country(match_field),
            "loc": f"{ipinfo_location.latitude(match_field)},{ipinfo_location.longitude(match_field)}",
            "org": f"{ipinfo_asn.asn(match_field)} {ipinfo_asn.name(match_field)}",
            "postal": ipinfo_location.postal_code(match_field),
            "timezone": ipinfo_location.timezone(match_field),
        }
    else:
        raise Exception("Please enable both IPInfo Location and ASN Lookup Tables")