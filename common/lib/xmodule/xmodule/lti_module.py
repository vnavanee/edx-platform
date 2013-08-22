"""
Module that allows to insert LTI tools to page.
"""

import logging
import requests
from uuid import uuid1
import datetime
import time


from xmodule.editing_module import MetadataOnlyEditingDescriptor
from xmodule.x_module import XModule
from pkg_resources import resource_string
from xblock.core import String, Scope

log = logging.getLogger(__name__)


class LTIFields(object):
    """provider_url and tool_id together is unique location of LTI in the web."""
    client_key = String(help="Client key", default='5c6b9020-066a-11e3-8ffd-0800200c9a66', scope=Scope.settings)
    client_secret = String(help="Client secret", default='75413f322a7b4e76223e332c625f3d34', scope=Scope.settings)
    lti_url = String(
        help="URL of the tool",
        default='https://bc-staging.vitalsource.com/books/1-889325-26-0',
        # TODO: Write a letter.
        scope=Scope.settings
    )


class LTIModule(LTIFields, XModule):
    '''LTI Module'''

    js = {
        'js': [
            resource_string(__name__, 'js/src/lti/lti.js')
        ]
    }
    css = {'scss': [resource_string(__name__, 'css/gst/display.scss')]}
    js_module_name = "LTI"

    def get_html(self):
        """ Renders parameters to template. """
        params = {
            'lti_url': self.lti_url,
            #TODO 'oauth_timestamp': int(time.mktime(datetime.datetime.now().timetuple())),
            'element_id': self.location.html_id(),
            'element_class': self.location.category,
        }
        params.update(self.oauth_params())
        # import ipdb; ipdb.set_trace()
        return self.system.render_template('lti.html', params)

    def oauth_params(self):
        """Obtains LTI html from provider"""
        client = requests.auth.Client(
            client_key=unicode(self.client_key),
            client_secret=unicode(self.client_secret)
        )
        # Please set content-type to application/x-www-form-urlencoded
        body1 = {
            'user_id': 'default_user_id',
            'oauth_callback': 'about:blank',
            'launch_presentation_return_url': 'http://www.imsglobal.org/developers/LTI/test/v1p1/lms_return.php',
            'lis_outcome_service_url': 'http://www.imsglobal.org/developers/LTI/test/v1p1/common/tool_consumer_outcome.php?b64=NWM2YjkwMjAtMDY2YS0xMWUzLThmZmQtMDgwMDIwMGM5YTY2Ojo6NzU0MTNmMzIyYTdiNGU3NjIyM2UzMzJjNjI1ZjNkMzQ=',
            'lis_result_sourcedid': 'feb-123-456-2929::28883',
            'lti_message_type': 'basic-lti-launch-request',
            'lti_version': 'LTI-1p0',
            'instructor': 'test'
        }
        # launch_presentation_return_url = http://www.imsglobal.org/developers/LTI/test/v1p1/lms_return.php
        header1= {
            'Authorization': requests.auth.CONTENT_TYPE_FORM_URLENCODED,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        uri, headers, body = client.sign(
            unicode(self.lti_url),
            http_method=u'POST',
            body=body1,
            headers=header1)
        params = headers['Authorization']
        # import ipdb; ipdb.set_trace()
        params = dict([param.strip().replace('"', '').split('=') for param in params.split('",')])
        params[u'oauth_nonce'] = params[u'OAuth oauth_nonce']
        return params



class LTIModuleDescriptor(LTIFields, MetadataOnlyEditingDescriptor):
    """LTI Descriptor"""
    module_class = LTIModule
