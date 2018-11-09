from __future__ import absolute_import
from FootlooseMail.celery import app
from bs4 import BeautifulSoup

@app.task
def task_scrape_members_group(api, group):
    r_mailgrouplist = api.session.get(api.MAILGROUPLISTURL.format(id=api.ID, listid=group['listid']))
    soup_mailgrouplist = BeautifulSoup(r_mailgrouplist.text, 'lxml')
    group['members'] = [x.get('value') for x in soup_mailgrouplist.find_all('input', {'id': 'add-address'}) if
                        x.get('value') != '']
    return group