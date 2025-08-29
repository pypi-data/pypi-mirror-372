import datetime
import os

from unittest.mock import patch

import httpretty

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from django.test import TestCase
from django.contrib.auth import get_user_model

from sortinghat.core import api
from sortinghat.core.context import SortingHatContext
from sortinghat.core.models import Individual, MAX_PERIOD_DATE, MIN_PERIOD_DATE

from sortinghat.core.importer.backends.eclipse import EclipseFoundationAccountsImporter


ECLIPSE_API_URL = "https://api.eclipse.org"
ECLIPSE_ACCOUNTS_URL = "https://accounts.eclipse.org/account/updated"
OAUTH_TOKEN_ENDPOINT = "https://accounts.eclipse.org/oauth2/token"


MOCK_DATETIME_NOW = datetime.datetime(2025, 1, 1, tzinfo=tzutc())


def read_file(filename, mode='r'):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), mode) as f:
        content = f.read()
    return content


def setup_mock_server():
    """Configure a Mock server"""

    def request_callback(request, uri, headers):
        since = int(request.querystring.get('since', 0)[0])

        if since > 4000000000:
            body = bodies[2]
            requests.append(httpretty.last_request())
            return [200, headers, body]

        page = int(request.querystring.get('page', [1])[0])
        body = bodies[page - 1]
        requests.append(httpretty.last_request())
        return [200, headers, body]

    requests = []

    # Accounts pages
    accounts_url = ECLIPSE_ACCOUNTS_URL
    bodies = [
        read_file('data/eclipse_accounts_page_1.json'),
        read_file('data/eclipse_accounts_page_2.json'),
        read_file('data/eclipse_accounts_page_3.json'),
    ]

    httpretty.register_uri(httpretty.GET,
                           accounts_url,
                           responses=[
                               httpretty.Response(body=request_callback)
                               for _ in bodies
                           ])

    # John Smith profile pages
    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_API_URL + "/account/profile/jsmith",
                           body=read_file('data/eclipse_jsmith.json'))
    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_API_URL + "/account/profile/jsmith/employment-history",
                           body=read_file('data/eclipse_jsmith_employment.json'))

    # John Doe profile pages
    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_API_URL + "/account/profile/jdoe",
                           body=read_file('data/eclipse_jdoe.json'))
    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_API_URL + "/account/profile/jdoe/employment-history",
                           body=read_file('data/eclipse_jdoe_employment.json'))

    # Jane Rae profile pages
    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_API_URL + "/account/profile/jrae",
                           body=read_file('data/eclipse_jrae.json'))
    httpretty.register_uri(httpretty.GET,
                           ECLIPSE_API_URL + "/account/profile/jrae/employment-history",
                           body=read_file('data/eclipse_jrae_employment.json'))

    return requests, bodies


