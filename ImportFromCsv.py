if __name__ == '__main__':
    import django
    import argparse
    import sys
    import os
    import csv

    parser = argparse.ArgumentParser(description="Load members from csv")
    parser.add_argument('--mode', nargs='?', const=1, type=str, default='debug', help='debug/production')

    MODE = parser.parse_args().mode

    if MODE not in ["debug", "production"]:
        sys.exit(1)
    if MODE == 'debug':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'FootlooseMail.settings_development'
    elif MODE == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'FootlooseMail.settings'

    django.setup()
    from mailmember.models import MailMember
    from dateutil import parser

    choice = input("This will delete all existing mailmembers, do you want to continue? (y|n)")
    if choice != 'y':
        sys.exit(0)

    MailMember.objects.all().delete()
    
    with open('footlooseusers.csv', 'r') as stream:
        l = stream.readlines()[1:]

    for i, usercsv in enumerate(csv.reader(l, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)):
        # usercsv = usercsv.strip().split(',')

        if 'betaald-lid' not in usercsv[22] and usercsv[21] == '':
            print("[{}/{}]: None".format(i, len(l)))
            continue

        user = MailMember()

        user.Email = usercsv[3]
        user.Registration = parser.parse(usercsv[5], ignoretz=True)
        user.FirstName = usercsv[8]
        user.LastName = usercsv[9]
        user.BirthDay = parser.parse(usercsv[10], ignoretz=True).date()
        if 'english' in usercsv[12].lower():
            user.Language = 1
        elif 'dutch' in usercsv[12].lower():
            user.Language = 0
        user.Study = usercsv[13]
        if 'yes' in usercsv[15].lower():
            user.BunkerAccess = True
        else:
            user.BunkerAccess = False
        user.Institute = usercsv[16].split('|')[-1]
        if 'yes' in usercsv[17].lower():
            user.Student = True
        else:
            user.Student = False
        user.City = usercsv[18]
        user.PostalCode = usercsv[19]
        user.Address = usercsv[20]
        if 'female' in usercsv[21].lower() or 'vrouw' in usercsv[21].lower():
            user.Gender = 1
        elif 'male' in usercsv[21].lower() or 'man' in usercsv[21].lower():
            user.Gender = 0

        user.save()

        print("[{}/{}]: {}".format(i, len(l), user))