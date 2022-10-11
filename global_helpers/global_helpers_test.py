#!/usr/bin/env python
# Unit tests for functions inside global_helpers

import datetime
import os
import sys
import unittest

# pipenv run does the right thing, but IDE based debuggers may fail to import
#   so noting, we append this directory to sys.path
sys.path.append(os.path.dirname(__file__))

import panther_base_helpers as p_b_h  # pylint: disable=C0413
import panther_tor_helpers as p_tor_h  # pylint: disable=C0413
import panther_ipinfo_helpers as p_i_h  # pylint: disable=C0413


class TestBoxParseAdditionalDetails(unittest.TestCase):
    def setUp(self):
        self.initial_dict = {"t": 10, "a": [{"b": 1, "c": 2}], "d": {"e": {"f": True}}}
        self.initial_list = ["1", 2, True, False]
        self.initial_bytes = b'{"t": 10, "a": [{"b": 1, "c": 2}], "d": {"e": {"f": True}}}'
        self.initial_str = '{"t": 10, "a": [{"b": 1, "c": 2}], "d": {"e": {"f": true}}}'
        self.initial_str_no_json = "this is a plain string"
        self.initial_str_list_json = "[1, 2, 3, 4]"

    def test_additional_details_string(self):
        event = {"additional_details": self.initial_str}
        returns = p_b_h.box_parse_additional_details(event)
        self.assertEqual(returns.get("t", 0), 10)

    # in the case of a byte array, we expect the empty dict
    def test_additional_details_bytes(self):
        event = {"additional_details": self.initial_bytes}
        returns = p_b_h.box_parse_additional_details(event)
        self.assertEqual(len(returns), 0)

    # In the case of a list ( not a string or bytes array ), expect un-altered return
    def test_additional_details_list(self):
        event = {"additional_details": self.initial_list}
        returns = p_b_h.box_parse_additional_details(event)
        self.assertEqual(len(returns), 4)

    # in the case of a dict or similar, we expect it to be returned un-altered
    def test_additional_details_dict(self):
        event = {"additional_details": self.initial_dict}
        returns = p_b_h.box_parse_additional_details(event)
        self.assertEqual(returns.get("t", 0), 10)

    # If it's a string with no json object to be decoded, we expect an empty dict back
    def test_additional_details_plain_str(self):
        event = {"additional_details": self.initial_str_no_json}
        returns = p_b_h.box_parse_additional_details(event)
        self.assertEqual(len(returns), 0)

    # If it's a string with a json list, we expect the list
    def test_additional_details_str_list_json(self):
        event = {"additional_details": self.initial_str_list_json}
        returns = p_b_h.box_parse_additional_details(event)
        self.assertEqual(len(returns), 4)


class TestTorExitNodes(unittest.TestCase):
    def test_ip_address_not_found(self):
        """Should not find anything"""
        tor_exit_nodes = p_tor_h.TorExitNodes({})
        ip_address = tor_exit_nodes.ip_address("foo")
        self.assertEqual(ip_address, None)

    def test_has_exit_nodes_found(self):
        """Should find enrichment"""
        tor_exit_nodes = p_tor_h.TorExitNodes(
            {"p_enrichment": {"tor_exit_nodes": {"foo": {"ip": "1.2.3.4"}}}}
        )
        self.assertEqual(tor_exit_nodes.has_exit_nodes(), True)

    def test_has_exit_nodes_not_found(self):
        """Should NOT find enrichment"""
        tor_exit_nodes = p_tor_h.TorExitNodes({"p_enrichment": {}})
        self.assertEqual(tor_exit_nodes.has_exit_nodes(), False)

    def test_ip_address_found(self):
        """Should find enrichment"""
        tor_exit_nodes = p_tor_h.TorExitNodes(
            {"p_enrichment": {"tor_exit_nodes": {"foo": {"ip": "1.2.3.4"}}}}
        )
        ip_address = tor_exit_nodes.ip_address("foo")
        self.assertEqual(ip_address, "1.2.3.4")

    def test_url(self):
        """url generation"""
        tor_exit_nodes = p_tor_h.TorExitNodes(
            {"p_enrichment": {"tor_exit_nodes": {"foo": {"ip": "1.2.3.4"}}}}
        )
        url = tor_exit_nodes.url("foo")
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        # pylint: disable=line-too-long
        self.assertEqual(
            url,
            f"https://metrics.torproject.org/exonerator.html?ip=1.2.3.4&timestamp={today}&lang=en",
        )

    def test_context(self):
        """context generation"""
        tor_exit_nodes = p_tor_h.TorExitNodes(
            {"p_enrichment": {"tor_exit_nodes": {"foo": {"ip": "1.2.3.4"}}}}
        )
        context = tor_exit_nodes.context("foo")
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        self.assertEqual(
            context,
            {
                "IP": "1.2.3.4",
                # pylint: disable=line-too-long
                "ExoneraTorURL": f"https://metrics.torproject.org/exonerator.html?ip=1.2.3.4&timestamp={today}&lang=en",
            },
        )


