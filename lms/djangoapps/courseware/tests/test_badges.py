"""
Contains tests for courseware/badges.py
"""
# pylint: disable=W0212

from mock import MagicMock
import json

from django.test import TestCase

import courseware.badges as badges


class BlankBadgeDataTestCase(TestCase):
    """
    Test that badges.make_badge_data behaves correctly on empty inputs.
    """
    def setUp(self):
        """
        Mock the _fetch() method to return fake blank data.
        """
        def temp_fetch(url):
            """
            Returns blank fake data depending on the URL passed in.
            """
            if 's/.json' in url:  # list endpoint
                return []
            elif '/.json' in url:  # not a list endpoint
                return {}
            else:
                return {}
        self.old_fetch, badges._fetch = (badges._fetch, temp_fetch)

    def test_blank_data_with_course(self):
        """
        In the case when a course is passed to make_badge_data -- test that make_badge_data returns
        what it should.
        """
        obtained_output = badges.make_badge_data("", "")
        ideal_output = {'issuers': {}, 'badge_urls': '[]', 'badges': {}, 'badgeclasses': {}}
        self.assertEquals(obtained_output, ideal_output)

    def test_blank_data_without_course(self):
        """
        In the case when a course is not passed to make_badge_data -- test that make_badge_data returns
        what it should.
        """
        obtained_output = badges.make_badge_data("")
        ideal_output = {'issuers': {}, 'badge_urls': '[]', 'badges': {}, 'badgeclasses': {}}
        self.assertEquals(obtained_output, ideal_output)

    def tearDown(self):
        """
        Restore the value of _fetch. (not sure if necessary)
        """
        badges._fetch = self.old_fetch


