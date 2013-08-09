"""
This module contains celery task functions for handling the sending of bulk email
to a course.
"""
import logging
import math
import re
import time

from smtplib import SMTPServerDisconnected, SMTPDataError, SMTPConnectError
from subprocess import Popen, PIPE

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import Http404
from celery import task, current_task
from django.core.urlresolvers import reverse

from bulk_email.models import (
    CourseEmail, Optout, CourseEmailTemplate
)
from courseware.access import _course_staff_group_name, _course_instructor_group_name
from courseware.courses import get_course_by_id

log = logging.getLogger(__name__)


@task(default_retry_delay=10, max_retries=5)  # pylint: disable=E1102
def delegate_email_batches(hash_for_msg, to_option, course_id, course_url, user_id):
    """
    Delegates emails by querying for the list of recipients who should
    get the mail, chopping up into batches of settings.EMAILS_PER_TASK size,
    and queueing up worker jobs.

    `to_option` is {'students', 'staff', or 'all'}

    Returns the number of batches (workers) kicked off.
    """
    try:
        course = get_course_by_id(course_id)
    except Http404 as exc:
        log.error("get_course_by_id failed: " + exc.args[0])
        raise Exception("get_course_by_id failed: " + exc.args[0])

    try:
        CourseEmail.objects.get(hash=hash_for_msg)
    except CourseEmail.DoesNotExist as exc:
        log.warning("Failed to get CourseEmail with hash %s, retry %d", hash_for_msg, current_task.request.retries)
        raise delegate_email_batches.retry(arg=[hash_for_msg, to_option, course_id, course_url, user_id], exc=exc)

    if to_option == "myself":
        recipient_qset = User.objects.filter(id=user_id).values('profile__name', 'email')
    else:
        staff_grpname = _course_staff_group_name(course.location)
        staff_group, _ = Group.objects.get_or_create(name=staff_grpname)
        staff_qset = staff_group.user_set.values('profile__name', 'email')
        instructor_grpname = _course_instructor_group_name(course.location)
        instructor_group, _ = Group.objects.get_or_create(name=instructor_grpname)
        instructor_qset = instructor_group.user_set.values('profile__name', 'email')
        recipient_qset = staff_qset | instructor_qset

        if to_option == "all":
            # Two queries are executed per performance considerations for MySQL.
            # See https://docs.djangoproject.com/en/1.2/ref/models/querysets/#in.
            course_optouts = Optout.objects.filter(course_id=course_id).values_list('email', flat=True)
            enrollment_qset = User.objects.filter(courseenrollment__course_id=course_id).exclude(email__in=list(course_optouts)).values('profile__name', 'email')
            recipient_qset = recipient_qset | enrollment_qset
        recipient_qset = recipient_qset.distinct()

    recipient_list = list(recipient_qset)
    total_num_emails = recipient_qset.count()
    num_workers = int(math.ceil(float(total_num_emails) / float(settings.EMAILS_PER_TASK)))
    chunk = int(math.ceil(float(total_num_emails) / float(num_workers)))

    for i in range(num_workers):
        to_list = recipient_list[i * chunk:i * chunk + chunk]
        course_email.delay(hash_for_msg, to_list, course.display_name, course_url, False)
    return num_workers


@task(default_retry_delay=15, max_retries=5)  # pylint: disable=E1102
def course_email(hash_for_msg, to_list, course_title, course_url, throttle=False):
    """
    Takes a subject and an html formatted email and sends it from
    sender to all addresses in the to_list, with each recipient
    being the only "to".  Emails are sent multipart, in both plain
    text and html.
    """
    # TODO:  this is a separate task, so it may run on a separate worker process
    # than the "delegate_email_batches" task that spawned it.  So we have to make
    # sure that the email templates have been loaded.
    course_email_template = CourseEmailTemplate.get_template()

    try:
        msg = CourseEmail.objects.get(hash=hash_for_msg)
    except CourseEmail.DoesNotExist as exc:
        log.exception(exc.args[0])
        raise exc

    subject = "[" + course_title + "] " + msg.subject

    process = Popen(['lynx', '-stdin', '-display_charset=UTF-8', '-assume_charset=UTF-8', '-dump'], stdin=PIPE, stdout=PIPE)
    (plaintext, err_from_stderr) = process.communicate(input=msg.html_message.encode('utf-8'))  # use lynx to get plaintext

    course_title_no_quotes = re.sub(r'"', '', course_title)
    from_addr = '"%s" Course Staff <%s>' % (course_title_no_quotes, settings.DEFAULT_BULK_FROM_EMAIL)

    if err_from_stderr:
        log.info(err_from_stderr)

    try:
        connection = get_connection()
        connection.open()
        num_sent = 0
        num_error = 0

        while to_list:
            (name, email) = to_list[-1].values()
#             html_footer = render_to_string('emails/email_footer.html',
#                                            {'name': name,
#                                             'email': email,
#                                             'course_title': course_title,
#                                             'course_url': course_url})
#             plain_footer = render_to_string('emails/email_footer.txt',
#                                             {'name': name,
#                                              'email': email,
#                                              'course_title': course_title,
#                                              'course_url': course_url})
#             plaintext_msg = plaintext + plain_footer.encode('utf-8')
#             html_msg = msg.html_message + html_footer.encode('utf-8')
            context = {
                'name': name,
                'email': email,
                'course_title': course_title,
                'course_url': course_url,
                'message_body': msg.html_message,
                'account_settings_url': 'https://{}{}'.format(settings.SITE_NAME, reverse('dashboard')),
                'platform_name': settings.PLATFORM_NAME,
            }

            plaintext_msg = course_email_template.render_plaintext(plaintext, context)
            html_msg = course_email_template.render_htmltext(msg.html_message, context)

            email_msg = EmailMultiAlternatives(subject, plaintext_msg, from_addr, [email], connection=connection)
            email_msg.attach_alternative(html_msg, 'text/html')

            if throttle or current_task.request.retries > 0:  # throttle if we tried a few times and got the rate limiter
                time.sleep(0.2)

            try:
                connection.send_messages([email_msg])
                log.info('Email with hash ' + hash_for_msg + ' sent to ' + email)
                num_sent += 1
            except SMTPDataError as exc:
                #According to SMTP spec, we'll retry error codes in the 4xx range.  5xx range indicates hard failure
                if exc.smtp_code >= 400 and exc.smtp_code < 500:
                    raise exc  # this will cause the outer handler to catch the exception and retry the entire task
                else:
                    #this will fall through and not retry the message, since it will be popped
                    log.warning('Email with hash ' + hash_for_msg + ' not delivered to ' + email + ' due to error: ' + exc.smtp_error)
                    num_error += 1

            to_list.pop()

        connection.close()
        return course_email_result(num_sent, num_error)

    except (SMTPDataError, SMTPConnectError, SMTPServerDisconnected) as exc:
        #error caught here cause the email to be retried.  The entire task is actually retried without popping the list
        raise course_email.retry(arg=[hash_for_msg, to_list, course_title, course_url, current_task.request.retries > 0], exc=exc, countdown=(2 ** current_task.request.retries) * 15)


# This string format code is wrapped in this function to allow mocking for a unit test
def course_email_result(num_sent, num_error):
    """Return the formatted result of course_email sending."""
    return "Sent {0}, Fail {1}".format(num_sent, num_error)
