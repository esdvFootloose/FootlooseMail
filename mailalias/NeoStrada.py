import requests
from bs4 import BeautifulSoup
from FootlooseMail.secret import cpanel_username, cpanel_password
from django.core.cache import caches
from .cpanelendpoints import *
import logging
import json
import dill as pickle

logger = logging.getLogger(__name__)

def Login():
    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]
    default = caches["default"]

    aliasusers.clear()
    useraliasses.clear()

    default.set('cpanelsession', None)
    default.set('security_token', None)

    session = requests.session()
    session.verify = False
    r = session.post(cpanelurl + "login/?login_only=1", data={
        "user": cpanel_username,
        "pass": cpanel_password,
    })

    if r.status_code == 401:
        logger.error("Invalid cpanel credentials!")
        return

    # manual cookie extraction fix, because somehow this goes wrong automatically
    for cookie in r.headers['Set-Cookie'].split(';'):
        if 'cpsession' in cookie:
            session.cookies['cpsession'] = cookie.split('=')[1]
            break

    loginresponse = json.loads(r.text)
    security_token = loginresponse['security_token']

    default.set('cpanelsession', pickle.dumps(session), 30*60)
    default.set('security_token', security_token, 30*60)

def FetchData():
    aliasusers = caches["aliasusers"]
    useraliasses = caches["useraliasses"]
    default = caches["default"]

    session = default.get('cpanelsession')
    security_token = default.get('security_token')

    if session is None or security_token is None:
        Login()
        session = pickle.loads(default.get('cpanelsession'))
        security_token = default.get('security_token')
    else:
        session = pickle.loads(session)

    r = session.get(cpanelurl + security_token + mailpanel)
    #TODO: communicate this to the user somehow
    #TODO: maybe try relogin after failure?
    if r.status_code != 200:
        logger.error("Could not retrieve mail list: {}".format(r.status_code))
        return

    listsoup = BeautifulSoup(r.text, "lxml")

    aliasestotal = set(aliasusers.get('keys', []))
    userstotal = set(useraliasses.get('keys', []))
    for row in listsoup.find_all("tr"):
        tr = []
        for cell in row.findChildren("td"):
            if '@' in cell.getText():
                tr.append(cell.getText().replace('\n', '').replace(' ', ''))

        if len(tr) == 0:
            continue

        users = aliasusers.get(tr[0], [])
        aliases = useraliasses.get(tr[1], [])

        users.append(tr[1])
        aliases.append(tr[0])

        aliasusers.set(tr[0], users)
        useraliasses.set(tr[1], aliases)

        aliasestotal.add(tr[0])
        userstotal.add(tr[1])

    aliasusers.set('keys', list(aliasestotal))
    useraliasses.set('keys', list(userstotal))

def AddToAlias(email, alias, refetchafter=True):
    aliasusers = caches["aliasusers"]
    default = caches["default"]

    if email in aliasusers.get(alias, []):
        return 200

    session = default.get('cpanelsession')
    security_token = default.get('security_token')

    if session is None or security_token is None:
        Login()
        session = pickle.loads(default.get('cpanelsession'))
        security_token = default.get('security_token')
    else:
        session = pickle.loads(session)

    if '@' in alias:
        alias = alias.split('@')[0]
    r = session.post(cpanelurl + security_token + addemail, data={
        "email": alias,
        "domain": "esdvfootloose.nl",
        "fwdopt": "fwd",
        "fwdemail": email,
        "failmsgs": "Deze persoon is niet bekend op dit adres.",
        "fwdsystem": cpanel_username,
        "pipefwd": "",
    })

    if r.status_code == 200 and refetchafter:
        FetchData()
    return r.status_code


def RemoveFromAlias(email, alias, refetchafter=True):
    aliasusers = caches["aliasusers"]
    default = caches["default"]

    if email not in aliasusers.get(alias, []):
        return -1

    session = default.get('cpanelsession')
    security_token = default.get('security_token')

    if session is None or security_token is None:
        Login()
        session = pickle.loads(default.get('cpanelsession'))
        security_token = default.get('security_token')
    else:
        session = pickle.loads(session)

    if '@' in alias:
        alias = alias.split('@')[0]
    r = session.get(cpanelurl + security_token + deletemail.format(alias, email))
    if r.status_code == 200 and refetchafter:
        FetchData()
    return r.status_code