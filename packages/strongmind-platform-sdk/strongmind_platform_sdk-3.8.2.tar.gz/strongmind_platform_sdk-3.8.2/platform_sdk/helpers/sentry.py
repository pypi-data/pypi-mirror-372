import re


def sentry_ignored(event, ignored_urls=None):
    if ignored_urls is None:
        ignored_urls = sentry_ignored_urls()
    event_url = event["request"]["url"]
    return any(re.search(url, event_url) for url in ignored_urls)


def sentry_ignored_urls():
    return [
        r'/up$',
        r'/health_check$',
        r'/favicon\.ico$',
        r'/robots\.txt$',
        r'/nuclei.svg$',
        r'/wp-admin',
        r'/cgi-bin',
        r'/jmx-console',
        r'/manager/html',
        r'/phpmyadmin',
        r'.+\.php$',
        r'.+\.ini$',
        r'.+\.env$',
        r'.+\.txt$',
        r'.+\.jsp$',
        r'.+\.do$',
        r'.+\.srf$',
        r'.+\.bak$',
        r'.+\.cfml?$',
        r'.+\.cgi$',
    ]