class MakeBadgeDataTestCase(TestCase):
    """
    Test that badges.make_badge_data behaves correctly on example input.
    """
    def setUp(self):
        """
        Set up: Mock the _fetch() method to return fake data.
        Wall of text incoming; data generated from known working example.
        """
        def temp_fetch(url):
            """
            Returns specific fake data depending on the URL passed in.
            """
            if "badges/.json?badgeclass__issuer__course=&email=" in url:
                return [{u'issuedOn': u'2013-08-22', u'edx_href': u'badges/1/.json', u'uid': u'1', u'url': u'badges/1/.json', u'verify': {u'url': u'badges/1/.json', u'type': u'hosted'}, u'image': u'media/default/default.png', u'expires': None, u'recipient': {u'type': u'email', u'salt': u'9e64af6affb80f3ee2ab07dede720bd56363e9a91709708eb8c404a9f4c86875', u'hashed': True, u'identity': u'sha256$66957c96bd5215f0c8503d8cdd54f617afc0eaa70662dc2db8600d108a4ca628'}, u'evidence': None, u'edx_list_href': u'badges/', u'edx_custom': {}, u'badge': u'badgeclasses/1/.json'}, {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/4/.json', u'uid': u'4', u'url': u'badges/4/.json', u'verify': {u'url': u'badges/4/.json', u'type': u'hosted'}, u'image': u'media/default/default.png', u'expires': None, u'recipient': {u'type': u'email', u'salt': u'8982407cab305b34f78dd771fa0e2a9ba9e326a85e6d2aa38a8799c60ea9ab8a', u'hashed': True, u'identity': u'sha256$d13a683f7a6803e2777598c65d11a9c04ab76c7e379fedc28d463f190895bbfd'}, u'evidence': None, u'edx_list_href': u'badges/', u'edx_custom': {}, u'badge': u'badgeclasses/4/.json'}]

            elif "badgeclasses/.json?issuer__course=" in url:
                return [{u'edx_href': u'badgeclasses/1/.json', u'description': u'Successfully pass CB22x, The Ancient Greek Hero, with both heels intact.', u'tags': [], u'url': u'badgeclasses/1/.json', u'image': u'media/default/default.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 1, u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/1/.json', u'alignment': [], u'name': u'Better-than-Achilles Badge'}, {u'edx_href': u'badgeclasses/3/.json', u'description': u'Navigate your way through every video this course has to offer.', u'tags': [], u'url': u'badgeclasses/3/.json', u'image': u'media/default/default.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 0, u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/1/.json', u'alignment': [], u'name': u'Odysseus Badge'}, {u'edx_href': u'badgeclasses/4/.json', u'description': u'Awarded to exceptional participants in the course discussion forums.', u'tags': [], u'url': u'badgeclasses/4/.json', u'image': u'media/default/default.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 1, u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/1/.json', u'alignment': [], u'name': u'Aristotle Badge'}]

            elif "issuers/1/.json" in url:
                return {u'edx_href': u'issuers/1/.json', u'name': u'CB22x: The Ancient Greek Hero', u'url': u'issuers/1/.json', u'edx_course': u'HarvardX/CB22x/The_Ancient_Greek_Hero', u'image': u'media/default/default.png', u'edx_list_href': u'issuers/', u'edx_custom': {}, u'org': None, u'email': None, u'description': None}

            elif "badges/.json?email=" in url:
                return [{u'issuedOn': u'2013-08-22', u'edx_href': u'badges/1/.json', u'uid': u'1', u'url': u'badges/1/.json', u'verify': {u'url': u'badges/1/.json', u'type': u'hosted'}, u'image': u'media/default/default.png', u'expires': None, u'recipient': {u'type': u'email', u'salt': u'9e64af6affb80f3ee2ab07dede720bd56363e9a91709708eb8c404a9f4c86875', u'hashed': True, u'identity': u'sha256$66957c96bd5215f0c8503d8cdd54f617afc0eaa70662dc2db8600d108a4ca628'}, u'evidence': None, u'edx_list_href': u'badges/', u'edx_custom': {}, u'badge': u'badgeclasses/1/.json'}, {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/2/.json', u'uid': u'2', u'url': u'badges/2/.json', u'verify': {u'url': u'badges/2/.json', u'type': u'hosted'}, u'image': u'media/Issuer/test_3.png', u'expires': None, u'recipient': {u'type': u'email', u'salt': u'b9f192ce0227b5bee070c2b35e6af6581a7671cebce96fdbf4f335cf50e71bf3', u'hashed': True, u'identity': u'sha256$fb89d81902bea47e37da79ab122a5ecdda3347f502251bc3335413a185c8a549'}, u'evidence': None, u'edx_list_href': u'badges/', u'edx_custom': {}, u'badge': u'badgeclasses/2/.json'}, {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/3/.json', u'uid': u'3', u'url': u'badges/3/.json', u'verify': {u'url': u'badges/3/.json', u'type': u'hosted'}, u'image': u'media/default/default.png', u'expires': None, u'recipient': {u'type': u'email', u'salt': u'620a6bd59fb004fc31489bdc115bcbd8edba6d29a3e89a6eb3cec01276e4ad47', u'hashed': True, u'identity': u'sha256$1667a38a72231d2b07f787d629d75ba848f0944a801509c1c87fd0bd5892a113'}, u'evidence': None, u'edx_list_href': u'badges/', u'edx_custom': {}, u'badge': u'badgeclasses/5/.json'}, {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/4/.json', u'uid': u'4', u'url': u'badges/4/.json', u'verify': {u'url': u'badges/4/.json', u'type': u'hosted'}, u'image': u'media/default/default.png', u'expires': None, u'recipient': {u'type': u'email', u'salt': u'8982407cab305b34f78dd771fa0e2a9ba9e326a85e6d2aa38a8799c60ea9ab8a', u'hashed': True, u'identity': u'sha256$d13a683f7a6803e2777598c65d11a9c04ab76c7e379fedc28d463f190895bbfd'}, u'evidence': None, u'edx_list_href': u'badges/', u'edx_custom': {}, u'badge': u'badgeclasses/4/.json'}]

            elif "badgeclasses/1/.json" in url:
                return {u'edx_href': u'badgeclasses/1/.json', u'description': u'Successfully pass CB22x, The Ancient Greek Hero, with both heels intact.', u'tags': [], u'url': u'badgeclasses/1/.json', u'image': u'media/default/default.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 1, u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/1/.json', u'alignment': [], u'name': u'Better-than-Achilles Badge'}

            elif "badgeclasses/2/.json" in url:
                return {u'edx_href': u'badgeclasses/2/.json', u'description': u'Register for at least one edX course.', u'tags': [], u'url': u'badgeclasses/2/.json', u'image': u'media/Issuer/test_3.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 1, u'criteria': u'http://www.edx.org/', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/3/.json', u'alignment': [], u'name': u'Learning is Fun'}

            elif "badgeclasses/5/.json" in url:
                return {u'edx_href': u'badgeclasses/5/.json', u'description': u'Complete the theoretical and applied components of the 19.001x lab assignment.', u'tags': [], u'url': u'badgeclasses/5/.json', u'image': u'media/default/default.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 1, u'criteria': u'http://hacks.mit.edu/', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/2/.json', u'alignment': [], u'name': u'Techcraft and Hackery'}

            elif "badgeclasses/4/.json" in url:
                return {u'edx_href': u'badgeclasses/4/.json', u'description': u'Awarded to exceptional participants in the course discussion forums.', u'tags': [], u'url': u'badgeclasses/4/.json', u'image': u'media/default/default.png', u'edx_custom': {}, u'edx_list_href': u'badgeclasses/', u'edx_number_awarded': 1, u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047', u'edx_created_on': u'2013-08-22', u'issuer': u'issuers/1/.json', u'alignment': [], u'name': u'Aristotle Badge'}

            elif "issuers/1/.json" in url:
                return {u'edx_href': u'issuers/1/.json', u'name': u'CB22x: The Ancient Greek Hero', u'url': u'issuers/1/.json', u'edx_course': u'HarvardX/CB22x/The_Ancient_Greek_Hero', u'image': u'media/default/default.png', u'edx_list_href': u'issuers/', u'edx_custom': {}, u'org': None, u'email': None, u'description': None}

            elif "issuers/2/.json" in url:
                return {u'edx_href': u'issuers/2/.json', u'name': u'19.001x: Laboratory in Urban Exploration and Engineering', u'url': u'issuers/2/.json', u'edx_course': u'MITx/19.001x/Laboratory_in_Urban_Exploration_and_Engineering', u'image': u'media/default/default.png', u'edx_list_href': u'issuers/', u'edx_custom': {}, u'org': None, u'email': None, u'description': None}

            elif "issuers/3/.json" in url:
                return {u'edx_href': u'issuers/3/.json', u'name': u'test-edX', u'url': u'issuers/3/.json', u'edx_course': None, u'image': u'media/Issuer/test_3.png', u'edx_list_href': u'issuers/', u'edx_custom': {}, u'org': None, u'email': None, u'description': None}

            else:
                return {}

        self.old_fetch, badges._fetch = (badges._fetch, temp_fetch)

    def test_with_course(self):
        """
        Compare the output of make_badge_data for a some fake output of _fetch()
        against this correct copy of the output -- when course.id is specified.
        """
        obtained_output = badges.make_badge_data("", "")
        ideal_output = {'issuers': {u'issuers/1/.json': {u'edx_list_href': u'issuers/', u'edx_href': u'issuers/1/.json', u'name': u'CB22x: The Ancient Greek Hero', u'edx_custom': {}, u'url': u'issuers/1/.json', u'edx_course': u'HarvardX/CB22x/The_Ancient_Greek_Hero', u'image': u'media/default/default.png', u'org': None, u'email': None, u'description': None}}, 'badge_urls': '["badges/1/.json", "badges/4/.json"]', 'badges': {u'badgeclasses/1/.json': {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/1/.json', u'uid': u'1', u'image': u'media/default/default.png', u'expires': None, u'evidence': None, u'edx_custom': {}, u'recipient': {u'salt': u'9e64af6affb80f3ee2ab07dede720bd56363e9a91709708eb8c404a9f4c86875', u'type': u'email', u'hashed': True, u'identity': u'sha256$66957c96bd5215f0c8503d8cdd54f617afc0eaa70662dc2db8600d108a4ca628'}, u'url': u'badges/1/.json', u'verify': {u'url': u'badges/1/.json', u'type': u'hosted'}, u'edx_list_href': u'badges/', u'badge': u'badgeclasses/1/.json'}, u'badgeclasses/4/.json': {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/4/.json', u'uid': u'4', u'image': u'media/default/default.png', u'expires': None, u'evidence': None, u'edx_custom': {}, u'recipient': {u'salt': u'8982407cab305b34f78dd771fa0e2a9ba9e326a85e6d2aa38a8799c60ea9ab8a', u'type': u'email', u'hashed': True, u'identity': u'sha256$d13a683f7a6803e2777598c65d11a9c04ab76c7e379fedc28d463f190895bbfd'}, u'url': u'badges/4/.json', u'verify': {u'url': u'badges/4/.json', u'type': u'hosted'}, u'edx_list_href': u'badges/', u'badge': u'badgeclasses/4/.json'}}, 'badgeclasses': {u'badgeclasses/3/.json': {u'edx_href': u'badgeclasses/3/.json', u'description': u'Navigate your way through every video this course has to offer.', u'tags': [], u'image': u'media/default/default.png', u'edx_number_awarded': 0, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/1/.json', u'name': u'Odysseus Badge', u'url': u'badgeclasses/3/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047'}, u'badgeclasses/1/.json': {u'edx_href': u'badgeclasses/1/.json', u'description': u'Successfully pass CB22x, The Ancient Greek Hero, with both heels intact.', u'tags': [], u'image': u'media/default/default.png', u'edx_number_awarded': 1, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/1/.json', u'name': u'Better-than-Achilles Badge', u'url': u'badgeclasses/1/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047'}, u'badgeclasses/4/.json': {u'edx_href': u'badgeclasses/4/.json', u'description': u'Awarded to exceptional participants in the course discussion forums.', u'tags': [], u'image': u'media/default/default.png', u'edx_number_awarded': 1, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/1/.json', u'name': u'Aristotle Badge', u'url': u'badgeclasses/4/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047'}}}
        self.assertEqualCustom(obtained_output, ideal_output)

    def test_without_course(self):
        """
        Compare the output of make_badge_data for a some fake output of fetch()
        against this correct copy of the output -- when course is not specified.
        """
        obtained_output = badges.make_badge_data("")
        ideal_output = {'badgeclasses': {u'badgeclasses/4/.json': {u'edx_href': u'badgeclasses/4/.json', u'description': u'Awarded to exceptional participants in the course discussion forums.', u'tags': [], u'image': u'media/default/default.png', u'edx_number_awarded': 1, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/1/.json', u'name': u'Aristotle Badge', u'url': u'badgeclasses/4/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047'}, u'badgeclasses/1/.json': {u'edx_href': u'badgeclasses/1/.json', u'description': u'Successfully pass CB22x, The Ancient Greek Hero, with both heels intact.', u'tags': [], u'image': u'media/default/default.png', u'edx_number_awarded': 1, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/1/.json', u'name': u'Better-than-Achilles Badge', u'url': u'badgeclasses/1/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'https://www.edx.org/course/harvard-university/cb22-1x/ancient-greek-hero/1047'}, u'badgeclasses/2/.json': {u'edx_href': u'badgeclasses/2/.json', u'description': u'Register for at least one edX course.', u'tags': [], u'image': u'media/Issuer/test_3.png', u'edx_number_awarded': 1, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/3/.json', u'name': u'Learning is Fun', u'url': u'badgeclasses/2/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'http://www.edx.org/'}, u'badgeclasses/5/.json': {u'edx_href': u'badgeclasses/5/.json', u'description': u'Complete the theoretical and applied components of the 19.001x lab assignment.', u'tags': [], u'image': u'media/default/default.png', u'edx_number_awarded': 1, u'edx_custom': {}, u'edx_created_on': u'2013-08-22', u'alignment': [], u'issuer': u'issuers/2/.json', u'name': u'Techcraft and Hackery', u'url': u'badgeclasses/5/.json', u'edx_list_href': u'badgeclasses/', u'criteria': u'http://hacks.mit.edu/'}}, 'issuers': {u'issuers/2/.json': {u'edx_list_href': u'issuers/', u'edx_href': u'issuers/2/.json', u'name': u'19.001x: Laboratory in Urban Exploration and Engineering', u'edx_custom': {}, u'url': u'issuers/2/.json', u'edx_course': u'MITx/19.001x/Laboratory_in_Urban_Exploration_and_Engineering', u'image': u'media/default/default.png', u'org': None, u'email': None, u'description': None}, u'issuers/1/.json': {u'edx_list_href': u'issuers/', u'edx_href': u'issuers/1/.json', u'name': u'CB22x: The Ancient Greek Hero', u'edx_custom': {}, u'url': u'issuers/1/.json', u'edx_course': u'HarvardX/CB22x/The_Ancient_Greek_Hero', u'image': u'media/default/default.png', u'org': None, u'email': None, u'description': None}, u'issuers/3/.json': {u'edx_list_href': u'issuers/', u'edx_href': u'issuers/3/.json', u'name': u'test-edX', u'edx_custom': {}, u'url': u'issuers/3/.json', u'edx_course': None, u'image': u'media/Issuer/test_3.png', u'org': None, u'email': None, u'description': None}}, 'badge_urls': '["badges/4/.json", "badges/1/.json", "badges/2/.json", "badges/3/.json"]', 'badges': {u'badgeclasses/4/.json': {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/4/.json', u'uid': u'4', u'image': u'media/default/default.png', u'expires': None, u'evidence': None, u'edx_custom': {}, u'recipient': {u'salt': u'8982407cab305b34f78dd771fa0e2a9ba9e326a85e6d2aa38a8799c60ea9ab8a', u'type': u'email', u'hashed': True, u'identity': u'sha256$d13a683f7a6803e2777598c65d11a9c04ab76c7e379fedc28d463f190895bbfd'}, u'url': u'badges/4/.json', u'verify': {u'url': u'badges/4/.json', u'type': u'hosted'}, u'edx_list_href': u'badges/', u'badge': u'badgeclasses/4/.json'}, u'badgeclasses/1/.json': {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/1/.json', u'uid': u'1', u'image': u'media/default/default.png', u'expires': None, u'evidence': None, u'edx_custom': {}, u'recipient': {u'salt': u'9e64af6affb80f3ee2ab07dede720bd56363e9a91709708eb8c404a9f4c86875', u'type': u'email', u'hashed': True, u'identity': u'sha256$66957c96bd5215f0c8503d8cdd54f617afc0eaa70662dc2db8600d108a4ca628'}, u'url': u'badges/1/.json', u'verify': {u'url': u'badges/1/.json', u'type': u'hosted'}, u'edx_list_href': u'badges/', u'badge': u'badgeclasses/1/.json'}, u'badgeclasses/2/.json': {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/2/.json', u'uid': u'2', u'image': u'media/Issuer/test_3.png', u'expires': None, u'evidence': None, u'edx_custom': {}, u'recipient': {u'salt': u'b9f192ce0227b5bee070c2b35e6af6581a7671cebce96fdbf4f335cf50e71bf3', u'type': u'email', u'hashed': True, u'identity': u'sha256$fb89d81902bea47e37da79ab122a5ecdda3347f502251bc3335413a185c8a549'}, u'url': u'badges/2/.json', u'verify': {u'url': u'badges/2/.json', u'type': u'hosted'}, u'edx_list_href': u'badges/', u'badge': u'badgeclasses/2/.json'}, u'badgeclasses/5/.json': {u'issuedOn': u'2013-08-22', u'edx_href': u'badges/3/.json', u'uid': u'3', u'image': u'media/default/default.png', u'expires': None, u'evidence': None, u'edx_custom': {}, u'recipient': {u'salt': u'620a6bd59fb004fc31489bdc115bcbd8edba6d29a3e89a6eb3cec01276e4ad47', u'type': u'email', u'hashed': True, u'identity': u'sha256$1667a38a72231d2b07f787d629d75ba848f0944a801509c1c87fd0bd5892a113'}, u'url': u'badges/3/.json', u'verify': {u'url': u'badges/3/.json', u'type': u'hosted'}, u'edx_list_href': u'badges/', u'badge': u'badgeclasses/5/.json'}}}
        self.assertEqualCustom(obtained_output, ideal_output)

    def assertEqualCustom(self, dict1, dict2):
        """
        Compares two dictionaries, recursively. Asserts their contents are roughly equal. Custom-made for these tests.

        The key 'badge_urls' is treated specially, since it is a string containing a json-dumped list of items --
        order doesn't matter for the list comparison, but just comparing the strings won't catch that.
        """

        for key in dict1.keys():
            if not key in dict2:
                self.assertTrue(False, 'Key {key} is in first dictionary but not second.'.format(key=key))

        for key in dict2.keys():
            if not key in dict1:
                self.assertTrue(False, 'Key {key} is in second dictionary but not first.'.format(key=key))

            value1, value2 = dict1[key], dict2[key]

            if key == 'badge_urls':
                list1, list2 = json.loads(value1), json.loads(value2)
                self.assertItemsEqual(list1, list2)  # order doesn't matter!
            elif type(value1) is dict and type(value2) is dict:
                self.assertEqualCustom(value1, value2)
            else:
                self.assertEqual(value1, value2)

    def tearDown(self):
        """
        Restore the value of _fetch. (not sure if necesary)
        """
        badges._fetch = self.old_fetch


class FetchTestCase(TestCase):
    """
    Tests the _fetch helper method of badges.py.

    The tests which test make_badge_data, the only function in badges.py which uses the _fetch helper method,
    do so by creating a mock of _fetch -- so _fetch itself needs this testing.
    """
    def setUp(self):
        """
        Create a mock of the requests library which has a dummy get() method.
        """
        def fake_get(url, timeout=None):
            """
            Return fake data, depending on the URL passed in. Replaces requests.get.
            """

            # _fetch should not be calling get without a timeout. If it is, that's a problem.
            if timeout is None:
                raise ValueError("badges._fetch calls requests.get without specifying a timeout -- which is bad")
            response = MagicMock()

            if 'test1' in url:
                output = {'results': ['list', 'of', 'things'], 'next': None, 'prev': None}
            elif 'test2.1' in url:
                output = {'results': ['thing 1', 'thing 2'], 'next': 'test2.2', 'prev': None}
            elif 'test2.2' in url:
                output = {'results': ['thing 3'], 'next': None, 'prev': 'test2.1'}
            elif 'test3' in url:
                output = {'dummy JSON object': True}
            else:
                output = {'results': [], 'next': None}

            response.json = output
            return response

        fake_requests = MagicMock()
        fake_requests.get = fake_get

        self.old_requests, badges.requests = badges.requests, fake_requests


    def test_fetch_list(self):
        """
        Test that _fetch returns correctly when reading a single list of objects.
        """
        obtained_output = badges._fetch('test1')
        ideal_output = ['list', 'of', 'things']
        self.assertItemsEqual(ideal_output, obtained_output)

    def test_fetch_list_paginated(self):
        """
        Test that _fetch returns all pages' lists put together when reading a paginated list of objects.
        """
        obtained_output = badges._fetch('test2.1')
        ideal_output = ['thing 1', 'thing 2', 'thing 3']
        self.assertItemsEqual(ideal_output, obtained_output)

    def test_fetch_instance(self):
        """
        Test that _fetch returns correctly when reading a single object.
        """
        obtained_output = badges._fetch('test3')
        ideal_output = {'dummy JSON object': True}
        self.assertEqual(ideal_output, obtained_output)

    def tearDown(self):
        """
        Restore the original requests (not sure if necessary).
        """
        badges.requests = self.old_requests
