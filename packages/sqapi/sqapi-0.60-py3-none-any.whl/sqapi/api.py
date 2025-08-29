import json
from getpass import getpass

# import requests
from time import sleep
from tqdm import tqdm

from sqapi.request import DEFAULT_HOST, SQAPIException, Get, Export, Post, Patch, SaveFile, query_filter


class SQAPI:
    def __init__(self, host=DEFAULT_HOST, api_key=None, verbosity=2, noauth=False):
        self.host = host or DEFAULT_HOST
        self.api_key = api_key
        self.verbosity = verbosity
        # self.session = requests
        self.current_user = None
        # self.session.headers.update({"X-auth-token": self.api_key})

        # Get current user info and login session using API key
        if not noauth:
            if self.api_key:
                self.connect(self.host, api_key)
            else:
                username = input(f"Enter the username that you want to use for '{self.host}': ")
                password = getpass()
                print("NOTE: to avoid this login prompt, instantiate with an api_key.")
                self.login(self.host, username, password)

    def login(self, host, username, password, *args, **keargs):
        self.host = host or self.host
        r = self.post("/api/users/login", data=json.dumps(dict(username=username, password=password))).execute()
        if r.ok:
            login_response = r.json()
            if login_response.get("api_token") is None:
                raise SQAPIException(f"Your API token does not appear to be set. You may need to login to the SQ+ "
                                     f"instance at {host} to activate it.")
            self.connect(host=host, api_key=login_response.get("api_token"))

    def connect(self, host=None, api_key=None, *args, **kwargs):
        self.host = host or self.host
        self.api_key = api_key or self.api_key
        self.current_user = self.get(
            "/api/users/login", headers={"X-auth-token": self.api_key}
        ).execute(verbosity=0).json()

    def status(self):
        return dict(
            host=self.host,
            current_user=self.current_user,
            verbosity=self.verbosity
        )

    def get(self, endpoint, poll_status_interval=None, *args, **kwargs) -> Get:
        result = Get(endpoint, sqapi=self, *args, poll_status_interval=poll_status_interval, **kwargs)
        # result = self.poll_task_status(result, poll_status_interval=poll_status_interval)
        return result

    def export(self, endpoint, include_columns=None, poll_status_interval=1.0, *args, **kwargs):
        result = Export(endpoint, sqapi=self, page=None, poll_status_interval=poll_status_interval, results_per_page=None, include_columns=include_columns, *args, **kwargs)
        # result = self.poll_task_status(result, poll_status_interval=poll_status_interval)
        return result

    def post(self, endpoint, data=None, json_data=None, **kwargs) -> Post:
        return Post(endpoint, sqapi=self, data=data, json_data=json_data, **kwargs)

    def patch(self, endpoint, data=None, json_data=None, **kwargs) -> Patch:
        return Patch(endpoint, sqapi=self, data=data, json_data=json_data, **kwargs)

    def upload_file(self, endpoint, file_path, data=None, **kwargs) -> Post:
        files = {'file': (file_path, open(file_path, 'rb'), 'text/x-spam')}
        return Post(endpoint, sqapi=self, files=files, data=data, headers=None, **kwargs)

    def save_file(self, endpoint, id=None, include_columns=None, fileops=None, save=None, **kwargs) -> SaveFile:
        return SaveFile(endpoint, sqapi=self, id=id, include_columns=include_columns, fileops=fileops, save=save, **kwargs)

    def api_ref_link(self, resource, title='{resource} API reference'):
        return (f"<a href='{self.host}/api/help?template=api_help_page.html#{resource}' target='api_reference'>"
                f"{title.format(resource=resource)}"
                f"</a>")

    def send_user_email(self, subject, message, email_addresses=None, user_ids=None, usernames=None):
        r0 = self.get("/api/users")
        or_filts = []
        if isinstance(email_addresses, list):
            or_filts.append(query_filter("email","in",email_addresses))
        if isinstance(user_ids, list):
            or_filts.append(query_filter("id", "in", user_ids))
        if isinstance(usernames, list):
            or_filts.append(query_filter("usernames", "in", usernames))

        users = r0.filters_or(or_filts).execute().json()

        for u in users.get("objects"):
            if u is not None:
                r = self.post(f"/api/users/{u.get('id')}/email", json_data=dict(subject=subject, message=message))
                r.execute(icon_ok="📩")