class TestIpInfoHelpersLocation(unittest.TestCase):
    def setUp(self):
        self.event = {
            "p_enrichment": {
                "ip-info-location-cidr": {
                    "match_field": {
                        "city": "Constantinople",
                        "country": "Byzantium",
                        "lat": "41.008610",
                        "lng": "28.971111",
                        "postal_code": "",
                        "region": "Asia Minor",
                        "region_code": "123",
                        "timezone": "GMT+03:00",
                    }
                }
            }
        }
        self.ip_info = p_i_h.get_ipinfo_location_object(self.event)

    def test_city(self):
        city = self.ip_info.city("match_field")
        self.assertEqual(city, "Constantinople")

    def test_country(self):
        country = self.ip_info.country("match_field")
        self.assertEqual(country, "Byzantium")

    def test_latitude(self):
        latitude = self.ip_info.latitude("match_field")
        self.assertEqual(latitude, "41.008610")

    def test_longitude(self):
        longitude = self.ip_info.longitude("match_field")
        self.assertEqual(longitude, "28.971111")

    def test_postal_code(self):
        postal_code = self.ip_info.postal_code("match_field")
        self.assertEqual(postal_code, "")

    def test_region(self):
        region = self.ip_info.region("match_field")
        self.assertEqual(region, "Asia Minor")

    def test_region_code(self):
        region_code = self.ip_info.region_code("match_field")
        self.assertEqual(region_code, "123")

    def test_timezone(self):
        timezone = self.ip_info.timezone("match_field")
        self.assertEqual(timezone, "GMT+03:00")


class TestIpInfoHelpersASN(unittest.TestCase):
    def setUp(self):
        self.event = {
            "p_enrichment": {
                "ip-info-asn-cidr": {
                    "match_field": {
                        "asn": "AS00000",
                        "domain": "byzantineempire.com",
                        "name": "Byzantine Empire",
                        "route": "1.2.3.4/24",
                        "type": "isp",
                    }
                }
            }
        }
        self.ip_info = p_i_h.get_ipinfo_asn_object(self.event)

    def test_asn(self):
        asn = self.ip_info.asn("match_field")
        self.assertEqual(asn, "AS00000")

    def test_domain(self):
        domain = self.ip_info.domain("match_field")
        self.assertEqual(domain, "byzantineempire.com")

    def test_name(self):
        name = self.ip_info.name("match_field")
        self.assertEqual(name, "Byzantine Empire")

    def test_route(self):
        route = self.ip_info.route("match_field")
        self.assertEqual(route, "1.2.3.4/24")

    def test_asn_type(self):
        _type = self.ip_info.asn_type("match_field")
        self.assertEqual(_type, "isp")


class TestIpInfoHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.event = {
            "match_field": "1.2.3.4.5",
            "p_enrichment": {
                "ip-info-location-cidr": {
                    "match_field": {
                        "city": "Constantinople",
                        "country": "Byzantium",
                        "lat": "41.008610",
                        "lng": "28.971111",
                        "postal_code": "",
                        "region": "Asia Minor",
                        "region_code": "123",
                        "timezone": "GMT+03:00",
                    }
                },
                "ip-info-asn-cidr": {
                    "match_field": {
                        "asn": "AS00000",
                        "domain": "byzantineempire.com",
                        "name": "Byzantine Empire",
                        "route": "1.2.3.4/24",
                        "type": "isp",
                    }
                },
            },
        }
        self.ipinfo_location = p_i_h.get_ipinfo_location_object(self.event)
        self.ipinfo_asn = p_i_h.get_ipinfo_asn_object(self.event)

    def test_geoinfo_from_ip(self):
        expected = {
            "ip": "1.2.3.4.5",
            "city": "Constantinople",
            "region": "Asia Minor",
            "country": "Byzantium",
            "loc": "41.008610,28.971111",
            "org": "AS00000 Byzantine Empire",
            "postal": "",
            "timezone": "GMT+03:00",
        }
        context = p_i_h.geoinfo_from_ip(self.event, "match_field")
        self.assertEqual(context, expected)

    def test_geoinfo_from_ip_fail(self):
        error_event = {
            "match_field": "1.2.3.4.5",
            "p_enrichment": {
                "ip-info-location-cidr": {
                    "match_field": {
                        "city": "Constantinople",
                        "country": "Byzantium",
                        "lat": "41.008610",
                        "lng": "28.971111",
                        "postal_code": "",
                        "region": "Asia Minor",
                        "region_code": "123",
                        "timezone": "GMT+03:00",
                    }
                }
            },
        }
        with self.assertRaises(p_i_h.PantherIPInfoException):
            p_i_h.geoinfo_from_ip(error_event, "match_field")


if __name__ == "__main__":
    unittest.main()