class TestEclipseImporter(TestCase):
    """EclipseImporter tests"""

    def setUp(self):
        """Initialize variables"""

        self.user = get_user_model().objects.create(username='test')
        self.ctx = SortingHatContext(self.user)

    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_initialization(self, mock_datetime_now):
        """Test whether attributes are initialized"""

        url = "https://test-url.com/"

        importer = EclipseFoundationAccountsImporter(
            ctx=self.ctx,
            url=url
        )

        self.assertEqual(importer.url, url)
        self.assertEqual(importer.ctx, self.ctx)
        self.assertEqual(importer.NAME, "EclipseFoundation")

        # 'from_date' is 1 year before the current date (MOCK_DATETIME_NOW)
        self.assertEqual(importer.from_date, mock_datetime_now.return_value - relativedelta(years=1))

    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_parse_from_date(self, mock_datetime_now):
        """Check if from_date parameter is parsed correctly"""

        # Check from_date is parsed correctly
        importer = EclipseFoundationAccountsImporter(
            ctx=self.ctx,
            url="https://test-url.com/",
            from_date="2025-12-01"
        )
        self.assertEqual(importer.from_date, datetime.datetime(year=2025,
                                                               month=12,
                                                               day=1,
                                                               tzinfo=tzutc()))

    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_from_date_older_than_one_year(self, mock_datetime_now):
        """Check if an error is raised when the from_date is invalid"""

        with self.assertRaises(ValueError):
            _ = EclipseFoundationAccountsImporter(
                ctx=self.ctx,
                url="https://test-url.com/",
                from_date="2000-01-01"
            )

    def test_backend_name(self):
        """Test whether the NAME of the backend is right"""

        self.assertEqual(EclipseFoundationAccountsImporter.NAME, "EclipseFoundation")

    @httpretty.activate
    @patch('sortinghat.core.importer.backends.eclipse.EclipseFoundationAPIClient.login', return_value="mocked_login")
    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_import_identities(self, mock_login, mock_datetime_now):

        # Set up a mock HTTP server
        requests, bodies = setup_mock_server()

        importer = EclipseFoundationAccountsImporter(ctx=self.ctx, url=None, from_date=None)
        n = importer.import_identities()

        # In total, 3 individuals and 5 identities were created.
        # The individuals 'jsmith' and 'jrae' have eclipse and github
        # identities, while 'jdoe' only has one eclipse identity.
        self.assertEqual(n, 5)

        individuals = Individual.objects.order_by('mk').all()

        self.assertEqual(len(individuals), 3)

        # John Doe
        jdoe = individuals[0]
        self.assertEqual(jdoe.profile.name, 'John Doe')
        self.assertEqual(jdoe.profile.email, 'jdoe@example.com')

        ids = jdoe.identities.order_by('uuid').all()

        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0].name, 'John Doe')
        self.assertEqual(ids[0].email, 'jdoe@example.com')
        self.assertEqual(ids[0].username, 'jdoe')
        self.assertEqual(ids[0].source, 'eclipsefdn')

        # John Smith
        jsmith = individuals[1]
        self.assertEqual(jsmith.profile.name, 'John Smith')
        self.assertEqual(jsmith.profile.email, 'jsmith@example.com')

        ids = jsmith.identities.order_by('uuid').all()

        self.assertEqual(len(ids), 2)
        self.assertEqual(ids[0].name, 'John Smith')
        self.assertEqual(ids[0].email, 'jsmith@example.com')
        self.assertEqual(ids[0].username, 'jsmith')
        self.assertEqual(ids[0].source, 'github')

        self.assertEqual(ids[1].name, 'John Smith')
        self.assertEqual(ids[1].email, 'jsmith@example.com')
        self.assertEqual(ids[1].username, 'jsmith')
        self.assertEqual(ids[1].source, 'eclipsefdn')

        # Jane Rae
        jrae = individuals[2]
        self.assertEqual(jrae.profile.name, 'Jane Rae')
        self.assertEqual(jrae.profile.email, 'jrae@example.com')

        ids = jrae.identities.order_by('uuid').all()

        self.assertEqual(len(ids), 2)
        self.assertEqual(ids[0].name, 'Jane Rae')
        self.assertEqual(ids[0].email, 'jrae@example.com')
        self.assertEqual(ids[0].username, 'jrae')
        self.assertEqual(ids[0].source, 'eclipsefdn')

        self.assertEqual(ids[1].name, 'Jane Rae')
        self.assertEqual(ids[1].email, 'jrae@example.com')
        self.assertEqual(ids[1].username, 'jrae')
        self.assertEqual(ids[1].source, 'github')

    @httpretty.activate
    @patch('sortinghat.core.importer.backends.eclipse.EclipseFoundationAPIClient.login', return_value="mocked_login")
    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_import_no_identities(self, mock_login, mock_datetime_now):
        # Set up a mock HTTP server
        requests, bodies = setup_mock_server()

        importer = EclipseFoundationAccountsImporter(
            ctx=self.ctx,
            url=None,
            from_date="2100-1-1"
        )

        n = importer.import_identities()

        # No identities
        self.assertEqual(n, 0)

    @httpretty.activate
    @patch('sortinghat.core.importer.backends.eclipse.EclipseFoundationAPIClient.login', return_value="mocked_login")
    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_import_merge_identities(self, mock_login, mock_datetime_now):

        # Add individuals that share email and github handle
        api.add_identity(self.ctx, source='github', username='jsmith')
        api.add_identity(self.ctx, source='git', email='jsmith@example.com')
        api.add_identity(self.ctx, source='jira', username='jrae')

        # Set up a mock HTTP server
        setup_mock_server()

        importer = EclipseFoundationAccountsImporter(ctx=self.ctx, url=None)

        n = importer.import_identities()
        self.assertEqual(n, 5)

        individuals = Individual.objects.order_by('mk').all()
        self.assertEqual(len(individuals), 4)

    @httpretty.activate
    @patch('sortinghat.core.importer.backends.eclipse.EclipseFoundationAPIClient.login', return_value="mocked_login")
    @patch('sortinghat.core.importer.backends.eclipse.datetime_utcnow', return_value=MOCK_DATETIME_NOW)
    def test_import_enrollments(self, mock_login, mock_datetime_now):

        # Set up a mock HTTP server
        setup_mock_server()

        importer = EclipseFoundationAccountsImporter(ctx=self.ctx, url=None)
        importer.import_identities()

        individuals = Individual.objects.order_by('mk').all()

        self.assertEqual(len(individuals), 3)

        # John Doe
        # This individual doesn't have enrollments in the endpoint
        # but the affiliation is taken from his profile endpoint.
        jdoe = individuals[0]
        self.assertEqual(jdoe.profile.name, 'John Doe')

        enrollments = jdoe.enrollments.all()
        self.assertEqual(len(enrollments), 1)

        rol = enrollments[0]
        self.assertEqual(rol.group.name, "Example")
        self.assertEqual(rol.start, MIN_PERIOD_DATE)
        self.assertEqual(rol.end, MAX_PERIOD_DATE)

        # John Smith
        jsmith = individuals[1]
        self.assertEqual(jsmith.profile.name, 'John Smith')

        enrollments = jsmith.enrollments.all()
        self.assertEqual(len(enrollments), 2)

        rol = enrollments[0]
        self.assertEqual(rol.group.name, "ACME")
        self.assertEqual(rol.start, datetime.datetime(2001, 1, 1, tzinfo=tzutc()))
        self.assertEqual(rol.end, datetime.datetime(2025, 8, 7, tzinfo=tzutc()))

        rol = enrollments[1]
        self.assertEqual(rol.group.name, "Example")
        self.assertEqual(rol.start, datetime.datetime(2025, 8, 7, tzinfo=tzutc()))
        self.assertEqual(rol.end, MAX_PERIOD_DATE)

        # Jane Rae
        jsmith = individuals[2]
        self.assertEqual(jsmith.profile.name, 'Jane Rae')

        enrollments = jsmith.enrollments.all()
        self.assertEqual(len(enrollments), 1)

        rol = enrollments[0]
        self.assertEqual(rol.group.name, "ACME")
        self.assertEqual(rol.start, datetime.datetime(2010, 1, 1, tzinfo=tzutc()))
        self.assertEqual(rol.end, MAX_PERIOD_DATE)
