"""
Contains the function make_badge_data, responsible for getting badge data from the badge service.
"""

import json
import requests

from django.conf import settings


def _fetch(url):
    """
    Helper method. Reads the JSON object located at a URL. Returns the Python representation of the JSON object.

    If the fetched JSON object is a paginated list -- with the next url at 'next' and the content at 'results' --
    this reads through all of the pages, and compiles the results together into one list.

    Prints an error message if unsuccessful.
    """

    # Create absolute URL from relative URL.
    if not settings.BADGE_SERVICE_URL in url:
        url = settings.BADGE_SERVICE_URL + url

    try:
        obj = requests.get(url, timeout=10).json  # pylint: disable=E1103

        results = obj.get('results', None)

        # Ensure that next results are obtained, if the output was paginated.
        if results is not None:
            next_url = obj.get('next', None)

            while next_url is not None:
                next_obj = requests.get(next_url, timeout=10).json  # pylint: disable=E1103
                results.extend(next_obj.get('results', []))
                next_url = obj.get('next', None)

            return results

        else:
            return obj

    except requests.exceptions.RequestException:
        print 'Badge service inaccessible? URL not found -- {url}'.format(url=str(url))
        return []


def make_badge_data(email, course=None):
    """
    Returns a dictionary:
        'badges': a dictionary --
            {badge's badgeclass's href: badge data, for badge in all badges this student has earned}
        'badgeclasses': a dictionary --
            {badgeclass's href: badgeclass data, for badgeclass in all badgeclasses for this course}
        'issuers': a dictionary --
            {issuer's href: issuer data, for issuer in all issuers referenced by all badgeclasses for this course}
        'badge_urls': a string contain JSON dump of a list of URLs; the URLs link to the JSON where
            each earned badge may be accessed, at the badge service
    """

    if course is not None:

        # Filter badges by the student's email and by the course ID.
        badges_url = 'v1/badges/.json?badgeclass__issuer__course={course}&email={email}'
        raw_badges = _fetch(badges_url.format(course=course.id, email=email))

        # Get the list of all badgeclasses for this course.
        raw_badgeclasses = _fetch('v1/badgeclasses/.json?issuer__course={course}'.format(course=course.id))

    else:
        # No course: only filter badges by the student's email, and display no unearned badges.
        badges_url = 'v1/badges/.json?email={email}'
        raw_badges = _fetch(badges_url.format(email=email))

        raw_badgeclasses = [
            _fetch(badge['badge'])
            for badge in raw_badges
        ]

    # Format badgeclasses into a dictionary -- badgeclass_url: badgeclass_data
    badgeclasses = dict([
        (badgeclass['edx_href'], badgeclass)
        for badgeclass in raw_badgeclasses
    ])

    # Format badges into a dictionary -- badgeclass_url: badge_data
    badges = dict([
        (badge['badge'], badge)
        for badge in raw_badges
    ])

    # Get the list of URLs to access to export badges to Mozilla.
    badge_urls = [
        badge['edx_href']
        for badge in badges.values()
        if badge is not None and 'edx_href' in badge
    ]

    # Fetch data about the issuer.
    issuers = {}
    for badgeclass in badgeclasses.values():
        issuer_url = badgeclass['issuer']
        if issuer_url not in issuers.keys():
            issuers.update({issuer_url: _fetch(issuer_url)})

    output = {
        'badges': badges,
        'badgeclasses': badgeclasses,
        'issuers': issuers,
        'badge_urls': json.dumps(badge_urls),
    }

    return output
