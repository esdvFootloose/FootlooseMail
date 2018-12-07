import requests
import json
from bs4 import BeautifulSoup
from time import sleep
from celery import group
from mailalias.tasks import task_scrape_members_group

class TransipApi:

    LOGINURL = "https://www.transip.nl/cp/"
    LOGINURL_AJAX = "https://www.transip.nl/session/ajaxlogin/"
    MAILGROUPURL = "https://www.transip.nl/cp/domein-hosting/hosting/email-list/overzicht/prm/200141253/esdvfootloose.nl/"
    ID = "200141253"
    MAILGROUPLISTURL = "https://www.transip.nl/cp/domein-hosting/hosting/email-list/wijzigen/prm/{id}/{listid}/"
    MAILGROUPLISTCREATE = "https://www.transip.nl/cp/domein-hosting/services/webhosting/maillist/create/"
    MAILGROUPLISTEDIT = "https://www.transip.nl/cp/domein-hosting/services/webhosting/maillist/update/"
    MAILGROUPLISTCREATEFORM = "https://www.transip.nl/cp/domein-hosting/hosting/email-list/wijzigen/prm/200141253/esdvfootloose.nl/"
    MAILGROUPLISTDELETE = "https://www.transip.nl/cp/domein-hosting/services/webhosting/maillist/delete/"

    def __init__(self):
        self.session = requests.session()
        self.session.headers['User-Agent'] = "esdv Footloose Mail Alias System"
        self.session.headers['From'] = "ict@esdvfootloose.nl"
        self.logged_in = False
        self.groups = {}
        self.failure_reason = ""

    def login(self, username, password):
        rlogin = self.session.get(self.LOGINURL)
        souplogin = BeautifulSoup(rlogin.text, 'lxml')

        csrf = souplogin.find('form', {'action' : "/session/ajaxlogin/"}).find('input', {'name':'_csrf_token'}).get('value')
        r_ajax_login = self.session.post(self.LOGINURL_AJAX, data={
            '_csrf_token' : csrf,
            'username' : username,
            'password' : password,
            'shouldReload' : 'true',
        })

        r_ajax_login_json = json.loads(r_ajax_login.text)
        self.logged_in = r_ajax_login_json['success']
        if not self.logged_in:
            self.failure_reason = r_ajax_login_json['reason']

        return self.logged_in


    def fetch_data(self):
        if not self.logged_in:
            return None

        r_mailgroup = self.session.get(self.MAILGROUPURL)
        soup_mailgroup = BeautifulSoup(r_mailgroup.text, 'lxml')
        soup_groups = soup_mailgroup.find('table').find_all('tr')
        self.groups = {}
        tasks = []
        for row in soup_groups:
            if 'td' in str(row):
                cells = row.find_all('td')
                mail_group = {
                    'name' : cells[0].text.replace(' ','').replace('\n','').split('@')[0],
                    'email' : cells[1].text.replace(' ','').replace('\n',''),
                    'count' : int(cells[2].text.replace(' ','').replace('\n','')),
                    'listid' : cells[3].find('input', {'type':'hidden', 'name' : 'mailListId'}).get('value'),
                }
                tasks.append(task_scrape_members_group.s(self, mail_group))
        job = group(tasks)
        result = job.apply_async()
        result.join()
        for mail_group in result.get():
            self.groups[mail_group['name']] = mail_group

        return self.groups

    def _fetch_single_group(self, name, members):
        if not self.logged_in:
            return None

        r_mailgroup = self.session.get(self.MAILGROUPURL)
        soup_mailgroup = BeautifulSoup(r_mailgroup.text, 'lxml')
        soup_groups = soup_mailgroup.find('table').find_all('tr')
        for row in soup_groups:
            if 'td' in str(row):
                cells = row.find_all('td')
                if cells[0].text.replace(' ', '').replace('\n', '') == name:
                    group = {
                        'name': cells[0].text.replace(' ', '').replace('\n', '').split('@')[0],
                        'email': cells[1].text.replace(' ', '').replace('\n', ''),
                        'count': int(cells[2].text.replace(' ', '').replace('\n', '')),
                        'members' : members,
                        'listid': cells[3].find('input', {'type': 'hidden', 'name': 'mailListId'}).get('value'),
                    }
                    self.groups[name] = group
                    return group

        return None

    def _get_csrf_alias_form(self):
        r_mailgroup_createform = self.session.get(self.MAILGROUPLISTCREATEFORM)
        soup_mailgroup_createform = BeautifulSoup(r_mailgroup_createform.text, 'lxml')
        return soup_mailgroup_createform.find('input',
                                              {'id': 'request-token', 'class': 'request-token', 'type': 'hidden'}).get(
            'value')

    def add_to_alias(self, alias, emails, overwrite=True, refetch=False):
        if self.groups == {} or not self.logged_in:
            return False

        data = {
            'address[]': emails,
            'id': self.ID,
            'item-id[]': self.ID,
            'item-name[]': 'esdvfootloose.nl',
            'mainAddress': alias,
            'name': alias,
        }
        csrf = self._get_csrf_alias_form()


        if alias in self.groups:
            if not overwrite:
                data['address[]'] = list(set(emails) | set(self.groups[alias]['members']))
            data['address[]'].append("")

            data['item-name[]'] = self.ID
            data['mailListId'] = self.groups[alias]['listid']
            r_mailgroup_edit = self.session.post(self.MAILGROUPLISTEDIT, data=data, headers={
                'X-CSRFToken' : csrf
            })
            try:
                r_mailgroup_json = json.loads(r_mailgroup_edit.text)
            except:
                self.failure_reason = r_mailgroup_edit.text
                return False

        else:
            r_mailgroup_create = self.session.post(self.MAILGROUPLISTCREATE, data=data, headers={
                'X-CSRFToken' : csrf
            })
            try:
                r_mailgroup_json = json.loads(r_mailgroup_create.text)
            except:
                self.failure_reason = r_mailgroup_create.text
                return False

        if r_mailgroup_json['success']:
            if not refetch:
                self._fetch_single_group(alias, emails)
            else:
                self.fetch_data()
            return True
        self.failure_reason = r_mailgroup_json['reason']
        return False

    def delete_alias(self, alias, refetch=False):
        if self.groups == {} or not self.logged_in:
            return False

        csrf = self._get_csrf_alias_form()
        data = {
            'id' : self.ID,
            'item-id[]' : self.ID,
            'item-name[]' : 'esdvfootloose.nl',
            'mailListId' : self.groups[alias]['listid']
        }

        r_mailgroup_delete = self.session.post(self.MAILGROUPLISTDELETE, data=data, headers={
            'X-CSRFToken': csrf
        })
        try:
            r_mailgroup_delete_json = json.loads(r_mailgroup_delete.text)
        except:
            self.failure_reason = r_mailgroup_delete.text
            return False

        if r_mailgroup_delete_json['success']:
            if refetch:
                self.fetch_data()
            else:
                del self.groups[alias]
            return True
        self.failure_reason = r_mailgroup_delete_json['reason']
        return False

    def diversion(self):
        self.session.get(self.MAILGROUPURL)
        sleep(12)
