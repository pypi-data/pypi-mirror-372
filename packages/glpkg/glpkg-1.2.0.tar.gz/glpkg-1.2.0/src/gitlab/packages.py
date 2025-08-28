from http.client import HTTPMessage
import json
import logging
import os
from urllib import request, parse

logger = logging.getLogger(__name__)


class Packages:
    def __init__(self, host: str, token_type: str, token: str):
        self.host = host
        self.token_type = token_type
        self.token = token

    def api_url(self) -> str:
        return "https://{}/api/v4/".format(parse.quote(self.host))

    def project_api_url(self, project: str) -> str:
        return self.api_url() + "projects/{}/".format(parse.quote_plus(project))

    def get_headers(self) -> dict:
        headers = {}
        if self.token_type and self.token:
            headers = {self.token_type: self.token}
        return headers

    def _request(self, url: str) -> tuple[int, bytes, HTTPMessage]:
        logger.debug("Requesting " + url)
        req = request.Request(url, headers=self.get_headers())
        with request.urlopen(req) as response:
            return response.status, response.read(), response.headers

    def _get_next_page(self, headers: HTTPMessage) -> int:
        ret = 0
        if headers:
            next_page = headers.get("x-next-page")
            if next_page:
                ret = int(next_page)
                logger.debug("Response incomplete, next page is " + next_page)
            else:
                logger.debug("Response complete")
        return ret

    def _build_query(self, arg: str, page: int) -> str:
        query = ""
        if arg or page:
            if page:
                page = "page=" + str(page)
            query = "?{}".format("&".join(filter(None, (arg, page))))
        return query

    def gl_project_api(self, project: str, path: str, arg: str = None) -> list:
        data = []
        more = True
        page = None
        while more:
            more = False
            query = self._build_query(arg, page)
            url = self.project_api_url(project) + path + query
            status, res_data, headers = self._request(url)
            logger.debug("Response status: " + str(status))
            res_data = json.loads(res_data)
            logger.debug("Response data: " + str(res_data))
            data = data + res_data
            page = self._get_next_page(headers)
            if page:
                more = True
        return data

    def list_packages(self, project: str, package_name: str) -> list:
        packages = []
        logger.debug("Listing packages with name " + package_name)
        data = self.gl_project_api(
            project, "packages", "package_name=" + parse.quote_plus(package_name)
        )
        for package in data:
            name = parse.unquote(package["name"])
            version = parse.unquote(package["version"])
            # GitLab API returns packages that have some match to the filter;
            # let's filter out non-exact matches
            if package_name != name:
                continue
            packages.append({"name": name, "version": version})
        return packages

    def list_files(self, project: str, package_id: int) -> list:
        files = []
        logger.debug("Listing package " + str(package_id) + " files")
        path = "packages/" + parse.quote_plus(str(package_id)) + "/package_files"
        data = self.gl_project_api(project, path)
        for package in data:
            # Only append the filename once to the list of files
            # as there's no way to download them separately through
            # the API
            filename = parse.unquote(package["file_name"])
            if filename not in files:
                files.append(filename)
        return files

    def get_package_id(
        self, project: str, package_name: str, package_version: str
    ) -> int:
        id = 0
        logger.debug(
            "Fetching package " + package_name + " (" + package_version + ") ID"
        )
        path = "packages"
        arg = (
            "package_name="
            + parse.quote_plus(package_name)
            + "&package_version="
            + parse.quote_plus(package_version)
        )
        data = self.gl_project_api(project, path, arg)
        if len(data) == 1:
            package = data.pop()
            id = package["id"]
        return id

    def download_file(
        self,
        project: str,
        package_name: str,
        package_version: str,
        filename: str,
        destination: str = "",
    ) -> int:
        ret = 1
        logger.debug("Downloading file " + filename)
        url = (
            self.project_api_url(project)
            + "packages/generic/"
            + parse.quote_plus(package_name)
            + "/"
            + parse.quote_plus(package_version)
            + "/"
            + parse.quote(filename)
        )
        status, data, _ = self._request(url)
        if status == 200:
            path = os.path.join(destination, filename)
            parent = os.path.dirname(path)
            if parent:
                # Create missing directories if needed
                # In case path has no parent, current
                # workind directory is used
                os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as file:
                file.write(data)
                ret = 0
        return ret

    def upload_file(
        self, project: str, package_name: str, package_version: str, file: str
    ) -> int:
        ret = 1
        logger.debug("Uploading file " + file)
        with open(str(file), "rb") as data:
            url = (
                self.project_api_url(project)
                + "packages/generic/"
                + parse.quote_plus(package_name)
                + "/"
                + parse.quote_plus(package_version)
                + "/"
                + parse.quote(str(file))
            )
            res = request.urlopen(
                request.Request(
                    url, method="PUT", data=data, headers=self.get_headers()
                )
            )
            if res.status == 201:  # 201 is created
                ret = 0
        return ret
